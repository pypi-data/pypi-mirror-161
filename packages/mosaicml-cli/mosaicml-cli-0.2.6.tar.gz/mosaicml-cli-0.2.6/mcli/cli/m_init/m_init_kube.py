""" mcli init_kube Entrypoint """
import argparse
import logging
import re
import textwrap
import webbrowser
from typing import Dict, List, NamedTuple, Optional

from mcli.cli.m_create.platform import PlatformCreator, PlatformValidationError, create_one_platform
from mcli.config import MCLI_KUBECONFIG, MESSAGE, MCLIConfigError
from mcli.utils.utils_interactive import ValidationError, secret_prompt, simple_prompt
from mcli.utils.utils_logging import FAIL, OK, console
from mcli.utils.utils_rancher import (ProjectInfo, configure_namespaces, generate_cluster_config, retrieve_clusters,
                                      retrieve_projects)
from mcli.utils.utils_string_validation import validate_rfc1123_name

RANCHER_ENDPOINT_PATTERN = 'https://rancher.z[0-9]+.r[0-9]+.mosaicml.cloud'
LEGACY_RANCHER_ENDPOINT = 'https://mosaicml-rancher.westus2.cloudapp.azure.com'
DEEP_LINKS = {
    'DEFAULT': 'dashboard/account/create-key',
    'https://mosaicml-rancher.westus2.cloudapp.azure.com': 'apikeys'
}

logger = logging.getLogger(__name__)


def bold(text: str) -> str:
    return f'[bold green]{text}[/]'


def validate_rancher_endpoint(endpoint: str) -> bool:
    if re.match(RANCHER_ENDPOINT_PATTERN.replace('.', r'\.'), endpoint):
        return True
    if endpoint == LEGACY_RANCHER_ENDPOINT:
        return True
    raise RuntimeError(f'Invalid MosaicML Cloud endpoint: {endpoint}. Should be of the form: '
                       f'{RANCHER_ENDPOINT_PATTERN}')


class RancherDetails(NamedTuple):
    endpoint: str
    auth_token: str
    namespace: str


def validate_auth_token(text: str) -> bool:
    if not text.startswith('token'):
        raise ValidationError('Bearer token should start with "token"')
    return True


def validate_namespace(text: str) -> bool:
    validated = validate_rfc1123_name(text)
    if not validated:
        raise ValidationError(validated.message)
    return True


def validate_number(text: str) -> bool:
    if not text.isnumeric():
        raise ValidationError(f'Zone must be a number. Got: {text}')
    return True


def fill_rancher_values(
    auth_token: Optional[str] = None,
    rancher_endpoint: Optional[str] = None,
    namespace: Optional[str] = None,
) -> RancherDetails:
    if not rancher_endpoint:
        zone = simple_prompt(
            'Which MosaicML Cloud "zone" would you like to access?',
            validate=validate_number,
        )
        rancher_endpoint = f'https://rancher.z{zone}.r0.mosaicml.cloud'

    assert rancher_endpoint is not None

    # Get required info
    if not auth_token:
        path = DEEP_LINKS.get(rancher_endpoint, None) or DEEP_LINKS['DEFAULT']
        url = f'{rancher_endpoint}/{path}'
        logger.info(
            f'\n\nTo communicate with the MosaicML Cloud we\'ll need your API key (also called the "{bold("Bearer Token")}"). '
            'Your browser should have opened to the API key creation screen. Login, if necessary, then, create a '
            f'key with "{bold("no scope")}" that expires "{bold("A day from now")}" and copy the '
            f'"{bold("Bearer Token")}" for this next step. If your browser did not open, please use this link:'
            f'\n\n[blue]{url}[/]\n\n'
            'If upon login you do not see the API key creation screen, either try the link above in Google Chrome or '
            f'select "{bold("Accounts & API Keys")}" from the top-right user menu, followed by '
            f'"{bold("Create API Key")}" and the directions above.')
        webbrowser.open_new_tab(url)

        auth_token = secret_prompt('What is your "bearer token"?', validate=validate_auth_token)

    assert auth_token is not None

    if not namespace:
        namespace = simple_prompt(
            'What should your namespace be? (Should only contain lower-case letters, numbers, or "-", e.g. "janedoe")',
            validate=validate_namespace)

    assert namespace is not None

    return RancherDetails(endpoint=rancher_endpoint, auth_token=auth_token, namespace=namespace)


