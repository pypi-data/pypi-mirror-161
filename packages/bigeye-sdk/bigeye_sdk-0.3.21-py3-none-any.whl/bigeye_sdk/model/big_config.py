from __future__ import annotations

from typing import List, Optional, Dict, Tuple, Any

from bigeye_sdk.exceptions.exceptions import TagNotExistsException, NoColumnSelectorsDefinedException, \
    DuplicateIDExistsException, InvalidMetricDefinitionException, SavedMetricIdNotExistsException, \
    InvalidConfigurationException
from bigeye_sdk.functions.search_functions import search
from bigeye_sdk.generated.com.torodata.models.generated import Source, CohortAndMetricDefinition, CohortDefinition, \
    MetricSuite
from bigeye_sdk.log import get_logger
from pydantic import Field, PrivateAttr
from pydantic_yaml import YamlModel

from bigeye_sdk.model.protobuf_message_facade import SimpleMetricDefinition, SimpleNotificationChannel
from bigeye_sdk.serializable import File

log = get_logger(__file__)


def _explode_fq_name(fq_name: str) -> List[str]:
    """
    Explodes a fully qualifeid name into a list of names.  Supports wild cards as *. Supports single and double quoted
    names containing periods.
        Example: wh."my.database".table.column resolves to ['wh', 'my.database', table, column]
    Args:
        fq_name: fully qualified asset name.

    Returns: list of names from the fully qualified name.
    """
    import re
    splt_unquoted_period_pattern = re.compile(r'''((?:[^."']|"[^"]*"|'[^']*')+)''')
    remove_quotes_pattern = re.compile(r"\"|'")
    r = [remove_quotes_pattern.sub('', i) for i in splt_unquoted_period_pattern.split(fq_name)[1::2]]

    return r


class ColumnSelector(YamlModel):
    name: str

    # types: List[SimpleFieldType] TODO V1

    def __post_init__(self):
        ## TODO: define rule for validating column_selectors
        pass

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, ColumnSelector):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.name == other.name


class TagDefinition(YamlModel):
    tag_id: str
    column_selectors: List[ColumnSelector]

    def __hash__(self):
        return hash((repr(self.tag_id), self.column_selectors))


# @dataclass
# class SavedMetricCollection:
#     collection_name: str
#     saved_metric_ids: List[str]


class SavedMetricDefinitions(YamlModel):
    # metric_collections: SavedMetricCollection
    metrics: List[SimpleMetricDefinition]

    def __post_init__(self):
        ## TODO: define rule for validating that every saved SimpleMetricDefinition has a `saved_metric_id`
        ## TODO: V1 define rule for validating that every saved MetricCollection `saved_metric_id` references a saved_metric in the saved Metrics section.
        pass


class RowCreationTimes(YamlModel):
    tag_ids: Optional[List[str]] = Field(default_factory=lambda: [])
    column_selectors: Optional[List[ColumnSelector]] = Field(default_factory=lambda: [])


