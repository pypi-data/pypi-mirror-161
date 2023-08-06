from typing import List, Tuple, Dict

from bigeye_sdk.generated.com.torodata.models.generated import Schema


def create_schema_id_pairs(source_schema_dict: Dict[str, Schema], target_schema_dict: Dict[str, Schema],
                           schema_name_pairs: List[Tuple[str, str]]) -> List[Tuple[int, int]]:
    """
    Matches id pairs based on schema name pairs.
    :param source_schema_dict: Dict[schema_name:str, Schema]
    :param target_schema_dict: Dict[schema_name:str, Schema]
    :param schema_name_pairs: paired names of schemas (source_schema_name, target_schema_name)
    :return: List[source_schema_id, target_schema_id]
    """

    return [(source_schema_dict[pair[0]].id, target_schema_dict[pair[1]].id) for pair in schema_name_pairs]
