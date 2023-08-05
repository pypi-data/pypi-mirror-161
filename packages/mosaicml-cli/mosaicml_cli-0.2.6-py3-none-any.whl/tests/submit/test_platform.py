""" Test Platform """
from typing import Tuple

import pytest

from mcli.models.mcli_platform import MCLIPlatform
from mcli.serverside.job.mcli_k8s_job import MCLIK8sJob
from mcli.serverside.platforms.instance_type import InstanceType
from mcli.serverside.platforms.platform import GenericK8sPlatform, InvalidPriorityError, PriorityLabel


@pytest.fixture
def mcli_job():
    job = MCLIK8sJob.empty('test')
    job.container.image = 'alpine'
    job.container.command = ['sleep', 'infinity']
    return job


@pytest.fixture(autouse=True)
def fake_secrets(mocker):
    from mcli.serverside.platforms import platform
    mocker.patch.object(platform.SecretManager, 'add_secrets_to_job', return_val=None)


def test_priority_label_ensure_enum():

    assert PriorityLabel.ensure_enum(PriorityLabel.low).name == "low"
    assert PriorityLabel.ensure_enum("low").name == "low"

    with pytest.raises(ValueError):
        PriorityLabel.ensure_enum(12345)  # type: ignore

    with pytest.raises(ValueError):
        PriorityLabel.ensure_enum("safasdfasdz")


def get_platform_and_instance(platform_name: str) -> Tuple[GenericK8sPlatform, InstanceType]:
    # Get k8s platform
    mcli_platform = MCLIPlatform(platform_name, platform_name, 'test')
    k8s_platform = GenericK8sPlatform.from_mcli_platform(mcli_platform)

    # Get instance type
    gpu_type, gpu_nums = list(k8s_platform.allowed_instances.available_instances.items())[0]
    first_instance = k8s_platform.allowed_instances.get_instance_type(gpu_type, gpu_nums[0])

    return k8s_platform, first_instance


@pytest.mark.parametrize('priority_name', ('scavenge', 'standard', 'emergency'))
def test_get_specs_priority(
    mcli_job: MCLIK8sJob,
    priority_name: str,
):
    """Test that r1z1 platform priorities get set properly within the resulting job spec

    Args:
        mcli_job: Simple MCLIK8sJob
        priority_name (str): Priority class name
    """
    # Get r1z1 platform and instance
    k8s_platform, instance_type = get_platform_and_instance('r1z1')

    # Get specs with priority_class
    k8s_platform.prepare_kubernetes_job_for_platform(
        kubernetes_job=mcli_job,
        instance_type=instance_type,
        priority_class=priority_name,
    )

    # Validate correct priority class
    assert mcli_job.pod_spec.priority_class_name == k8s_platform.priority_class_labels[priority_name]


def test_get_specs_priority_default(mcli_job: MCLIK8sJob):
    """Test that r1z1 platform priorities properly handle a priority of None as default

    Args:
        mcli_job: Simple MCLIK8sJob
    """
    # Get r1z1 platform and instance
    k8s_platform, instance_type = get_platform_and_instance('r1z1')

    # Get specs with priority_class
    k8s_platform.prepare_kubernetes_job_for_platform(
        kubernetes_job=mcli_job,
        instance_type=instance_type,
        priority_class=None,
    )

    # Validate correct priority class
    assert k8s_platform.default_priority_class is not None
    default_priority = k8s_platform.priority_class_labels[k8s_platform.default_priority_class]
    assert mcli_job.pod_spec.priority_class_name == default_priority


@pytest.mark.parametrize('platform_name', ('aws-research-01', 'gcp-research-01'))
def test_get_specs_priority_none(
    mcli_job: MCLIK8sJob,
    platform_name: str,
):
    """Test that a few platforms priorities properly handle a priority of None

    Args:
        mcli_job: Simple MCLIK8sJob
        platform_name (str): Name of the platform
    """
    # Get platform and instance
    k8s_platform, instance_type = get_platform_and_instance(platform_name)

    # Get specs with priority_class
    k8s_platform.prepare_kubernetes_job_for_platform(
        kubernetes_job=mcli_job,
        instance_type=instance_type,
        priority_class=None,
    )

    # Validate correct priority class
    assert mcli_job.pod_spec.priority_class_name == None


@pytest.mark.parametrize('platform_name', ('aws-research-01', 'r1z1', 'r6z1', 'gcp-research-01'))
def test_get_specs_priority_invalid(
    mcli_job: MCLIK8sJob,
    platform_name: str,
):
    """Test that a few platforms priorities properly handle an incorrect priority name

    Args:
        mcli_job: Simple MCLIK8sJob
        platform_name (str): Name of the platform
    """
    # Get platform and instance
    k8s_platform, instance_type = get_platform_and_instance(platform_name)

    # Raises InvalidPriorityError
    with pytest.raises(InvalidPriorityError):
        k8s_platform.prepare_kubernetes_job_for_platform(
            kubernetes_job=mcli_job,
            instance_type=instance_type,
            priority_class='not-a-real-priority',
        )