class TagDeployment(YamlModel):
    metrics: List[SimpleMetricDefinition]
    tag_id: Optional[str] = None
    column_selectors: Optional[List[ColumnSelector]] = Field(default_factory=lambda: [])

    def explode_fq_column_selectors(self) -> List[List[str]]:
        """
        Explodes a fully qualifeid column selectors into a list of names.  Supports wild cards as *. Supports single and
        double quoted  names containing periods.  Supports fully qulified names with either source.database.schema or
        source.schema convention.

            Example: wh."my.*".some_*_table.* resolves to ['wh', 'my.*', 'some_*_table', '*']

        Returns: list of names from each fully qualified column selector in the Tag Deployment
        """
        return [self._explode_fq_column_selectors(i.name) for i in self.column_selectors]

    @staticmethod
    def _explode_fq_column_selectors(fq_column_selector: str) -> List[str]:

        names = _explode_fq_name(fq_column_selector)

        if len(names) == 5:
            """Accommodates source types that have a source/instance, database, and schema in the fully 
            qualified name"""
            names[1:3] = ['.'.join(names[1:3])]
            return names
        elif len(names) == 4:
            """Accommodates source types that have a source/instance/database and schema in the fully qualified
            name"""
            return names
        else:
            """Other patterns not currently supported."""
            raise InvalidConfigurationException(f"Fully qualified column selectors must resolve to a column.  Names "
                                                f"must have either 3 elements or 4 elements.  For example: "
                                                f"source.schema.table.column OR "
                                                f"source.database.schema.table.column.  Wild cards are accepted.  "
                                                f"The fully qualified name given is {fq_column_selector}")

    def to_cohort_and_metric_def(self, sources: Dict[str, Source]) -> Dict[int, List[CohortAndMetricDefinition]]:
        """
        Builds a Cohort and MetricDefinition from a TagDeployment object
        Args:
            sources: An index of Sources by Source Name.

        Returns: Dict[source_id: int, List[CohortAndMetricDefinition]] matched based on warehouse_id to consolidate to
        a single metric suite object.
        """

        cmds: Dict[int, List[CohortAndMetricDefinition]] = {}
        metrics = [m.to_datawatch_object() for m in self.metrics]

        for cs in self.explode_fq_column_selectors():
            source_pattern = cs[0]
            schema_pattern = cs[1]
            table_pattern = cs[2]
            column_pattern = cs[3]

            this_cohort = CohortDefinition(schema_name_pattern=schema_pattern, table_name_pattern=table_pattern,
                                           column_name_pattern=column_pattern)

            matching_source_ids = [source.id
                                   for source_name, source in sources.items()
                                   if source_name in search(search_string=source_pattern,
                                                            content=[source_name])
                                   ]

            for sid in matching_source_ids:
                """Tag deployments support source patterns.  Each source id becomes a key in the returned dictionary 
                with the exact same cohorts and metrics."""
                cmd = CohortAndMetricDefinition(cohorts=[this_cohort], metrics=metrics)
                if sid in cmds:
                    cmds[sid].append(cmd)
                else:
                    cmds[sid] = [cmd]

        return cmds


class TagDeploymentSuite(YamlModel):
    deployments: List[TagDeployment]
    sla_name: Optional[str] = None
    notification_channels: Optional[List[SimpleNotificationChannel]] = None


class ColumnMetricDeployment(YamlModel):
    column_name: str
    metrics: List[SimpleMetricDefinition]


class TableDeployment(YamlModel):
    fq_table_name: str
    columns: List[ColumnMetricDeployment]
    table_metrics: Optional[List[SimpleMetricDefinition]] = None
    row_creation_time: Optional[str] = None

    # TODO validate no wild cards exist in fq_table_name
    def explode_fq_table_name(self):
        """
        Explodes a fully qualifeid table name into a list of names.  Supports single and double quoted  names
        containing periods.  Supports fully qulified names with either source.database.schema or source.schema
        conventions.  DOES NOT support wild cards.

            Example: wh."my.schema".some_table resolves to ['wh', 'my.schema', 'some_table']

        Returns: list of names from the fully qualified table name
        """

        return self._explode_fq_table_name(self.fq_table_name)

    @staticmethod
    def _explode_fq_table_name(fq_table_name: str) -> List[str]:
        names = _explode_fq_name(fq_table_name)

        if len(names) == 4:
            """Accommodates source types that have a source/instance, database, and schema in the fully 
            qualified name"""
            names[1:3] = ['.'.join(names[1:3])]
            return names
        elif len(names) == 3:
            """Accommodates source types that have a source/instance/database and schema in the fully qualified
            name"""
            return names
        else:
            """Other patterns not currently supported."""
            raise InvalidConfigurationException(f"Fully qualified table names must have 3 elements or 4 elements.  For"
                                                f"example: source.schema.table OR source.database.schema.table.  "
                                                f"Wild cards are accepted.  The fully qualified name given "
                                                f"is {fq_table_name}")

    def to_cohort_and_metric_def(self, sources: Dict[str, Source]) -> Dict[int, List[CohortAndMetricDefinition]]:
        """
        Builds a Cohort and MetricDefinition from a TableDeployment object
        Args:
            sources: An index of Sources by Source Name.

        Returns: Dict[warehouse_id: int, CohortAndMetricDefinition]
        """

        result: Dict[int, List[CohortAndMetricDefinition]] = {}

        fq_names_list = self.explode_fq_table_name()
        source_name = fq_names_list[0]
        schema_name = fq_names_list[1]
        table_name = fq_names_list[2]

        if source_name in sources:
            sid = sources[source_name].id
        else:
            # TODO error to context to find containing file and line numbers
            raise InvalidConfigurationException(f"Source does not exist for Table Deployment: {self.fq_table_name}")

        cmds: List[CohortAndMetricDefinition] = []

        for c in self.columns:
            cohort = CohortDefinition(schema_name_pattern=schema_name, table_name_pattern=table_name,
                                      column_name_pattern=c.column_name)
            cmds.append(
                CohortAndMetricDefinition(cohorts=[cohort], metrics=[m.to_datawatch_object() for m in c.metrics]))

        result[sid] = cmds

        return result


