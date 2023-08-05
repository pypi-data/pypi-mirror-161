""" Defines what Instance Types a Platform supports """
from __future__ import annotations

import textwrap
from abc import ABC
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, Tuple

from mcli.serverside.platforms.gpu_type import GPUType
from mcli.serverside.platforms.instance_type import InstanceType
from mcli.utils.utils_logging import set_indent

if TYPE_CHECKING:
    from mcli.models.mcli_platform import MCLIPlatform


class InstanceTypeUnavailable(Exception):
    """ Raised if the instance type is not available on a platform"""
    attempted_instance_type: InstanceTypeLookupData
    current_platform_name: Optional[str] = None
    current_platform_available_instances: Dict[GPUType, List[int]] = {}
    all_platform_available_instances: Dict[str, Dict[GPUType, List[int]]] = {}

    def __init__(
        self,
        attempted_instance_type: InstanceTypeLookupData,
        current_platform_available_instances: Dict[GPUType, List[int]],
    ) -> None:
        self.attempted_instance_type = attempted_instance_type
        self.current_platform_available_instances = current_platform_available_instances
        self.all_platform_available_instances = {}
        super().__init__()

    @staticmethod
    def _get_instances_description(available_dict: Dict[GPUType, List[int]]) -> str:
        gpus = sorted(list(available_dict.keys()))

        def get_num_str(nums: List[int]) -> str:
            return ', '.join([f'{ii}x' for ii in nums])

        descs = [f'{get_num_str(available_dict[gpu])} {gpu}' for gpu in gpus]
        return '\n'.join(descs)

    def __str__(self) -> str:
        ait = self.attempted_instance_type

        if ait.gpu_type == GPUType.NONE:
            instance_desc = f'{ait.cpus or 1} CPU(s) and 0 GPUs'
        else:
            instance_desc = f'{ait.gpu_num}x {ait.gpu_type} GPUs'

        if self.current_platform_name:
            platform_desc = f'On platform {self.current_platform_name}'
        else:
            platform_desc = 'On the current platform'

        error_message = f"""

{platform_desc}, the requested instance with {instance_desc} is not available.

{self.get_current_platforms_error_message()}
{self.get_other_platforms_error_message()}
"""
        return textwrap.dedent(error_message)

    def get_current_platforms_error_message(self) -> str:
        error_message = ''
        cpai = self.current_platform_available_instances
        if cpai:
            error_message = f"""\
The instance types available for this platform are:
{self._get_instances_description(cpai)}
"""
        return error_message

    def get_other_platforms_error_message(self) -> str:
        error_message = ''
        ait = self.attempted_instance_type
        if self.all_platform_available_instances:
            matching_platforms: List[Tuple[str, List[int]]] = []
            for platform_name, instance_data in self.all_platform_available_instances.items():
                if ait.gpu_type in instance_data:
                    matching_platforms.append((platform_name, instance_data[ait.gpu_type]))

            if matching_platforms:
                found_platforms_str = ', '.join([pt_name for pt_name, _ in matching_platforms])
                error_message += f'Did you mean a different platform? ({found_platforms_str})\n'
                for pt_name, instance_nums_available in matching_platforms:
                    if ait.gpu_type != GPUType.NONE:
                        gpu_selector_str = f'{ait.gpu_num}x {ait.gpu_type}(s)'
                    else:
                        gpu_selector_str = 'cpu jobs'
                    if ait.gpu_num in instance_nums_available:
                        error_message += f'On: {pt_name}, {gpu_selector_str} can be run'
                    else:

                        quantities_str = ', '.join(f'{ii}x' for ii in sorted(instance_nums_available))
                        error_message += f'On: {pt_name}, only {quantities_str} {ait.gpu_type}(s) can be run'
                    error_message += '\n'
        return error_message


GPU_CONFIG = Dict[GPUType, List[int]]  # Mapping of GPUTypes to a list of gpu counts


