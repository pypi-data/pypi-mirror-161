""" mcli ticket Entrypoint """
import argparse
import datetime as dt
import io
import json
import logging
import re
import textwrap
from base64 import b64decode
from contextlib import redirect_stdout
from typing import Any, Dict, List, Optional, Tuple, cast

import arrow
import yaml
from slack_sdk import WebClient
from slack_sdk.models.blocks import MarkdownTextObject, SectionBlock

from mcli import __version__, config
from mcli.cli.m_get.display import OutputDisplay
from mcli.cli.m_get.runs import get_runs
from mcli.cli.m_log.m_log import get_logs
from mcli.models.mcli_platform import MCLIPlatform
from mcli.utils.utils_interactive import choose_one, query_yes_no, simple_prompt
from mcli.utils.utils_kube import KubeContext, find_jobs_by_label, find_pods_by_label, read_secret
from mcli.utils.utils_kube_labels import label

logger = logging.getLogger(__name__)

SLACK_CHANNEL = 'C03MGE78BKJ'  # mcli-tickets

SLACK_TOKEN_NAMESPACE = 'mcli-tickets-shared'
SLACK_TOKEN_NAME = 'mcli-tickets-token'


class CredentialsNotFoundError(Exception):
    pass


def get_slack_client(config: config.MCLIConfig) -> WebClient:
    if not config.platforms:
        failure_message = textwrap.dedent("""\
        `mcli ticket` can only be used after you have initialized at least one platform.
        If you need help initializing platforms, please contact us at support@mosaicml.com.
        """)
        logger.error(failure_message)
        raise CredentialsNotFoundError(failure_message)

    for platform in config.platforms:
        try:
            with MCLIPlatform.use(platform):
                secret = read_secret(namespace=SLACK_TOKEN_NAMESPACE, name=SLACK_TOKEN_NAME)
                if secret is None:
                    continue

                secret_data: str = secret['data'][SLACK_TOKEN_NAME]  # type: ignore
                secret_value = b64decode(secret_data).decode('utf-8')

                client = WebClient(token=secret_value)
                client.auth_test()

                return client
        except:
            pass

    failure_message = textwrap.dedent("""\
    Valid credentials for submitting a ticket could not be found in any of your initialized platforms.
    Please contact us at support@mosaicml.com.
    """)

    logger.error(failure_message)
    raise CredentialsNotFoundError(failure_message)


def post_ticket_to_slack(slack_client: WebClient, name: str, description: str, mcli_config: str,
                         run: Optional[Dict[str, str]], job_yaml: Optional[str], pod_yamls: Optional[List[str]],
                         logs: Optional[str]):

    ticket_fields: List[Tuple[str, str]] = [('MCLI Version', __version__)]
    if run is not None:
        ticket_fields += list(run.items())

    files_to_upload: List[Tuple[str, str]] = [('mcli_config', mcli_config)]

    if job_yaml is not None:
        files_to_upload += [('Job', job_yaml)]

    if pod_yamls is not None:
        files_to_upload += [(f'Pod {i}', pod_yaml) for i, pod_yaml in enumerate(pod_yamls)]

    if logs is not None:
        files_to_upload += [('logs', logs)]

    response = slack_client.chat_postMessage(
        channel=SLACK_CHANNEL,
        # The `text` field is only shown on legacy clients
        text=':rotating_light: *A New Ticket has been Submitted by _{name}_* :rotating_light:',
        blocks=[
            SectionBlock(text=MarkdownTextObject(
                text=f':rotating_light: *A New Ticket has been Submitted by _{name}_* :rotating_light:')),
            SectionBlock(text=MarkdownTextObject(text=f'*Description:* {description}')),
            SectionBlock(fields=[MarkdownTextObject(text=f'*{k}:* {v}') for k, v in ticket_fields])
        ])
    assert response.status_code == 200

    for filename, content in files_to_upload:
        file_response = slack_client.files_upload(channels=SLACK_CHANNEL, content=content, title=filename)
        assert file_response.status_code == 200


def try_get_runs() -> Optional[List[Dict[str, str]]]:
    logger_level = logger.level
    logger.setLevel(logging.ERROR)
    try:
        runs_buffer = io.StringIO()
        with redirect_stdout(runs_buffer):
            get_runs(output=OutputDisplay.JSON)
        runs_str = runs_buffer.getvalue()

        # strip console formatting
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|')
        runs_str = ansi_escape.sub('', runs_str)

        # replace newlines with a space, being careful not to produce consecutive spaces
        whitespace_regex = re.compile(r'\s+')
        runs_str = whitespace_regex.sub(' ', runs_str)

        runs = json.loads(runs_str)
    except Exception:
        return None
    finally:
        logger.setLevel(logger_level)

    return runs


