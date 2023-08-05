""" mcli interactive Entrypoint """
import argparse
import logging
from typing import Optional, Set

from mcli.config import MESSAGE, MCLIConfig, MCLIConfigError
from mcli.models.mcli_platform import MCLIPlatform
from mcli.models.run_input import PartialRunInput, RunInput
from mcli.serverside.job.mcli_job import MCLIJob, MCLIJobType
from mcli.serverside.platforms.instance_type import GPUType
from mcli.serverside.platforms.platform import GenericK8sPlatform
from mcli.serverside.platforms.platform_instances import (IncompleteInstanceRequest, InstanceRequest,
                                                          InstanceTypeUnavailable, UserInstanceRegistry, ValidInstance)
from mcli.serverside.runners.runner import Runner
from mcli.utils.utils_epilog import CommonLog, EpilogSpinner, RunEpilog
from mcli.utils.utils_interactive import query_yes_no
from mcli.utils.utils_kube import PlatformRun, connect_to_pod, delete_runs
from mcli.utils.utils_logging import FAIL, INFO, OK, console
from mcli.utils.utils_pod_state import PodState, PodStatus
from mcli.utils.utils_types import get_hours_type

_MAX_INTERACTIVE_DURATION: float = 12

logger = logging.getLogger(__name__)


def _get_interactive_instance_registry() -> UserInstanceRegistry:

    interactive_platforms = []
    for platform in MCLIConfig.load_config(safe=True).platforms:
        if GenericK8sPlatform.from_mcli_platform(platform).interactive:
            interactive_platforms.append(platform)

    return UserInstanceRegistry(interactive_platforms)


# pylint: disable-next=invalid-name
INTERACTIVE_REGISTRY = _get_interactive_instance_registry()


def interactive_entrypoint(
    name: Optional[str] = None,
    platform: Optional[str] = None,
    gpu_type: Optional[str] = None,
    gpus: Optional[int] = None,
    cpus: int = 1,
    hours: float = 1,
    image: str = 'mosaicml/pytorch',
    confirm: bool = True,
    connect: bool = True,
    **kwargs,
) -> int:
    del kwargs

    try:
        request = InstanceRequest(platform=platform, gpu_type=gpu_type, gpu_num=gpus)
        options = INTERACTIVE_REGISTRY.lookup(request)
        logger.debug(f'Found {len(options)} potential instances')

        valid_instance: Optional[ValidInstance] = None
        if len(options) == 1:
            valid_instance = options[0]
        elif len(options) > 1:
            # If multiple options, check for r1z2 options and choose the one with the fewest GPUs
            r1z2_options = [option for option in options if option.platform == 'r1z2']
            if r1z2_options:
                valid_instance = sorted(r1z2_options, key=lambda x: x.gpu_num)[0]

        if not valid_instance:
            raise IncompleteInstanceRequest(request, ValidInstance.to_registry(options), INTERACTIVE_REGISTRY.registry)
        logger.debug(f'Chosen instance type: {valid_instance}')

        if not name:
            name = f'interactive-{valid_instance.gpu_type.replace("_", "-")}-{valid_instance.gpu_num}'.lower()

        partial_run = PartialRunInput(
            run_name=name,
            platform=valid_instance.platform,
            gpu_type=valid_instance.gpu_type,
            gpu_num=valid_instance.gpu_num,
            cpus=cpus,
            command=f'sleep {int(3600 * hours)}',
            image=image,
        )
        run_input = RunInput.from_partial_run_input(partial_run)

        mcli_job = MCLIJob.from_run_input(run_input=run_input)

        if valid_instance.gpu_type != str(GPUType.NONE):
            gpu_cpu_string = f'{valid_instance.gpu_num} GPU(s)'
        else:
            gpu_cpu_string = f'{cpus} CPU(s)'

        logger.info(
            f'{OK} Ready to submit a [bold]{gpu_cpu_string}[/] interactive session for [bold]{hours} hour(s)[/] '
            f'to platform [bold green]{valid_instance.platform}[/]')
        if confirm:
            confirm = query_yes_no('Do you want to submit?')
            if not confirm:
                raise RuntimeError('Canceling!')

        mcli_platform = MCLIPlatform.get_by_name(valid_instance.platform)
        # We already know this is a valid platform name, so it should never return None
        assert mcli_platform is not None
        exit_code = run_mcli_job_interactively(mcli_job, mcli_platform, connect)
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1
    except (IncompleteInstanceRequest, InstanceTypeUnavailable) as e:
        logger.error(e)
        return 1
    except RuntimeError as e:
        logger.error(e)
        return 1

    return exit_code or 0


