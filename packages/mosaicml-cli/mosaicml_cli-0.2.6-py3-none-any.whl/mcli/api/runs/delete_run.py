""" Delete a run. """
from typing import List, Optional

from mcli.api.engine.engine import run_graphql_success_query
from mcli.api.model.run_model import RunModel, get_run_schema
from mcli.api.schema.query import named_success_query
from mcli.api.schema.query_models import SuccessResponse
from mcli.api.types import GraphQLQueryVariable, GraphQLVariableType


def delete_run(run_names: Optional[List[str]] = None) -> SuccessResponse[RunModel]:
    """Runs a GraphQL query to delete one or more runs.

    Args:
        run_names (List[str], optional): The names of the runs to delete. If not provided then all
            runs are deleted.

    Returns:
        SuccessResponse[RunModel]: The GraphQL response for deleted runs.
    """

    query_function = 'deleteRun'
    get_variable_data_name = '$getRunsInput'
    variables = {get_variable_data_name: {'runNames': run_names}}

    get_graphql_variable: GraphQLQueryVariable = GraphQLQueryVariable(
        variableName='getRunsData',
        variableDataName=get_variable_data_name,
        variableType=GraphQLVariableType.GET_RUNS_INPUT,
    )

    query = named_success_query(
        query_name='DeleteRun',
        query_function=query_function,
        query_item=get_run_schema(),
        variables=[get_graphql_variable],
        is_mutation=True,
    )

    response = run_graphql_success_query(
        query=query,
        queryFunction=query_function,
        return_model_type=RunModel,
        variables=variables,
    )
    return response