class InstanceRequest(NamedTuple):
    """Partially filled-in user's instance request
    """
    platform: Optional[str]
    gpu_type: Optional[str]
    gpu_num: Optional[int]

    def __str__(self) -> str:
        messages = [
            f'Platform: {self.platform or "-"}',
            f'GPU Type: {self.gpu_type or "-"}',
            f'Count: {self.gpu_num if self.gpu_num is not None else "-"}',
        ]
        return ', '.join(messages)


class ValidInstance(NamedTuple):
    """A fully-entered valid instance request
    """
    platform: str
    gpu_type: str
    gpu_num: int

    def __str__(self) -> str:
        messages = [
            f'Platform: {self.platform}',
            f'GPU Type: {self.gpu_type}',
            f'Count: {self.gpu_num}',
        ]
        return ', '.join(messages)

    @classmethod
    def to_registry(cls, instances: List[ValidInstance]) -> Dict[str, GPU_CONFIG]:
        """Convert a list of valid instance requests to a registry

        Args:
            instances: List of valid instance requests

        Returns:
            A registry that maps platforms to gpu types and gpu counts
        """
        registry: Dict[str, GPU_CONFIG] = {}
        for instance in instances:
            instance_configs = registry.setdefault(instance.platform, {})
            instance_configs.setdefault(GPUType.from_string(instance.gpu_type), []).append(instance.gpu_num)

        return registry


class IncompleteInstanceRequest(Exception):
    """Raised if an instance request could not be completed with the specified parameters

    This can happen for two main reasons:
    1. The request specified an instance that doesn't exist in the user's platforms
    2. The request under-specified which instance to use and multiple could satisfy the constraints

    In either case, an error is raised with a message alerting the user to the possible instance requests they can make
    """
    requested: InstanceRequest
    options: Dict[str, GPU_CONFIG]
    registry: Dict[str, GPU_CONFIG]

    def __init__(self, requested: InstanceRequest, options: Dict[str, GPU_CONFIG], registry: Dict[str, GPU_CONFIG]):
        self.requested = requested
        self.options = options
        self.registry = registry

    @staticmethod
    def _get_platform_description(name: str, instances: GPU_CONFIG):
        instances_desc = set_indent(InstanceTypeUnavailable._get_instances_description(instances), 4)
        platform_desc = f'{name}:\n{instances_desc}'
        return platform_desc

    def __str__(self) -> str:

        if not self.registry:
            # User doesn't have any instances
            return 'No instances available. Please run `mcli create platform` to create your first platform.'

        requested_message = set_indent(
            f"""
        Requested an instance with parameters:
        platform: {self.requested.platform or '-'}
        gpu_type: {self.requested.gpu_type or '-'}
        gpu_num:  {self.requested.gpu_num if self.requested.gpu_num is not None else '-'}
        """, 0).lstrip()

        available_message: str
        if self.options:
            # Couldn't narrow down fully, so say that
            platform_descs = [
                self._get_platform_description(name, instances) for name, instances in self.options.items()
            ]
            full_platform_message = '\n'.join(platform_descs)
            available_message = f'The following instances match your requested values:\n\n{full_platform_message}'
        else:
            # No matching values, so give all options
            platform_descs = [
                self._get_platform_description(name, instances) for name, instances in self.registry.items()
            ]
            full_platform_message = '\n'.join(platform_descs)
            available_message = ('No instances match your requested values. '
                                 f'Available instances are:\n\n{full_platform_message}')
        available_message = set_indent(available_message, 0).lstrip()

        error_message = ('Could not select an instance with the parameters provided.\n\n'
                         f'{requested_message}\n\n'
                         f'{available_message}')
        return set_indent(error_message, 0)