def run_mcli_job_interactively(
    mcli_job: MCLIJob,
    mcli_platform: MCLIPlatform,
    connect: bool,
) -> int:
    runner = Runner()
    runner.submit(job=mcli_job, job_type=MCLIJobType.INTERACTIVE)
    if connect:
        with MCLIPlatform.use(mcli_platform):
            logger.info(f'{INFO} Interactive session submitted. Waiting for it to start...')
            logger.info(f'{INFO} Press Ctrl+C to quit and interact with your session manually.')
            epilog = RunEpilog(mcli_job.unique_name, mcli_platform.namespace)
            last_status: Optional[PodStatus] = None
            with EpilogSpinner() as spinner:
                last_status = epilog.wait_until(callback=spinner, timeout=300)

            # Wait timed out
            common_log = CommonLog(logger)
            context = mcli_platform.to_kube_context()
            exec_cmd = f'kubectl --context {context.name} exec -it {epilog.rank0_pod} -- /bin/bash'
            if last_status is None:
                get_pods_cmd = f'kubectl --context {context.name} get pods -w {epilog.rank0_pod}'
                logger.warning(
                    'Waiting for interactive session to spawn exceeded the timeout. You can monitor it '
                    f'using:\n\n{get_pods_cmd}\n\n'
                    f'Once the pod is "Running", you can attach to it using:\n\n{exec_cmd}',)
                return 0
            elif last_status.state == PodState.FAILED_PULL:
                common_log.log_pod_failed_pull(mcli_job.unique_name, mcli_job.image)
                with console.status('Deleting failed run...'):
                    delete_runs([PlatformRun(mcli_job.unique_name, mcli_platform.to_kube_context())])
                return 1
            elif last_status.state == PodState.FAILED:
                common_log.log_pod_failed(mcli_job.unique_name)
                return 1
            elif last_status.state.before(PodState.RUNNING):
                common_log.log_unknown_did_not_start()
                logger.debug(last_status)
                return 1

            logger.info(f'{OK} Interactive session created. Attaching...')
            logger.info(
                f'{INFO} Press Ctrl+C to quit attaching. Once attached, press Ctrl+D or type exit '
                'to leave the session.',)
            connected = connect_to_pod(epilog.rank0_pod, context)
            if not connected:
                logger.warning(f'{FAIL} Could not connect to the interactive session.')
                logger.warning(
                    f'Please double-check that [bold]{context.name}[/] is your context and '
                    f'[bold]{context.namespace}[/] is your correct namespace.',)
                logger.warning(f'If so, try manually running {exec_cmd}')
    else:
        logger.info(f'{OK} Interactive session submitted. Please use `kubectl` to connect to it')
    return 0


def configure_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:

    parser.add_argument(
        '--name',
        default=None,
        type=str,
        help='Name for the interactive session. '
        'Default: "interactive-<gpu type>-<gpu num>"',
    )

    if INTERACTIVE_REGISTRY.registry:
        platform_descriptions = [
            IncompleteInstanceRequest._get_platform_description(pl, instances)
            for pl, instances in INTERACTIVE_REGISTRY.registry.items()
        ]
        full_platform_description = '\nAvailable interactive instances:\n\n'
        full_platform_description += '\n'.join(platform_descriptions)
    else:
        full_platform_description = '\nNo interactive instances available\n\n'

    platform_arguments = parser.add_argument_group('Instance settings', description=full_platform_description)
    available_platforms = sorted(list(INTERACTIVE_REGISTRY.registry.keys()))
    platform_arguments.add_argument(
        '--platform',
        default=None,
        choices=available_platforms,
        metavar='PLATFORM',
        help='Platform where your interactive session should run. If you '
        'only have one available, that one will be selected by default. '
        'Depending on your platform, you\'ll have access to different GPU types and counts. '
        'See the available combinations above. '
        f'Choices: {", ".join(available_platforms)}',
    )

    available_types: Set[str] = set()
    available_nums: Set[int] = set()
    for instance in INTERACTIVE_REGISTRY.registry.values():
        for gpu_type, gpu_nums in instance.items():
            available_types.add(str(gpu_type))
            available_nums.update(set(gpu_nums))
    gpu_types = sorted(list(available_types))
    gpu_nums = sorted(list(available_nums))

    platform_arguments.add_argument(
        '--gpu-type',
        choices=gpu_types,
        metavar='TYPE',
        help=f'Type of GPU to use. Choices: {", ".join(gpu_types)}. '
        'Valid GPU types depend on the platform and GPU numbers requested. See the available combinations above',
    )
    platform_arguments.add_argument(
        '--gpus',
        type=int,
        metavar='NGPUs',
        choices=gpu_nums,
        help=f'Number of GPUs to run interactively. Choices: {", ".join(str(x) for x in gpu_nums)}. '
        'Valid GPU numbers depend on the platform and GPU type. See the available combinations above.',
    )
    platform_arguments.add_argument(
        '--cpus',
        default=1,
        type=int,
        metavar='NCPUs',
        help='Number of CPUs to run interactively. This will only take effect when --gpu-type is set to "none". '
        'Default: %(default)s',
    )

    parser.add_argument(
        '--hours',
        default=1,
        type=get_hours_type(_MAX_INTERACTIVE_DURATION),
        help='Number of hours the interactive session should run. '
        f' Default: %(default)s. MAX: {_MAX_INTERACTIVE_DURATION}',
    )
    parser.add_argument(
        '--image',
        default='mosaicml/pytorch',
        help='Docker image to use',
    )
    parser.add_argument(
        '-y',
        '--no-confirm',
        dest='confirm',
        action='store_false',
        help='Do not request confirmation',
    )
    parser.add_argument(
        '--no-connect',
        dest='connect',
        action='store_false',
        help='Do not connect to the interactive session immediately',
    )

    parser.set_defaults(func=interactive_entrypoint)
    return parser


def add_interactive_argparser(subparser: argparse._SubParsersAction,) -> argparse.ArgumentParser:
    """Adds the get parser to a subparser

    Args:
        subparser: the Subparser to add the Get parser to
    """

    interactive_parser: argparse.ArgumentParser = subparser.add_parser(
        'interactive',
        help='Create an interactive session',
        description=
        'Create an interactive session on a node with persistent storage. Once created, you can attach to the session. Interactive sessions are only allowed in pre-specified platforms.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    get_parser = configure_argparser(parser=interactive_parser)
    return get_parser