def try_get_job_yaml(contexts: List[KubeContext], run_name: str) -> Optional[str]:
    try:
        run_label = {label.mosaic.JOB: run_name}
        jobs_res = find_jobs_by_label(contexts=contexts, labels=run_label)
        assert jobs_res is not None
        jobs = cast(List[Dict[str, Any]], jobs_res.response['items'])
        assert len(jobs) == 1
        job = jobs[0]

        del job['metadata']['managedFields']  # This section is big and useless
        job_yaml = yaml.dump(job)

        return job_yaml
    except Exception:
        return None


def try_get_pod_yamls(contexts: List[KubeContext], run_name: str) -> Optional[List[str]]:
    try:
        run_label = {label.mosaic.JOB: run_name}
        pods_res = find_pods_by_label(contexts=contexts, labels=run_label)
        assert pods_res is not None
        pods = cast(List[Dict[str, Any]], pods_res.response['items'])

        pod_yamls: List[str] = []
        for pod in pods:
            del pod['metadata']['managedFields']  # This section is big and useless
            pod_yamls.append(yaml.dump(pod))

        return pod_yamls
    except Exception:
        return None


def try_get_logs(run_name: str) -> Optional[str]:
    logger_level = logger.level
    logger.setLevel(logging.ERROR)
    try:
        logs_buffer = io.StringIO()
        with redirect_stdout(logs_buffer):
            get_logs(run_name=run_name)
        logs = logs_buffer.getvalue()

        return logs
    except Exception:
        return None
    finally:
        logger.setLevel(logger_level)


def ticket_entrypoint(**kwargs):
    del kwargs
    logger.info(
        textwrap.dedent("""\
    ===================================
    Welcome to the MCLI support system!
    ===================================
    """))

    conf = config.MCLIConfig.load_config(safe=True)

    try:
        slack_client = get_slack_client(conf)
    except CredentialsNotFoundError:
        return

    name = None
    namespaces = set([p.namespace for p in conf.platforms])
    if len(namespaces) == 1:
        name = namespaces.pop()
    else:
        name = simple_prompt(
            message='Please provide your name (so we can follow up with you):',
            mandatory=True,
        )

    description = simple_prompt(
        message="Please provide a brief description of your issue (we'll follow up for more information):",
        mandatory=False,
    ) or 'none provided 😭'

    runs = try_get_runs()

    include_run = bool(runs) and query_yes_no(
        message='Do you want to attach metadata from an MCLI run to this ticket?',
        default=True,
    )

    chosen_run = None
    job_yaml = None
    pod_yamls = None
    logs = None

    if include_run:
        assert runs is not None

        def _format_run(run: Dict[str, Any]) -> str:
            run_name = run['name']
            platform = run['platform']

            timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
            submitted = arrow.get(run['created_time'], 'YYYY-MM-DD HH:mm A', tzinfo=timezone).humanize()
            status = run['status']
            return f'{run_name} [{status}]: submitted {submitted} to {platform}'

        chosen_run = choose_one(
            message='Choose a run to attach:',
            options=runs,
            formatter=_format_run,
        )

        run_name = chosen_run['name']
        contexts = [p.to_kube_context() for p in conf.platforms]

        job_yaml = try_get_job_yaml(contexts=contexts, run_name=run_name)
        pod_yamls = try_get_pod_yamls(contexts=contexts, run_name=run_name)

        include_logs = query_yes_no(
            message="Do you want to attach this run's logs? This will help us debug your issue.",
            default=True,
        )

        if include_logs:
            logs = try_get_logs(run_name=run_name)
        else:
            logs = None

    else:
        chosen_run = None
        job_yaml = None
        pod_yamls = None
        logs = None

    post_ticket_to_slack(slack_client=slack_client,
                         name=name,
                         description=description,
                         mcli_config=str(conf),
                         run=chosen_run,
                         job_yaml=job_yaml,
                         pod_yamls=pod_yamls,
                         logs=logs)

    logger.info("Your ticket has been submitted. We'll get back to you as soon as possible!")


def add_ticket_argparser(subparser: argparse._SubParsersAction) -> None:
    run_parser: argparse.ArgumentParser = subparser.add_parser(
        'ticket',
        help='Submit a support ticket for help configuring MCLI or debugging a run submission',
    )
    run_parser.set_defaults(func=ticket_entrypoint)
