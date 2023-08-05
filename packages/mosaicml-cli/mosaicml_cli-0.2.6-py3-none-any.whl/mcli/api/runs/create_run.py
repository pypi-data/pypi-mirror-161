""" Create a Run """
from mcli.api.engine.engine import run_graphql_success_query
from mcli.api.model.run_model import RunModel, get_run_schema
from mcli.api.schema.query import named_success_query
from mcli.api.schema.query_models import SuccessResponse
from mcli.api.types import GraphQLQueryVariable, GraphQLVariableType
from mcli.models.run_input import RunInput


def create_run(run: RunInput,) -> SuccessResponse[RunModel]:
    """Runs a GraphQL query to create a new run from a RunInput

    Args:
        run (RunInput): The :type RunInput: to persist

    Returns:
        SuccessResponse[RunModel]: The GraphQL response containing the created run.
    """
    query_function = 'createRun'
    variable_data_name = '$createRunInput'
    variables = {
        variable_data_name: run.to_create_run_api_input(),
    }
    graphql_variable: GraphQLQueryVariable = GraphQLQueryVariable(
        variableName='createRunData',
        variableDataName=variable_data_name,
        variableType=GraphQLVariableType.CREATE_RUN_INPUT,
    )

    query = named_success_query(
        query_name='CreateRun',
        query_function=query_function,
        query_item=get_run_schema(),
        variables=[graphql_variable],
        is_mutation=True,
    )

    response = run_graphql_success_query(
        query=query,
        queryFunction=query_function,
        return_model_type=RunModel,
        variables=variables,
    )

    return response
