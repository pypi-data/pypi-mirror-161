def has_either_ids_or_names(id: int = None, name: str = None) -> bool:
    return id is not None or name is not None