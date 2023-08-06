from __future__ import annotations

from itertools import product
from typing import List, Dict, Tuple

from fuzzywuzzy import fuzz

from bigeye_sdk.functions.table_functions import get_table_column_id
from bigeye_sdk.generated.com.torodata.models.generated import ComparisonColumnMapping, ColumnApplicableMetricTypes, \
    TableApplicableMetricTypes, IdAndDisplayName, Table, ComparisonTableInfo
from bigeye_sdk.model.protobuf_message_facade import SimpleColumnMapping


def build_ccm(scm: SimpleColumnMapping, source_table: Table, target_table: Table) -> ComparisonColumnMapping:
    cm = ComparisonColumnMapping()
    cm.source_column = IdAndDisplayName(id=get_table_column_id(source_table, scm.source_column_name),
                                        display_name=scm.source_column_name)
    cm.target_column = IdAndDisplayName(id=get_table_column_id(target_table, scm.target_column_name),
                                        display_name=scm.target_column_name)
    cm.metrics = [m.to_datawatch_object() for m in scm.metrics]
    return cm


def infer_column_mappings(source_metric_types: TableApplicableMetricTypes,
                          target_metric_types: TableApplicableMetricTypes) -> List[ComparisonColumnMapping]:
    # TODO add fuzzy matching here too.
    """
    Used to infer column mappings, based on TableApplicableMetricTypes.

    :param source_metric_types: The TableApplicableMetricTypes of the source table
    :param target_metric_types: The TableApplicableMetricTypes of the target table

    :returns: List[ComparisonColumnMapping]

    >>> infer_column_mappings(source_metric_types=smt, target_metric_types=tmt)
    [ComparisonColumnMapping(source_column=IdAndDisplayName(id=29128800, display_name='id'), target_column=IdAndDisplayName(id=29128800, display_name='id'), metrics=[MetricType(predefined_metric=PredefinedMetric(metric_name=<PredefinedMetricName.COUNT_NULL: 2>), template_metric=TemplateMetric(template_id=0, aggregation_type=0, template_name=''), is_metadata_metric=False, is_table_metric=False)], user_defined=False)]
    """
    sct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower().replace('_', ''): i
        for i in source_metric_types.applicable_metric_types
    }

    tct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower().replace('_', ''): i
        for i in target_metric_types.applicable_metric_types
    }

    column_mappings: List[ComparisonColumnMapping] = [
        ComparisonColumnMapping(source_column=sct[k].column, target_column=tct[k].column,
                                metrics=sct[k].applicable_metric_types)
        for k in sct.keys() if k in tct
        if sct[k].applicable_metric_types == tct[k].applicable_metric_types
    ]

    return column_mappings


def _fuzzy_match(strings1: List[str], strings2: List[str],
                 min_match_score: int) -> List[Tuple[str, str]]:
    carteasien = set(product(set(strings1), set(strings2)))
    l: List[Tuple[str, str]] = []

    for i in carteasien:
        r = fuzz.token_set_ratio(i[0], i[1])
        if r >= min_match_score:
            l.append(i)

    return l


def match_tables_by_name(source_tables: List[Table], target_tables: List[Table]) -> Dict[str, Tuple[int, int]]:
    """
    Creates a dictionary of table ids keyed by a delta name
    :param source_tables: list of source Table objects
    :param target_tables: list of target Table objects
    :return: Dict[delta_name:str, Tuple[source_table_id, target_table_id]
    """
    sourced: Dict[str, Table] = {t.name: t for t in target_tables}
    targetd: Dict[str, Table] = {t.name: t for t in source_tables}

    # TODO match columns too.
    matched = _fuzzy_match(sourced.keys(), targetd.keys(), 96)

    r: Dict[str, Tuple[int, int]] = {}

    for m in matched:
        st: Table = sourced[m[0]]
        tt: Table = targetd[m[1]]
        k = f"(suggested_delta) {st.schema_name}.{st.name} -> {tt.schema_name}.{tt.name}"
        r[k] = st.id, tt.id

    return r


if __name__ == "__main__":
    import doctest

    globs = locals()
    template = {
        "id": 1883035,
        "applicableMetricTypes": [
            {
                "column": {
                    "id": 29128800,
                    "displayName": "id"
                },
                "applicableMetricTypes": [
                    {
                        "predefinedMetric": {
                            "metricName": "COUNT_NULL"
                        },
                        "isMetadataMetric": False,
                        "isTableMetric": False
                    }
                ]
            }
        ]
    }
    globs['smt'] = TableApplicableMetricTypes().from_dict(template)
    globs['tmt'] = TableApplicableMetricTypes().from_dict(template)

    doctest.testmod(globs=globs)