def initialize_k8s(
    auth_token: Optional[str] = None,
    rancher_endpoint: Optional[str] = None,
    namespace: Optional[str] = None,
    **kwargs,
) -> int:
    del kwargs

    try:
        if rancher_endpoint:
            # Ensure no trailing '/'.
            rancher_endpoint = rancher_endpoint.rstrip('/')
            validate_rancher_endpoint(rancher_endpoint)

        if namespace:
            result = validate_rfc1123_name(namespace)
            if not result:
                raise RuntimeError(result.message)

        details = fill_rancher_values(auth_token=auth_token, rancher_endpoint=rancher_endpoint, namespace=namespace)
        rancher_endpoint, auth_token, namespace = details

        # Retrieve all available clusters
        with console.status('Retrieving clusters...'):
            clusters = retrieve_clusters(rancher_endpoint, auth_token)
        if clusters:
            logger.info(f'{OK} Found {len(clusters)} clusters that you have access to')
        else:
            logger.error(f'{FAIL} No clusters found. Please double-check that you have access to clusters in '
                         'the MosaicML Cloud')
            return 1

        # Setup namespace
        with console.status('Getting available projects...'):
            projects = retrieve_projects(rancher_endpoint, auth_token)

        # Get unique projects
        cluster_project_map: Dict[str, List[ProjectInfo]] = {}
        for project in projects:
            cluster_project_map.setdefault(project.cluster, []).append(project)
        unique_projects: List[ProjectInfo] = []
        for cluster_id, project_list in cluster_project_map.items():
            chosen = project_list[0]
            unique_projects.append(chosen)
            if len(project_list) > 1:
                cluster_name = {cluster.id: cluster.name for cluster in clusters}.get(cluster_id)
                assert cluster_name is not None
                logger.warning(
                    f'Found {len(project_list)} projects for cluster {bold(cluster_name)}. '
                    f'Creating namespace in the first one: {chosen.display_name}. If you need to use a different '
                    'project, please move the namespace in Rancher.')

        with console.status(f'Setting up namespace {namespace}...'):
            configure_namespaces(rancher_endpoint, auth_token, unique_projects, namespace)
        logger.info(f'{OK} Configured namespace {namespace} in {len(clusters)} available clusters')

        # Generate kubeconfig file from clusters
        with console.status('Generating custom kubeconfig file...'):
            generate_cluster_config(rancher_endpoint, auth_token, clusters, namespace)
        logger.info(f'{OK} Created a new Kubernetes config file at: {MCLI_KUBECONFIG}')

        # Suggest next steps
        cluster_names = ', '.join(bold(cluster.name) for cluster in clusters)
        logger.info(f'You now have access to {bold(str(len(clusters)))} new clusters: '
                    f'{cluster_names}')

        clusters_failed_creation = []
        platform_creator = PlatformCreator()
        for cluster in clusters:
            cluster_name = cluster.name
            try:
                create_one_platform(creator=platform_creator,
                                    name=cluster_name,
                                    kubernetes_context=cluster_name,
                                    namespace=namespace)
            except PlatformValidationError:
                clusters_failed_creation.append(cluster_name)
            except MCLIConfigError:
                logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
                break

        if len(clusters_failed_creation) > 0:
            logger.info(
                textwrap.dedent(f"""
                    Platform(s) {', '.join(clusters_failed_creation)} already exist. If these are already setup correctly, then nothing more is required.

                    If you would like to update details on them, please delete them and recreate them with:

                    [bold]mcli delete {' '.join(clusters_failed_creation)}[/]
                    [bold]mcli create platform {' '.join(clusters_failed_creation)}[/]
                    """))

    except RuntimeError as e:
        logger.error(f'{FAIL} {e}')
        return 1

    return 0


def add_init_kube_parser(subparser: argparse._SubParsersAction):
    kube_init_parser: argparse.ArgumentParser = subparser.add_parser(
        'init-kube',
        help='Configure your Kubernetes clusters in the MosaicML Cloud',
    )
    kube_init_parser.add_argument('--auth-token', default=None, help='Your bearer token')
    kube_init_parser.add_argument(
        '--endpoint',
        dest='rancher_endpoint',
        default=None,
        help=f'The Rancher instance URL of the form: {RANCHER_ENDPOINT_PATTERN}. This is only required for use cases '
        'with advanced configuration requirements.',
    )
    kube_init_parser.add_argument(
        '--namespace',
        default=None,
        help='Your namespace within the clusters. If it '
        'doesn\'t exist, it\'ll be created for you.',
    )
    kube_init_parser.set_defaults(func=initialize_k8s)
    return kube_init_parser
