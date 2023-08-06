import attr


@attr.s
class GraphQLEnum():
    """Wraps an enumeration string to identify it as an enum
    May be needed to identify string literals as enums in GraphQLBuilder.
    Example:
    "L101" -> str
    "INSERTED_AT" -> Enum
    "SUCCESS" -> Enum
    "Gobierno" -> str
    etc
    """
    value: str = attr.ib()
