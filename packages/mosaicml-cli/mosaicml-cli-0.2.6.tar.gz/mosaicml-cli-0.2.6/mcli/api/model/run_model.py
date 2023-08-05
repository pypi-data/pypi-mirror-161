""" GraphQL representation of MCLIJob"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from mcli.api.engine.utils import dedent_indent
from mcli.api.schema.generic_model import DeserializableModel
from mcli.models.run_input import RunInput
from mcli.utils.utils_pod_state import PodState


@dataclass
class RunModel(DeserializableModel):
    """The GraphQL Serializable and Deserializable representation of a Run

    The intermediate form includes both the RunInput and MCLIJob as a bjson value
    """

    run_uid: str
    run_name: str
    run_status: PodState
    created_at: datetime
    updated_at: datetime
    run_input: RunInput
    job_config: dict

    property_translations = {
        'runUid': 'run_uid',
        'runName': 'run_name',
        'runStatus': 'run_status',
        'createdAt': 'created_at',
        'updatedAt': 'updated_at',
        'runInput': 'run_input',
        'jobConfig': 'job_config',
    }


def get_run_schema(indentation: int = 2,):
    """ Get the GraphQL schema for a :type RunModel:
    Args:
        indentation (int): Optional[int] for the indentation of the block
    Returns:
        Returns a GraphQL string with all the fields needed to initialize a
        :type RunModel:
    """
    return dedent_indent("""
runUid
runName
runInput
runStatus
createdAt
updatedAt
jobConfig
        """, indentation)