class UserInstanceRegistry():
    """Registry of instances that the user has access to

    Args: platforms (List[MCLIPlatform]): A list of platforms to search. If not provided, all of the user's platforms
    will be checked

    Attributes:
        registry (Dict[str, GPU_CONFIG]): A registry that maps platform names to GPU types and GPU counts
    """
    registry: Dict[str, GPU_CONFIG]

    def __init__(self, platforms: Optional[List[MCLIPlatform]] = None):
        self.registry = self.build_registry(platforms=platforms)

    @staticmethod
    def _get_platform_instances(platform: MCLIPlatform) -> GPU_CONFIG:
        # pytest: disable-next=import-outside-toplevel
        from mcli.serverside.platforms import GenericK8sPlatform

        k8s_platform = GenericK8sPlatform.from_mcli_platform(platform)
        return k8s_platform.allowed_instances.available_instances

    def build_registry(self, platforms: Optional[List[MCLIPlatform]] = None) -> Dict[str, GPU_CONFIG]:
        """Build the user's instance registry

        Args:
            platforms: An optional list of platforms to look for instances. If not provided, all of the user's
                platforms will be checked.

        Returns:
            A registry that maps platform names to GPU types and GPU counts
        """
        # pylint: disable-next=import-outside-toplevel
        from mcli.config import MCLIConfig

        if not platforms:
            conf = MCLIConfig.load_config(safe=True)
            platforms = conf.platforms

        registry = {pl.name: self._get_platform_instances(pl) for pl in platforms}
        return registry

    def lookup(
        self,
        request: InstanceRequest,
    ) -> List[ValidInstance]:
        """Look up all instances that match the user's request

        Args:
            request: A (possibly incomplete) user instance request. This will be checked against the registry to
                determine if the request can be fulfilled.

        Returns:
            A list of valid instance requests
        """

        options: List[ValidInstance] = []
        for found_platform, instances in self.registry.items():
            if request.platform and request.platform != found_platform:
                # Not the right platform
                continue

            gpu_type = GPUType.from_string(request.gpu_type) if request.gpu_type else None
            if gpu_type and gpu_type not in instances:
                # Incorrect gpu types
                continue

            # Get possibilities with a valid gpu type
            poss_types = [gpu_type] if gpu_type else list(instances)
            for gt in poss_types:
                found_nums = instances[gt]
                # Get only those with a valid gpu num
                valid_nums: List[int] = []
                if request.gpu_num is not None:
                    valid_nums = [request.gpu_num] if request.gpu_num in found_nums else []
                else:
                    valid_nums = found_nums
                options.extend([ValidInstance(found_platform, str(gt), n) for n in valid_nums])

        return options


class InstanceTypeLookupData(NamedTuple):
    """ Used for looking up instances """
    gpu_type: GPUType
    gpu_num: int
    cpus: Optional[int] = None

    @property
    def _key(self) -> Tuple[GPUType, int]:
        return (self.gpu_type, self.gpu_num)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._key == other._key
        else:
            return False

    def __hash__(self) -> int:
        return hash(self._key)


class PlatformInstances(ABC):
    """ How a platform defines what instances are available to itself """
    # Used to define what combinations of GPUTypes and numbers of each GPU are available
    available_instances: Dict[GPUType, List[int]] = {}

    def get_instance_type(
        self,
        gpu_type: GPUType,
        gpu_num: int,
        cpus: Optional[int] = None,
    ) -> InstanceType:
        """Converts GPUType, GPUNum into an InstanceType given a Platforms
        Availability

        Args:
            gpu_type: The Type of GPU Requested
            gpu_num: The Number of GPUs Requested
            cpus: Optional cpus requested iff GPUType is None

        Returns:
            InstanceType of the requeted Instance

        Throws:
            InstanceTypeUnavailable: if no instance with the specified specs could be found
        """
        attempted_it = InstanceTypeLookupData(gpu_type, gpu_num, cpus)
        del cpus
        if gpu_type == GPUType.NONE:
            gpu_num = 0
        if gpu_type not in self.available_instances:
            raise InstanceTypeUnavailable(
                attempted_instance_type=attempted_it,
                current_platform_available_instances=self.available_instances,
            )
        if gpu_num not in self.available_instances.get(gpu_type, []):
            raise InstanceTypeUnavailable(
                attempted_instance_type=attempted_it,
                current_platform_available_instances=self.available_instances,
            )
        return InstanceType(gpu_type, gpu_num)

    def validate_all_instance_combinations(self) -> bool:
        """Helper for validating that all InstanceTypes produce selectors
        """
        passed = True
        for gpu_type, gpu_nums in self.available_instances.items():
            for gpu_num in gpu_nums:
                # pylint: disable-next=assignment-from-no-return
                instance_type = self.get_instance_type(gpu_type, gpu_num)
                selectors = instance_type.selectors
                if not selectors:
                    print(f'No selectors found for gpu: {gpu_type}, num: {gpu_num}')
                    passed = False
        return passed


