""" Functions for deleting MCLI objects """
import fnmatch
import logging
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar

from mcli.config import MESSAGE, MCLIConfig, MCLIConfigError
from mcli.models import MCLIPlatform
from mcli.objects.secrets.platform_secret import SecretManager
from mcli.utils.utils_epilog import ContextPodStatus
from mcli.utils.utils_interactive import query_yes_no
from mcli.utils.utils_kube import PlatformRun, delete_runs, group_pods_by_job, list_pods_across_contexts
from mcli.utils.utils_kube_labels import label
from mcli.utils.utils_logging import FAIL, INFO, OK, console, get_indented_list
from mcli.utils.utils_pod_state import PodState

logger = logging.getLogger(__name__)

# pylint: disable-next=invalid-name
T_NOUN = TypeVar('T_NOUN')


class DeleteGroup(Generic[T_NOUN]):
    """Helper for extracting objects to delete from an existing set
    """

    def __init__(self, requested: List[str], existing: Dict[str, T_NOUN]):
        # Get unique values, with order
        self.requested = list(dict.fromkeys(requested))
        self.existing = existing

        self.chosen: Dict[str, T_NOUN] = {}
        self.missing: List[str] = []
        for pattern in self.requested:
            matching = fnmatch.filter(self.existing, pattern)
            if matching:
                self.chosen.update({k: self.existing[k] for k in matching})
            else:
                self.missing.append(pattern)

        self.remaining = {k: v for k, v in self.existing.items() if k not in self.chosen}


def delete_environment_variable(variable_names: List[str],
                                force: bool = False,
                                delete_all: bool = False,
                                **kwargs) -> int:
    del kwargs
    if not (variable_names or delete_all):
        logger.error(f'{FAIL} Must specify environment variable names or --all.')
        return 1
    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    if delete_all:
        variable_names = ['*']

    group = DeleteGroup(variable_names, {ev.name: ev for ev in conf.environment_variables})

    # Some platforms couldn't be found. Throw a warning and continue
    if group.missing:
        logger.warning(f'{INFO} Could not find environment variable(s) matching: {", ".join(sorted(group.missing))}. '
                       f'Maybe you meant one of: {", ".join(sorted(list(group.remaining)))}?')

    # Nothing to delete, so error
    if not group.chosen:
        logger.error(f'{FAIL} No environment variables to delete')
        return 1

    if not force:
        if len(group.chosen) > 1:
            logger.info(f'{INFO} Ready to delete environment variables:\n'
                        f'{get_indented_list(sorted(list(group.chosen)))}\n')
            confirm = query_yes_no('Would you like to delete the environment variables listed above?')
        else:
            chosen_ev = list(group.chosen)[0]
            confirm = query_yes_no(f'Would you like to delete the environment variable: {chosen_ev}?')
        if not confirm:
            logger.error('Canceling deletion')
            return 1

    conf.environment_variables = list(group.remaining.values())
    conf.save_config()
    return 0


