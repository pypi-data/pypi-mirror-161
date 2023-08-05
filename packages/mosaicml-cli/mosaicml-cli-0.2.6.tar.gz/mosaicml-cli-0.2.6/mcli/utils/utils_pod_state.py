"""Utilities for interpreting pod status"""
from __future__ import annotations

import functools
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar

from kubernetes import client

from mcli.utils.utils_kube import deserialize


@functools.total_ordering
class PodState(Enum):
    """Enum for possible pod states
    """
    PENDING = 'PENDING'
    SCHEDULED = 'SCHEDULED'
    QUEUED = 'QUEUED'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED_PULL = 'FAILED_PULL'
    FAILED = 'FAILED'
    TERMINATING = 'TERMINATING'
    UNKNOWN = 'UNKNOWN'

    @property
    def order(self) -> List[PodState]:
        """Order of pod states, from latest to earliest
        """
        return [
            PodState.TERMINATING,
            PodState.FAILED,
            PodState.FAILED_PULL,
            PodState.COMPLETED,
            PodState.RUNNING,
            PodState.STARTING,
            PodState.SCHEDULED,
            PodState.QUEUED,
            PodState.PENDING,
            PodState.UNKNOWN,
        ]

    def __lt__(self, other: PodState):
        if not isinstance(other, PodState):
            raise TypeError(f'Cannot compare order of ``PodState`` and {type(other)}')
        return self.order.index(self) > self.order.index(other)

    def before(self, other: PodState, inclusive: bool = False) -> bool:
        """Returns True if this state usually comes "before" the other

        Args:
            other: Another PodState
            inclusive: If True, == evaluates to True. Default False.

        Returns:
            True of this state is "before" the other

        Examples:
        > PodState.RUNNING.before(PodState.COMPLETED)
        True

        > PodState.PENDING.before(PodState.RUNNING)
        True
        """
        return (self < other) or (inclusive and self == other)

    def after(self, other: PodState, inclusive: bool = False) -> bool:
        """Returns True if this state usually comes "after" the other

        Args:
            other: Another PodState
            inclusive: If True, == evaluates to True. Default False.

        Returns:
            True of this state is "after" the other

        Examples:
        > PodState.RUNNING.before(PodState.COMPLETED)
        True

        > PodState.PENDING.before(PodState.RUNNING)
        True
        """
        return (self > other) or (inclusive and self == other)


StatusType = TypeVar('StatusType')  # pylint: disable=invalid-name


@dataclass
class PodStatus():
    """Base pod status detector
    """
    state: PodState
    message: str = ''
    reason: str = ''

    @classmethod
    def from_pod_dict(cls: Type[PodStatus], pod_dict: Dict[str, Any]) -> PodStatus:
        """Get the status of a pod from its dictionary representation

        This is useful if the pod has already been converted to a JSON representation

        Args:
            pod_dict: Dictionary representation of a V1Pod object

        Returns:
            PodStatus instance
        """
        if 'status' not in pod_dict:
            raise KeyError('pod_dict must have a valid "status" key')
        pod = deserialize(pod_dict, 'V1Pod')
        return cls.from_pod(pod)

    @classmethod
    def _pending_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:

        # Scheduled or queuing
        conditions = pod.status.conditions if pod.status.conditions else []
        if conditions:
            scheduled_condition = [c for c in conditions if c.type == 'PodScheduled'][0]
            if scheduled_condition.status == 'True' and len(conditions) == 1:
                return PodStatus(state=PodState.SCHEDULED)
            elif scheduled_condition.status == 'False' and scheduled_condition.reason == 'Unschedulable':
                return PodStatus(state=PodState.QUEUED)

        # Attempting to start container
        container_statuses = pod.status.container_statuses if pod.status.container_statuses else []
        if container_statuses:
            waiting = container_statuses[0].state.waiting
            if waiting and 'ContainerCreating' in waiting.reason:
                return PodStatus(state=PodState.STARTING)
            elif waiting and waiting.reason in {'ErrImagePull', 'ImagePullBackOff'}:
                return PodStatus(state=PodState.FAILED_PULL)

        # Else generic pending
        return PodStatus(state=PodState.PENDING)

    @classmethod
    def _running_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=PodState.RUNNING)

    @classmethod
    def _completed_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=PodState.COMPLETED)

    @classmethod
    def _failed_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=PodState.FAILED)

    @classmethod
    def _unknown_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=PodState.UNKNOWN)

    @classmethod
    def from_pod(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        """Get the appropriate PodStatus instance from a Kubernetes V1PodStatus object

        The resulting PodStatus instance contains parsed information about the current state of the pod

        Args:
            status: Valid V1PodStatus object

        Returns:
            PodStatus instance
        """

        if getattr(pod.metadata, 'deletion_timestamp', None) is not None:
            return PodStatus(state=PodState.TERMINATING)

        if pod.status.phase == 'Pending':
            return cls._pending_phase_match(pod)
        elif pod.status.phase == 'Running':
            return cls._running_phase_match(pod)
        elif pod.status.phase == 'Succeeded':
            return cls._completed_phase_match(pod)
        elif pod.status.phase == 'Failed':
            return cls._failed_phase_match(pod)
        else:
            return cls._unknown_phase_match(pod)
