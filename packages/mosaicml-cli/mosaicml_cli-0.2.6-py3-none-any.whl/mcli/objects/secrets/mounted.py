""" MCLI Mounted Secret """
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Type

from kubernetes import client

from mcli.models import MCLIGenericSecret, SecretType
from mcli.models.mcli_secret import SECRET_MOUNT_PATH_PARENT
from mcli.serverside.job.mcli_k8s_job import MCLIK8sJob, MCLIVolume


def name_as_key(name: str) -> str:
    """Convert the secret name to a valid environment variable

    Args:
        name: Secret name

    Returns:
        Environment variable key
    """

    suffix = name.replace('-', '_').upper()
    return f'SECRET_PATH_{suffix}'


@dataclass
class MCLIMountedSecret(MCLIGenericSecret):
    """Secret class for generic secrets that will be mounted to run pods as files
    """
    mount_path: Optional[str] = None

    def __post_init__(self):
        if self.mount_path is None:
            self.mount_path = str(SECRET_MOUNT_PATH_PARENT / self.name)

    @property
    def required_packing_fields(self) -> Set[str]:
        return set(self.disk_skipped_fields + ['mount_path'])

    @property
    def additional_volume_sources(self) -> List[client.V1KeyToPath]:
        return []

    @classmethod
    def from_generic_secret(
        cls: Type[MCLIMountedSecret],
        generic_secret: MCLIGenericSecret,
        mount_path: Optional[str] = None,
    ) -> MCLIMountedSecret:
        return cls(
            name=generic_secret.name,
            value=generic_secret.value,
            secret_type=SecretType.mounted,
            mount_path=mount_path,
        )

    def add_to_job(self, kubernetes_job: MCLIK8sJob, permissions: int = 420) -> bool:
        assert self.mount_path is not None
        path = Path(self.mount_path)
        secret_volume = client.V1Volume(
            name=self.name,
            secret=client.V1SecretVolumeSource(
                secret_name=self.name,
                items=[client.V1KeyToPath(key='value', path='secret')] + self.additional_volume_sources,
                default_mode=permissions,
            ),
        )
        secret_mount = client.V1VolumeMount(
            name=self.name,
            mount_path=self.mount_path,
            read_only=True,
        )

        mcli_volume = MCLIVolume(volume=secret_volume, volume_mount=secret_mount)
        kubernetes_job.add_volume(volume=mcli_volume)

        mount_path_env = client.V1EnvVar(
            name=name_as_key(self.name),
            value=str(path / 'secret'),
        )
        kubernetes_job.add_env_var(mount_path_env)

        return True