class CloudPlatformInstances(PlatformInstances):
    """ A Cloud Platform Map for Cloud Platforms to define instances that are available """

    # Used for Cloud Platforms where GPUType+GPUNum produce InstanceTypes directly
    instance_type_map: Dict[InstanceTypeLookupData, InstanceType] = {}

    def __init__(
        self,
        instance_type_map: Optional[Dict[InstanceTypeLookupData, InstanceType]] = None,
    ) -> None:
        self.available_instances = {}
        self.instance_type_map = instance_type_map if instance_type_map else {}
        for it_data in self.instance_type_map:
            if it_data.gpu_type not in self.available_instances:
                self.available_instances[it_data.gpu_type] = []
            if it_data.gpu_num not in self.available_instances[it_data.gpu_type]:
                self.available_instances[it_data.gpu_type].append(it_data.gpu_num)

    def get_instance_type(
        self,
        gpu_type: GPUType,
        gpu_num: int,
        cpus: Optional[int] = None,
    ) -> InstanceType:
        # Calls super just to ensure non available GPU throw properly
        _ = super().get_instance_type(
            gpu_type,
            gpu_num,
            cpus,
        )
        it_data = InstanceTypeLookupData(gpu_type, gpu_num, cpus)
        if it_data not in self.instance_type_map:
            raise InstanceTypeUnavailable(
                attempted_instance_type=it_data,
                current_platform_available_instances=self.available_instances,
            )
        return self.instance_type_map[it_data]


class PlatformInstanceGPUConfiguration(NamedTuple):
    """ A Helper Container to ensure that all possible options for an
    internal GPU cluster are configured
    """
    gpu_type: GPUType
    gpu_nums: List[int]
    gpu_selectors: Dict[str, str]
    cpus: Optional[int] = None
    cpus_per_gpu: Optional[int] = None
    memory: Optional[int] = None
    memory_per_gpu: Optional[int] = None
    storage: Optional[int] = None
    storage_per_gpu: Optional[int] = None
    multinode_rdma_roce: Optional[int] = None


