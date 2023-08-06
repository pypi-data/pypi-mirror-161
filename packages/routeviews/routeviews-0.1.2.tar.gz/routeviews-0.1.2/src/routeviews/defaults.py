import dataclasses


def empty_list():
    """Dataclass field definition. 

    Shorthand for 'default to an empty list' for dataclass attribute(s).

    Returns:
        dataclasses.field: A dataclass field that will default to empty list.
    """
    return dataclasses.field(default_factory=list)
