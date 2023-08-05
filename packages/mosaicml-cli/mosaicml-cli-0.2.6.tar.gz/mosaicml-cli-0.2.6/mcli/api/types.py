""" GraphQL Helper Objects """
from enum import Enum
from typing import NamedTuple

GraphQLVariableName = str
GraphQLVariableDataName = str


class GraphQLVariableType(Enum):
    STRING_REQUIRED = 'String!'
    STRING_OPTIONAL = 'String'
    CREATE_PROJECT_INPUT = 'CreateProjectInput!'
    UPDATE_PROJECT_INPUT = 'UpdateProjectInput!'
    CREATE_RUN_INPUT = 'CreateRunInput!'
    GET_RUNS_INPUT = 'GetRunsInput!'


class GraphQLQueryVariable(NamedTuple):
    variableName: GraphQLVariableName
    variableDataName: GraphQLVariableDataName
    variableType: GraphQLVariableType