class TableDeploymentSuite(YamlModel):
    deployments: List[TableDeployment]
    sla_name: Optional[str] = None
    notification_channels: Optional[List[SimpleNotificationChannel]] = None


class BigConfig(File, type='BIG_CONFIG_FILE'):
    """
    BigConfig is a canonical model used to collate and compile all definition and deployment files maintained by users
    into a single object that can be used to generate a metric suite.  Tag Definitions and Saved Metric Definitions
    are applied -- and validated -- during the __post_init__ phase of instantiating a BigConfig.
    """
    tag_definitions: Optional[List[TagDefinition]] = Field(
        default_factory=lambda: [])  # only one because we must consolidate if creating BigConfig from multiple files.
    row_creation_times: Optional[RowCreationTimes] = None
    saved_metric_definitions: Optional[
        SavedMetricDefinitions] = None  # only one because we must consolidate if creating BigConfig from multiple files.
    tag_deployments: Optional[List[TagDeploymentSuite]] = Field(default_factory=lambda: [])
    table_deployments: Optional[List[TableDeploymentSuite]] = Field(default_factory=lambda: [])

    _tag_ix_: Dict[str, List[ColumnSelector]] = PrivateAttr({})  # Dict[tag_id, List[ColumnSelector]]
    _saved_metric_ix_: Dict[str, SimpleMetricDefinition] = PrivateAttr(
        {})  # Dict[saved_metric_id, SimpleMetricDefinition]

    # _saved_metric_collection_ix_: Dict[str, List, str] = {}  # Dict[saved_metric_collection_id, List[saved_metric_id]] (V1)

    def __init__(self, **data: Any):
        super().__init__(**data)

        log.info('Applying Tags and Saved Metrics.')
        if self.tag_definitions:
            self._tag_ix_ = self._generate_tag_ix(self.tag_definitions)
            apply_result = self._apply_tags(tag_ix=self._tag_ix_, tag_deps=self.tag_deployments,
                                            row_creation_times=self.row_creation_times)
            self.tag_deployments = apply_result[0]
            self.row_creation_times = apply_result[1]
        if self.saved_metric_definitions:
            self._saved_metric_ix_ = self._generate_saved_metric_def_ix(self.saved_metric_definitions)
            apply_result = self._apply_saved_metrics(saved_metric_ix=self._saved_metric_ix_,
                                                     tag_deps=self.tag_deployments,
                                                     table_deps=self.table_deployments)
            self.tag_deployments = apply_result[0]
            self.table_deployments = apply_result[1]

        # TODO validate no saved metrics exist but tag and table deployments include metric definitions with only a saved_metric_id

    @staticmethod
    def _generate_tag_ix(tag_definitions: List[TagDefinition]) -> Dict[str, List[ColumnSelector]]:
        """
        Generates an index of Column Selectors by Tag ID and validates no duplicates exist and that column selectors
        is not empty.
        Args:
            tag_definitions: List of Tag Definitions from which an Index will be generated.

        Returns: An index of Column Selectors by Tag ID.
        """
        tix: Dict[str, List[ColumnSelector]] = {}
        for td in tag_definitions:
            if td.tag_id in tix:
                # TODO instead append duplicates to a context and report on them at the end of the process.
                DuplicateIDExistsException(f"Tag ID: {td.tag_id} is a duplicate.")
            if not td.column_selectors:
                # TODO instead  append missing column selectors to context and report on them at the end of the process.
                NoColumnSelectorsDefinedException(f"Tag ID: {td.tag_id} has no defined Column Selectors.")

            tix[td.tag_id] = td.column_selectors

        return tix

    @staticmethod
    def _generate_saved_metric_def_ix(smd: SavedMetricDefinitions) -> Dict[str, SimpleMetricDefinition]:
        """
        Generates an index of Saved Metric Definitions by Saved Metric ID and validates no duplicates exist and that
        the Metric Definitions defined have at least a `saved_metric_id` and a `metric_type`.
        Args:
            smd: a Saved Metric Definitions object from which the Saved Metric Definitions IX will be generated.

        Returns: An index of Simple Metric Definitions keyed by `saved_metric_id`.

        """
        smdix: Dict[str, SimpleMetricDefinition] = {}
        for d in smd.metrics:
            if d.saved_metric_id in smdix:
                # TODO instead append duplicate details to context and report at end of process.
                raise DuplicateIDExistsException(f"Duplicate Saved Metric ID exists: {d.saved_metric_id}")
            if not d.saved_metric_id or not d.metric_type:
                # TODO instead append erroneous metric definitions to a context and report at end of process.
                raise InvalidMetricDefinitionException(f"Saved Metric Definition needs both a Saved Metric ID and a "
                                                       f"Metric Type: {d.json()}")

            smdix[d.saved_metric_id] = d

        return smdix

    @staticmethod
    def _apply_tags(tag_ix: Dict[str, List[ColumnSelector]],
                    tag_deps: List[TagDeploymentSuite],
                    row_creation_times: RowCreationTimes) -> Tuple[List[TagDeploymentSuite], RowCreationTimes]:
        """
        Applies tags by tag id in all tag deployments and row creation times definitinos.  Validates that all tags
        called in deployments exist in the tags definitions.  Validates that column selectors exist after application.
        Args:
            tag_ix: index of column selectors keyed by tag_id
            tag_deps: list of Tag Deployment Suites to which tags will be applied.
            row_creation_times: row creation times to which tags will be applied

        Returns: list of Tag Deployment Suites to which tags have been applied.

        """

        def _valid_tag_id_in_ix(tid: str) -> bool:
            if tid not in tag_ix:
                # TODO instead append missing tag to context and report at end of process.
                raise TagNotExistsException(f"Tag ID {d.tag_id} does not exist in Tag Definitions.")
            else:
                return True

        def _col_selectors_not_none(col_selectors: List[ColumnSelector]) -> bool:
            if not d.column_selectors:
                # TODO instead append missing column selectors to context and report at end of process.
                # May be duplicative logic.  TODO think about this. am I capturing anything new?
                """If, after applying tags, no column selectors exist then throw error."""
                raise NoColumnSelectorsDefinedException(f'Tag Deployment contains no column selectors: '
                                                        f'{td.json()}')
            else:
                return True

        for td in tag_deps:
            for d in td.deployments:
                if d.tag_id and _valid_tag_id_in_ix(d.tag_id):
                    tagged_col_selectors = tag_ix.get(d.tag_id, [])
                    d.column_selectors.extend(tagged_col_selectors)
                    d.column_selectors = sorted(list(set(d.column_selectors)))

        for tag_id in row_creation_times.tag_ids:
            if _valid_tag_id_in_ix(tag_id):
                row_creation_times.column_selectors.extend(tag_ix[tag_id])

        row_creation_times.column_selectors = sorted(list(set(row_creation_times.column_selectors)))

        return tag_deps, row_creation_times

    @staticmethod
    def _apply_saved_metrics(saved_metric_ix: Dict[str, SimpleMetricDefinition],
                             tag_deps: List[TagDeploymentSuite],
                             table_deps: List[TableDeploymentSuite]
                             ) -> Tuple[List[TagDeploymentSuite], List[TableDeploymentSuite]]:

        def _apply_overrides(saved: SimpleMetricDefinition,
                             override: SimpleMetricDefinition) -> SimpleMetricDefinition:
            for attr in override.__dict__.keys():
                if attr not in ['saved_metric_id', 'metric_type']:
                    setattr(saved, attr, getattr(override, attr))

            return saved

        def _validate_and_apply(m: SimpleMetricDefinition) -> SimpleMetricDefinition:
            if not m.saved_metric_id:
                return m

            if m.saved_metric_id not in saved_metric_ix:
                # TODO instead append missing id to context and report at end of process.
                SavedMetricIdNotExistsException(f"Saved Metric ID does not exist in ix: {m.saved_metric_id}")

            if m.saved_metric_id and m.metric_type:
                """Assuming the only thing you cannot override in a saved metric is the metric type"""
                # TODO instead append error to context and report at end of process
                # TODO also valide in SimpleMetricDefinition.
                InvalidMetricDefinitionException(f"Cannot override the metric_type in a Saved "
                                                 f"Metric Definition: {m.json()}")

            saved = saved_metric_ix[m.saved_metric_id]
            return _apply_overrides(saved, m)

        for tag_dep in tag_deps:
            for d in tag_dep.deployments:
                metrics: List[SimpleMetricDefinition] = []
                for m in d.metrics:
                    metrics.append(_validate_and_apply(m))
                d.metrics = metrics

        for table_dep in table_deps:
            for d in table_dep.deployments:
                table_metrics: List[SimpleMetricDefinition] = []
                for m in d.table_metrics:
                    table_metrics.append(_validate_and_apply(m))
                d.table_metrics = table_metrics

                for c in d.columns:
                    column_metrics: List[SimpleMetricDefinition] = []
                    for m in c.metrics:
                        column_metrics.append(_validate_and_apply(m))
                    c.metrics = column_metrics

        return tag_deps, table_deps

    def to_metric_suite(self, sources: Dict[str, Source]) -> List[MetricSuite]:
        """
        Creates a MetricSuite for each source identified in a BigConfig Table or Tag Deployment.
        Args:
            sources: An index of Sources by Source Name.

        Returns: List[MetricSuite]
        """
        cmds: Dict[int, List[CohortAndMetricDefinition]] = {}

        for tag_d_suite in self.tag_deployments:
            for tag_d in tag_d_suite.deployments:
                r = tag_d.to_cohort_and_metric_def(sources=sources)
                for sid, definitions in r.items():
                    if sid in cmds:
                        cmds[sid].extend(definitions)
                    else:
                        cmds[sid] = definitions

        for table_d_suite in self.table_deployments:
            for table_d in table_d_suite.deployments:
                r = table_d.to_cohort_and_metric_def(sources=sources)
                for sid, definitions in r.items():
                    if sid in cmds:
                        cmds[sid].extend(definitions)
                    else:
                        cmds[sid] = definitions

        return [MetricSuite(source_id=source_id, definitions=definitions) for source_id, definitions in cmds.items()]
