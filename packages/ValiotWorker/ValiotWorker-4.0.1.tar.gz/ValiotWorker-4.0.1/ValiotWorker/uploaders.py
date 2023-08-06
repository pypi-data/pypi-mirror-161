from pygqlc import GraphQLClient
from . import mutations
gql = GraphQLClient()


def update_job(variables):
    return gql.mutate(mutation=mutations.update_job, variables=variables)