def delete_secret(secret_names: List[str], force: bool = False, delete_all: bool = False, **kwargs) -> int:
    """Delete the requested secret(s) from the user's platforms

    Args:
        secret_names: List of secrets to delete
        force: If True, do not request confirmation. Defaults to False.

    Returns:
        True if deletion was successful
    """
    del kwargs

    if not (secret_names or delete_all):
        logger.error(f'{FAIL} Must specify secret names or --all.')
        return 1

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    if not conf.platforms:
        logger.error(f'{FAIL} No platforms found. You must have at least 1 platform added before working with secrets.')
        return 1

    if delete_all:
        secret_names = ['*']

    # Note, we could just attempt to delete and catch the error.
    # I think it's a bit cleaner to first check if the secret exists, but this will be a bit slower
    # This slowness should be OK for secrets since they are generally small in number

    ref_platform = conf.platforms[0]
    secret_manager = SecretManager(ref_platform)

    group = DeleteGroup(secret_names, {ps.secret.name: ps for ps in secret_manager.get_secrets()})

    # Some platforms couldn't be found. Throw a warning and continue
    if group.missing:
        logger.warning(f'{INFO} Could not find secrets(s) matching: {", ".join(sorted(group.missing))}. '
                       f'Maybe you meant one of: {", ".join(sorted(list(group.remaining)))}?')

    if not group.chosen:
        logger.error(f'{FAIL} No secrets to delete')
        return 1

    if not force:
        if len(group.chosen) > 1:
            logger.info(f'{INFO} Ready to delete secrets:\n'
                        f'{get_indented_list(sorted(list(group.chosen)))}\n')
            confirm = query_yes_no('Would you like to delete the secrets listed above?')
        else:
            secret_name = list(group.chosen)[0]
            confirm = query_yes_no(f'Would you like to delete the secret: {secret_name}?')
        if not confirm:
            logger.error(f'{FAIL} Canceling deletion')
            return 1

    failures: Dict[str, List[str]] = {}
    with console.status('Deleting secrets...') as status:
        for platform in conf.platforms:
            with MCLIPlatform.use(platform):
                status.update(f'Deleting secrets from {platform.name}...')
                for ps in group.chosen.values():
                    success = ps.delete(platform.namespace)
                    if not success:
                        failures.setdefault(ps.secret.name, []).append(platform.name)

    deleted = sorted([name for name in group.chosen if name not in failures])
    if deleted:
        logger.info(f'{OK} Deleted secret(s): {", ".join(deleted)}')

    if failures:
        logger.error(f'{FAIL} Could not delete secret(s): {", ".join(sorted(list(failures.keys())))}')
        for name, failed_platforms in failures.items():
            logger.error(f'Secret {name} could not be deleted from platform(s): {", ".join(sorted(failed_platforms))}')
        return 1

    return 0


def delete_platform(platform_names: List[str], force: bool = False, delete_all: bool = False, **kwargs) -> int:
    del kwargs

    if not (platform_names or delete_all):
        logger.error(f'{FAIL} Must specify platform names or --all.')
        return 1

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    if delete_all:
        platform_names = ['*']

    group = DeleteGroup(platform_names, {pl.name: pl for pl in conf.platforms})

    # Some platforms couldn't be found. Throw a warning and continue
    if group.missing:
        logger.warning(f'{INFO} Could not find platform(s) matching: {", ".join(sorted(group.missing))}. '
                       f'Maybe you meant one of: {", ".join(sorted(list(group.remaining)))}?')

    # Nothing to delete, so error
    if not group.chosen:
        logger.error(f'{FAIL} No platforms to delete')
        return 1

    if not force:
        if len(group.chosen) > 1:
            logger.info(f'{INFO} Ready to delete platforms:\n'
                        f'{get_indented_list(sorted(list(group.chosen)))}\n')
            confirm = query_yes_no('Would you like to delete the platforms listed above?')
        else:
            chosen_platform = list(group.chosen)[0]
            confirm = query_yes_no(f'Would you like to delete the platform: {chosen_platform}?')
        if not confirm:
            logger.error(f'{FAIL} Canceling deletion')
            return 1

    conf.platforms = list(group.remaining.values())
    conf.save_config()

    logger.info(f"{OK} Deleted platform{'s' if len(group.chosen) > 1 else ''}: {', '.join(list(group.chosen.keys()))}")
    return 0


def delete_project(project_name: str, **kwargs) -> int:
    del kwargs

    # TODO: Fix projects implementation
    existing_projects = []
    found_projects = [x for x in existing_projects if x.project == project_name]
    if not found_projects:
        print(f'Unable to find project with name: {project_name}.'
              ' To see all projects run `mcli get projects`')
        return 1
    if len(existing_projects) == 1:
        print('Unable to delete the only existing project'
              ' To see all projects run `mcli get projects`')
        return 1
    if found_projects and len(found_projects) == 1:
        found_project = found_projects[0]
        return found_project.delete()

    return 1


def _format_run_state(text: str):
    return text.title().replace('_', '').lower()


