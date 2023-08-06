# from .gstorm import mainClass
from . import cli
from . import helpers
from .BaseGraphQLType import BaseGraphQLType
from .GraphQLType import GraphQLType
from .QueryBuilder import QueryBuilder
from .MutationBuilder import MutationBuilder
from._mutation_runners import (
    create,
    save_multi_create
)

# * Package name:
name = 'gstorm'
# * required here for pypi upload exceptions:
__version__ = "0.7.0"
