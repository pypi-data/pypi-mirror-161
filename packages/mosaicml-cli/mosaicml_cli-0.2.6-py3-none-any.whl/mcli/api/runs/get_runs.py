""" Get runs """
from typing import List, Optional

from mcli.api.engine.engine import run_graphql_success_query
from mcli.api.model.run_model import RunModel, get_run_schema
from mcli.api.schema.query import named_success_query
from mcli.api.schema.query_models import SuccessResponse
from mcli.api.types import GraphQLQueryVariable, GraphQLVariableType


def get_runs(run_names: Optional[List[str]] = None, include_deleted: bool = False) -> SuccessResponse[RunModel]:
    """Runs a GraphQL query to get all runs for the authenticated user.

    Args:
        run_names (List[str], optional): The list of run names to get. If not provided then
            all non-deleted runs for the user are returned.
        include_deleted (bool): ``True`` to include deleted runs ``False``
            to not include deleted runs.

    Returns:
        SuccessResponse[RunModel]: The GraphQL response containing the runs.
    """
    query_function = 'getRuns'
    variable_data_name = '$getRunsInput'
    variables = {
        variable_data_name: {
            'runNames': run_names,
            'includeDeleted': include_deleted,
        },
    }
    graphql_variable: GraphQLQueryVariable = GraphQLQueryVariable(
        variableName='getRunsData',
        variableDataName=variable_data_name,
        variableType=GraphQLVariableType.GET_RUNS_INPUT,
    )

    query = named_success_query(
        query_name='GetRuns',
        query_function=query_function,
        query_items=get_run_schema(),
        variables=[graphql_variable],
        is_mutation=False,
    )

    response = run_graphql_success_query(
        query=query,
        queryFunction=query_function,
        return_model_type=RunModel,
        variables=variables,
    )

    return response