class LocalPlatformInstances(PlatformInstances):
    """ A Local Platform implementation to parameterize different instance types and resources """

    # Maximum machine CPU size for the Platform (CPU Jobs only)
    MIN_CPU: int = 1
    MAX_CPU: int = 128

    # Used to batch set selectors for different GPU types.
    # Adds a default selector for all gpu_num amounts of a GPUType
    default_gpu_type_selector: Dict[GPUType, Dict[str, str]] = {}

    # Used to batch set selectors for certain GPU_Nums
    # Adds a default selector for all gpu_num amounts
    #
    #  Example: 8 -> 8 wide instance selector
    #           1 -> single-GPU instance selector
    default_gpu_num_selector: Dict[int, Dict[str, str]] = {}

    # Note: This is mostly only for internal clusters where multiple jobs
    #    can schedule on the same machine and a machine can be split.
    #    Reduces only the request, but not limit for compressible resources (cpu)
    #    For incompressible resources, the request limit will also be changed
    #
    #  Example:
    #    Default:
    #    Request 2 GPUs, setting GPUType_cpus (X) gives (X CPUs, requested and limit)
    #    Request 2 GPUs, setting GPUType_memory (X) gives (X CPUs, requested and limit)
    #    Request 2 GPUs, setting GPUType_storage (X) gives (X CPUs, requested and limit)
    #
    #    Per Gpu Overrides:
    #    Request 2 GPUs, setting GPUType_cpus_per_gpu (X) gives (X * 2 CPUs, requested, full cpus limit)
    #    Request 2 GPUs, setting GPUType_memory_per_gpu (X) gives (X * 2 CPUs, requested and limit)
    #    Request 2 GPUs, setting GPUType_storage_per_gpu (X) gives (X * 2 CPUs, requested and limit)
    #
    #    safety_margin -> subtracts safety_margin from all produced values in the designated value

    default_gpu_type_cpus: Dict[GPUType, int] = {}
    default_gpu_type_memory: Dict[GPUType, int] = {}
    default_gpu_type_storage: Dict[GPUType, int] = {}

    default_gpu_type_cpus_per_gpu: Dict[GPUType, int] = {}
    default_gpu_type_memory_per_gpu: Dict[GPUType, int] = {}
    default_gpu_type_storage_per_gpu: Dict[GPUType, int] = {}

    default_gpu_type_multinode_rdma_roce: Dict[GPUType, int] = {}

    # Note: Applies to 2 CPU, 10% Memory, 10% Storage
    safety_margin_cpu: float = 2
    safety_margin_memory: float = 0.1
    safety_margin_storage: float = 0.1

    def __init__(
        self,
        available_instances: Optional[Dict[GPUType, List[int]]] = None,
        instance_type_map: Optional[Dict[InstanceTypeLookupData, InstanceType]] = None,
        gpu_type_selector: Optional[Dict[GPUType, Dict[str, str]]] = None,
        gpu_num_selector: Optional[Dict[int, Dict[str, str]]] = None,
        gpu_configurations: Optional[List[PlatformInstanceGPUConfiguration]] = None,
    ) -> None:
        self.available_instances = available_instances or {}
        self.instance_type_map = instance_type_map or {}
        for it_data in self.instance_type_map:
            if it_data.gpu_type not in self.available_instances:
                self.available_instances[it_data.gpu_type] = []
            if it_data.gpu_num not in self.available_instances[it_data.gpu_type]:
                self.available_instances[it_data.gpu_type].append(it_data.gpu_num)

        self.default_gpu_type_selector = gpu_type_selector or {}
        self.default_gpu_num_selector = gpu_num_selector or {}

        self.safety_margin_cpu: float = 1
        self.safety_margin_memory: float = 0.1
        self.safety_margin_storage: float = 0.1

        self.default_gpu_type_cpus: Dict[GPUType, int] = {}
        self.default_gpu_type_memory: Dict[GPUType, int] = {}
        self.default_gpu_type_storage: Dict[GPUType, int] = {}

        self.default_gpu_type_cpus_per_gpu: Dict[GPUType, int] = {}
        self.default_gpu_type_memory_per_gpu: Dict[GPUType, int] = {}
        self.default_gpu_type_storage_per_gpu: Dict[GPUType, int] = {}

        self.default_gpu_type_multinode_rdma_roce: Dict[GPUType, int] = {}

        gpu_configurations = gpu_configurations or []
        for gpu_config in gpu_configurations:
            self.add_platform_instance_gpu_configuration(gpu_config)

    def add_platform_instance_gpu_configuration(
        self,
        gpu_configuration: PlatformInstanceGPUConfiguration,
    ):
        """Adds a batch of settings for a single GPU Type

        Args:
            gpu_configuration: The GPU Configuration Batch
        """
        if gpu_configuration.gpu_type in self.available_instances:
            print(f'WARNING: {gpu_configuration.gpu_type.value} may already be configured')
        self.available_instances[gpu_configuration.gpu_type] = gpu_configuration.gpu_nums
        self.default_gpu_type_selector[gpu_configuration.gpu_type] = gpu_configuration.gpu_selectors
        if gpu_configuration.cpus is not None:
            self.default_gpu_type_cpus[gpu_configuration.gpu_type] = gpu_configuration.cpus
        if gpu_configuration.cpus_per_gpu is not None:
            self.default_gpu_type_cpus_per_gpu[gpu_configuration.gpu_type] = gpu_configuration.cpus_per_gpu
        if gpu_configuration.memory is not None:
            self.default_gpu_type_memory[gpu_configuration.gpu_type] = gpu_configuration.memory
        if gpu_configuration.memory_per_gpu is not None:
            self.default_gpu_type_memory_per_gpu[gpu_configuration.gpu_type] = gpu_configuration.memory_per_gpu
        if gpu_configuration.storage is not None:
            self.default_gpu_type_storage[gpu_configuration.gpu_type] = gpu_configuration.storage
        if gpu_configuration.storage_per_gpu is not None:
            self.default_gpu_type_storage_per_gpu[gpu_configuration.gpu_type] = gpu_configuration.storage_per_gpu
        if gpu_configuration.multinode_rdma_roce is not None:
            self.default_gpu_type_multinode_rdma_roce[
                gpu_configuration.gpu_type] = gpu_configuration.multinode_rdma_roce

    def get_instance_type(
        self,
        gpu_type: GPUType,
        gpu_num: int,
        cpus: Optional[int] = None,
    ) -> InstanceType:
        instance_type = super().get_instance_type(gpu_type, gpu_num, cpus)
        if gpu_type == GPUType.NONE and cpus:
            instance_type.resource_requirements.cpus = cpus
        self.fill_instance_type_resources(instance_type)
        return instance_type

    def fill_instance_type_resources(
        self,
        instance_type: InstanceType,
    ) -> None:
        rr = instance_type.resource_requirements

        if instance_type.gpu_num > 0:
            rr.gpus = min(instance_type.gpu_num, instance_type.local_world_size)

        if instance_type.gpu_type == GPUType.NONE:
            # If min CPU amount has been set, keep that required amount
            min_cpus = self.MIN_CPU
            if rr.cpus != 0:
                min_cpus = rr.cpus
            rr.cpus = self.MAX_CPU - self.safety_margin_cpu
            rr.request_cpus = min_cpus

        # GPU Type Overrides
        if instance_type.gpu_type in self.default_gpu_type_cpus:
            rr.cpus = self.default_gpu_type_cpus[instance_type.gpu_type] - self.safety_margin_cpu
        if instance_type.gpu_type in self.default_gpu_type_memory:
            rr.memory = int(self.default_gpu_type_memory[instance_type.gpu_type] * (1 - self.safety_margin_memory))
        if instance_type.gpu_type in self.default_gpu_type_storage:
            rr.ephemeral_storage = int(self.default_gpu_type_storage[instance_type.gpu_type] *
                                       (1 - self.safety_margin_storage))

        # Per GPU Overrides
        if instance_type.gpu_type in self.default_gpu_type_cpus_per_gpu:
            rr.request_cpus = self.default_gpu_type_cpus_per_gpu[
                instance_type.gpu_type] * instance_type.local_world_size - self.safety_margin_cpu
        if instance_type.gpu_type in self.default_gpu_type_memory_per_gpu:
            rr.memory = int(self.default_gpu_type_memory_per_gpu[instance_type.gpu_type] *
                            instance_type.local_world_size * (1 - self.safety_margin_memory))
        if instance_type.gpu_type in self.default_gpu_type_storage_per_gpu:
            rr.ephemeral_storage = int(self.default_gpu_type_storage_per_gpu[instance_type.gpu_type] *
                                       instance_type.local_world_size * (1 - self.safety_margin_storage))
        instance_type.selectors = self.get_instance_selectors(instance_type)

        # Multinode Overrides
        if (instance_type.gpu_num > 0) and (instance_type.gpu_num > instance_type.local_world_size
                                           ) and instance_type.gpu_type in self.default_gpu_type_multinode_rdma_roce:
            rr.rdma_roce = self.default_gpu_type_multinode_rdma_roce[instance_type.gpu_type]

    def get_instance_selectors(
        self,
        instance_type: InstanceType,
    ) -> Dict[str, str]:
        selectors: Dict[str, str] = {}

        if instance_type.gpu_type in self.default_gpu_type_selector:
            selectors.update(self.default_gpu_type_selector[instance_type.gpu_type])

        if instance_type.gpu_num in self.default_gpu_num_selector:
            selectors.update(self.default_gpu_num_selector[instance_type.gpu_num])
        return selectors