def _get_status_filter(statuses: Optional[List[str]] = None) -> Callable[[List[Dict[str, Any]]], bool]:
    """Get a function that filters runs according to their status
    """

    valid_statuses = {_format_run_state(state.value) for state in PodState}
    if statuses:
        invalid_statuses = {status for status in statuses if status not in valid_statuses}
        if invalid_statuses:
            logger.warning(f'Ignoring invalid status filter(s): {", ".join(sorted(list(invalid_statuses)))}')
            statuses = list(set(statuses).difference(invalid_statuses))

    def _return_true(pod_dicts: List[Dict[str, Any]]) -> bool:
        del pod_dicts
        return True

    def _check_statuses(pod_dicts: List[Dict[str, Any]]) -> bool:
        assert statuses is not None
        pod_statuses = [ContextPodStatus.from_pod_dict(pod_dict) for pod_dict in pod_dicts]
        run_status = _format_run_state(ContextPodStatus.aggregate(pod_statuses).state.value)
        return run_status in statuses

    if statuses is None:
        return _return_true
    else:
        return _check_statuses


# pylint: disable-next=too-many-statements
def delete_run(name_filter: Optional[List[str]] = None,
               platform_filter: Optional[List[str]] = None,
               status_filter: Optional[List[str]] = None,
               delete_all: bool = False,
               force: bool = False,
               **kwargs):
    del kwargs

    if not (name_filter or platform_filter or status_filter or delete_all):
        logger.error(f'{FAIL} Must specify run names or at least one of --platform, --status, --all.')
        return 1

    if not name_filter:
        # Accept all that pass other filters
        name_filter = ['*']

    try:
        filter_statuses = _get_status_filter(status_filter)
    except ValueError as e:
        logger.error(f'{FAIL} {e}')
        return 1

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    if not conf.platforms:
        logger.error(f'{FAIL} No platforms found. You must have at least 1 platform added before working with runs.')
        return 1

    if platform_filter:
        platforms_to_use: List[MCLIPlatform] = []
        unused: Set[str] = set(platform_filter)
        for platform in conf.platforms:
            if platform.name in unused:
                unused.discard(platform.name)
                platforms_to_use.append(platform)
            if not unused:
                break
        if unused:
            logger.warning(f'Ignoring invalid platform filter(s): {", ".join(sorted(list(unused)))}')

        if len(platforms_to_use) == 0:
            logger.error(f'{FAIL} No platforms found matching filter: {", ".join(platform_filter)}')
            return 1

    else:
        platforms_to_use = conf.platforms

    contexts = [p.to_kube_context() for p in platforms_to_use]

    _, context_calls = list_pods_across_contexts(contexts=contexts, labels={label.mosaic.JOB: None})
    runs_to_delete: Dict[str, PlatformRun] = {}
    for response, context in context_calls:
        filtered = group_pods_by_job(pods=response['items'])
        if status_filter:
            filtered = {name: pod_dicts for name, pod_dicts in filtered.items() if filter_statuses(pod_dicts)}
        runs_to_delete.update({name: PlatformRun(name, context) for name in filtered})
    group = DeleteGroup(name_filter, runs_to_delete)

    # Some run name filters couldn't be found. Throw a warning and continue
    if group.missing:
        logger.warning(f'{INFO} Could not find run(s) matching: {", ".join(sorted(group.missing))}')

    if not group.chosen:
        logger.error(f'{FAIL} No runs found matching the specified criteria.')
        return 1

    if not force:
        if len(group.chosen) > 1:
            if len(group.chosen) >= 50:
                logger.info(f'Ready to delete {len(group.chosen)} runs')
                confirm = query_yes_no(f'Would you like to delete all {len(group.chosen)} runs?')
            else:
                logger.info(f'{INFO} Ready to delete runs:\n'
                            f'{get_indented_list(sorted(list(group.chosen)))}\n')
                confirm = query_yes_no('Would you like to delete the runs listed above?')
        else:
            chosen_run = list(group.chosen)[0]
            confirm = query_yes_no(f'Would you like to delete the run: {chosen_run}?')
        if not confirm:
            logger.error(f'{FAIL} Canceling deletion')
            return 1

    plural = 's' if len(group.chosen) > 1 else ''
    with console.status(f'Deleting run{plural}...') as console_status:
        if not delete_runs(list(group.chosen.values())):
            console_status.stop()
            logger.error('Job deletion failed')
            return 1

    logger.info(f'{OK} Deleted run{plural}')
    return 0
