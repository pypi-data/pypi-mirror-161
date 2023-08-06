import os
from pygqlc import GraphQLClient


def setup_gql(env_name=None):
    env = env_name or os.environ.get('ENV')
    gql = GraphQLClient()
    gql.addEnvironment(
        'dev',
        url=os.environ.get('API_DEV'),
        wss=os.environ.get('WSS_DEV'),
        headers={'Authorization': os.environ.get('TOKEN_DEV')})
    gql.addEnvironment(
        'prod',
        url=os.environ.get('API'),
        wss=os.environ.get('WSS'),
        headers={'Authorization': os.environ.get('TOKEN')})
    # ! Sets the environment selected in the .env file
    gql.setEnvironment(env)
    return gql
