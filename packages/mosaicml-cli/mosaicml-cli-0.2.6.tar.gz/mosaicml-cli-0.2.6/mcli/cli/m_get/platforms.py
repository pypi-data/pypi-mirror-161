"""CLI getter for platforms"""
from dataclasses import dataclass
from typing import Dict, Generator, List

from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.config import MCLIConfig, MCLIConfigError
from mcli.models import MCLIPlatform
from mcli.serverside.platforms.gpu_type import GPUType
from mcli.serverside.platforms.platform_instances import UserInstanceRegistry
from mcli.utils.utils_logging import FAIL, err_console


@dataclass
class PlatformDisplayItem(MCLIDisplayItem):
    context: str
    namespace: str
    gpu_types_and_nums: Dict[str, List[int]]


class MCLIPlatformDisplay(MCLIGetDisplay):
    """`mcli get platforms` display class
    """

    def __init__(self, platforms: List[MCLIPlatform]):
        self.platforms = platforms

    def __iter__(self) -> Generator[PlatformDisplayItem, None, None]:
        gpu_registry = _get_gpu_registry(self.platforms)
        for platform in self.platforms:
            yield PlatformDisplayItem(name=platform.name,
                                      context=platform.kubernetes_context,
                                      namespace=platform.namespace,
                                      gpu_types_and_nums=gpu_registry[platform.name])


def _get_gpu_registry(platforms: List[MCLIPlatform]) -> Dict[str, Dict[str, List[int]]]:
    user_registry = UserInstanceRegistry(platforms=platforms)
    gpu_info: Dict[str, Dict[str, List[int]]] = {}
    for platform, gpu_dict in user_registry.registry.items():
        gpu_info[platform] = {}
        for gpu_type, gpu_nums in gpu_dict.items():
            if gpu_type == GPUType.NONE:
                gpu_type_str = 'none (CPU only)'
            else:
                gpu_type_str = gpu_type.value
            gpu_info[platform][gpu_type_str] = gpu_nums
    return gpu_info


def get_platforms(output: OutputDisplay = OutputDisplay.TABLE, **kwargs) -> int:
    del kwargs

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        err_console.print(f'{FAIL} MCLI not yet initialized. Please run `mcli init` and then `mcli create platform` '
                          'to create your first platform.')
        return 1

    display = MCLIPlatformDisplay(conf.platforms)
    display.print(output)
    return 0
