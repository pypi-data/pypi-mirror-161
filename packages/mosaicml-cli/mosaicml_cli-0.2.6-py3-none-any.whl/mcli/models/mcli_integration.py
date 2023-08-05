""" Implements MCLI Integrations """
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Type

import yaml
from rich.status import Status

from mcli.serverside.job.mcli_k8s_job import MCLIK8sJob
from mcli.utils.utils_serializable_dataclass import SerializableDataclass, T_SerializableDataclass
from mcli.utils.utils_types import CommonEnum


class IntegrationType(CommonEnum):
    """ Enum for Types of Setup Items Allowed """
    wandb = 'wandb'
    git_repo = 'git_repo'
    apt_packages = 'apt_packages'
    pip_packages = 'pip_packages'
    local = 'local'


@dataclass
class MCLIIntegration(SerializableDataclass, ABC):
    """
    The Base Integration Class for MCLI SetupItems

    SetupItems can not nest other SerializableDataclass objects
    """

    integration_type: IntegrationType

    @abstractmethod
    def add_to_job(self, kubernetes_job: MCLIK8sJob) -> bool:
        """Add a integration to a job
        """

    def build_to_docker(self, image: str, status: Optional[Status] = None) -> None:
        """Add integration to docker image
        """
        raise NotImplementedError()

    @classmethod
    def from_dict(cls: Type[T_SerializableDataclass], data: Dict[str, Any]) -> T_SerializableDataclass:
        # Make a copy to avoid mutating the original run input
        integration_data = data.copy()
        integration_type = integration_data.get('integration_type', None)

        if not integration_type:
            raise ValueError(f'No `integration_type` found for integration with data: \n{yaml.dump(integration_data)}')

        integration_type: IntegrationType = IntegrationType.ensure_enum(integration_type)
        integration_data['integration_type'] = integration_type

        # pylint: disable-next=import-outside-toplevel
        from mcli.objects.integrations import (MCLIAptPackagesIntegration, MCLIGitRepoIntegration, MCLILocalIntegration,
                                               MCLIPipPackagesIntegration, MCLIWandBIntegration)
        integration: Optional[MCLIIntegration] = None
        if integration_type == IntegrationType.wandb:
            integration = MCLIWandBIntegration(**integration_data)
        elif integration_type == IntegrationType.git_repo:
            integration = MCLIGitRepoIntegration(**integration_data)
        elif integration_type == IntegrationType.apt_packages:
            integration = MCLIAptPackagesIntegration(**integration_data)
        elif integration_type == IntegrationType.pip_packages:
            integration = MCLIPipPackagesIntegration(**integration_data)
        elif integration_type == IntegrationType.local:
            integration = MCLILocalIntegration(**integration_data)
        else:
            raise NotImplementedError(f'Setup Item of type: { integration_type } not supported yet')
        assert isinstance(integration, MCLIIntegration)

        return integration  # type: ignore

    def __str__(self) -> str:
        data = asdict(self)
        del data['integration_type']
        return f'Integration: {self.integration_type.value}' + f'\n{ yaml.dump( data ) }'
