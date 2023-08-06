from __future__ import annotations

from abc import ABC
from json import JSONDecodeError
from typing import List, Optional, Dict, Tuple

import requests

from bigeye_sdk.model.protobuf_extensions import MetricDebugQueries
from requests.auth import HTTPBasicAuth

from bigeye_sdk.client.enum import Method
from bigeye_sdk.client.generated_datawatch_client import GeneratedDatawatchClient
from bigeye_sdk.functions.delta_functions import infer_column_mappings, build_ccm, match_tables_by_name
from bigeye_sdk.functions.metric_functions import set_default_model_type_for_threshold, is_freshness_metric
from bigeye_sdk.functions.table_functions import get_table_column_priority_first, table_has_metric_time

from bigeye_sdk.generated.com.torodata.models.generated import MetricCreationState, \
    MetricConfiguration, TimeInterval, Threshold, MetricType, MetricParameter, LookbackType, NotificationChannel, \
    CreateComparisonTableResponse, CreateComparisonTableRequest, \
    ComparisonTableConfiguration, IdAndDisplayName, ComparisonColumnMapping, \
    ColumnNamePair, Table, GetDebugQueriesResponse, Schema, Source

from bigeye_sdk.log import get_logger
from bigeye_sdk.authentication.api_authentication import BasicAuthRequestLibConf, BrowserAuthConf, ApiAuthConf
from bigeye_sdk.model.protobuf_message_facade import SimpleColumnMapping, SimpleColumnPair
from bigeye_sdk.model.metric_facade import SimpleUpsertMetricRequest
from bigeye_sdk.model.delta_facade import SimpleDeltaConfiguration, SimpleDeltaConfigurationFile

log = get_logger(__file__)


def datawatch_client_factory(auth: ApiAuthConf):
    if isinstance(auth, BasicAuthRequestLibConf):
        client = BasicAuthDatawatchClient(api_conf=auth)
    elif isinstance(auth, BrowserAuthConf):
        client = BrowserAuthDatawatchClient(api_conf=auth)
    else:
        raise Exception('Auth type not supported.')

    return client


class DatawatchClient(GeneratedDatawatchClient, ABC):
    def get_sources_by_name(self, source_names: List[str] = None) -> Dict[str, Source]:
        """
        Creates a source index keyed by name and optionally limited by a list of names passed in.
        Args:
            source_names: names used to limit the index returned

        Returns: an index of sources that is keyed by name.

        """
        if not source_names:
            return {s.name: s for s in self.get_sources().sources}
        else:
            return {s.name: s for s in self.get_sources().sources if s.name in source_names}

    def get_schemas_by_fq_name(self, fq_schema_names: List[str]) -> Dict[str, Schema]:
        """
        Get schemas by fully qualified name.
        :param fq_schema_names: List of fully qualified schema names.  e.g. some_source.some_schema
        :return: Dictionary of schemas keyed by fully qualified schema name.
        """
        r: Dict[str, Schema] = {}
        for sn in fq_schema_names:
            split = sn.split('.')
            if len(split) != 3:
                raise Exception(f"Erroneous input.  Should be a fully qualified schema name.  Received: {sn}")

            warehouse_name, schema_name = split[0], '.'.join(split[-2:])
            source = self.get_sources_by_name(source_names=[warehouse_name])[warehouse_name]

            r[sn] = self.get_schemas_by_name(warehouse_id=source.id, schema_names=[schema_name])[schema_name]

        return r

    def get_schemas_by_name(self, warehouse_id: int, schema_names: List[str]) -> Dict[str, Schema]:
        """
        Builds a dictionary of schemas keyed by name.
        :param warehouse_id:
        :param schema_names:
        :return: Dict[schema_name:str, Schema]
        """
        schemas = self.get_schemas(warehouse_id=[warehouse_id])
        return {s.name: s for s in schemas.schemas if s.name in schema_names}

    def set_table_metric_time(self,
                              column_id: int):
        """
        Sets metric time by column id for a particular table.
        :param column_id: column id
        :return:
        """
        url = f'/dataset/loadedDate/{column_id}'
        self._call_datawatch(method=Method.PUT, url=url, body=None)

    def unset_table_metric_time(self,
                                table: Table):
        """
        Sets metric time by column id for a particular table.
        :param table: Table object
        :return:
        """

        if table_has_metric_time(table):
            url = f'/dataset/loadedDate/{table.metric_time_column.id}'
            log.info(f'Removing metric time from table: {table.database_name}.{table.schema_name}.{table.name}')
            self._call_datawatch(method=Method.DELETE, url=url, body=None)
        else:
            log.info(f'Table has no metric time set: {table.database_name}.{table.schema_name}.{table.name}')

    def _set_table_metric_times(self,
                                column_names: List[str],
                                tables: List[Table],
                                replace: bool = False
                                ):
        """Sets metric times on tables if a column matches, by order priority, and column name in the list of column
        names.  If replace is true then it will reset metric time on tables then it will do a backfill of all metrics
        in that table."""
        for t in tables:
            has_metric_time = table_has_metric_time(t)
            if not has_metric_time or replace:
                c = get_table_column_priority_first(table=t, column_names=column_names)
                if c:
                    log.info(f'Setting column {c.name} in table {t.database_name}.{t.schema_name}.{t.name} '
                             f'as metric time.')
                    self.set_table_metric_time(c.id)

                    if has_metric_time and replace:
                        mcs = self.search_metric_configuration(table_ids=[t.id])
                        mids = [mc.id for mc in mcs]
                        log.info(f'Backfilling metrics after replace.  Metric IDs: {mids}')
                        self.backfill_metric(metric_ids=mids)
                else:
                    log.info(f'No column name provided can be identified in table '
                             f'{t.database_name}.{t.schema_name}.{t.name}')

    def set_table_metric_times(self,
                               column_names: List[str],
                               table_ids: List[int],
                               replace: bool = False):
        """
        Accepts a list of column_names that are acceptable metric time columns and applies for a list of tables.
        :param replace: replace metric time if exists.
        :param column_names: names of columns that would be acceptable metric time columns.
        :param table_ids: the tables to apply metric times on.
        :return:
        """
        tables = self.get_tables(ids=table_ids).tables
        self._set_table_metric_times(tables=tables, column_names=column_names, replace=replace)

    def set_source_metric_times(self,
                                column_names: List[str],
                                wid: int,
                                replace: bool = False):
        """
        Accepts a list of column_names that are acceptable metric time columns and applies for the whole source.
        :param replace: replace metric time if exists.
        :param column_names: names of columns that would be acceptable metric time columns.
        :param wid: the wid to apply metric times on.
        :return:
        """
        tables = self.get_tables(warehouse_id=[wid]).tables
        self._set_table_metric_times(tables=tables, column_names=column_names, replace=replace)

    def unset_table_metric_times(self,
                                 table_ids: List[int]):
        """
        Unsets metric time for specified table ids.
        :param table_ids: table ids.
        :return:
        """
        tables = self.get_tables(ids=table_ids).tables
        for t in tables:
            self.unset_table_metric_time(t)

    def unset_source_metric_times(self,
                                  wid: int):
        """
        Unsets metric time for all tables in warehouse.
        :param wid: warehouse id.
        :return:
        """
        tables = self.get_tables(warehouse_id=[wid]).tables
        for t in tables:
            self.unset_table_metric_time(t)

    def suggest_deltas(self,
                       warehouse_name_pairs: List[Tuple[str, str]] = None,
                       fq_schema_name_pairs: List[Tuple[str, str]] = None,
                       warehouse_id_pairs: List[Tuple[int, int]] = None,
                       schema_id_pairs: List[Tuple[int, int]] = [],
                       table_id_pairs: List[Tuple[int, int]] = []) -> SimpleDeltaConfigurationFile:
        """
        Takes pairs of ids at the warehouse, schema, and table level and creates deltas between those ids.  Tables will
        match by name based on fuzzy logic for warehouse and schema ids.  The deltas created will use defaults and infer
        column mappings based on a string match.
        :param warehouse_name_pairs: List containing pairs of warehouse names [source, target]
        :param fq_schema_name_pairs: List containing pairs of fully qualified schema names [source, target]
        :param fq_table_name_pairs: List containing pairs of fully qualified table names [source, target]
        :param warehouse_id_pairs: list containing pairs of warehouse ids [source, target]
        :param schema_id_pairs: pairs of schema ids. [source, target]
        :param table_id_pairs: pairs of table ids. [source, target]
        :return: List of simple delta configurations created. [source, target]
        :return: a list of SimpleDeltaConfigurations that were suggested and created.
        """

        # TODO: If exists then pull the config
        # TODO: Add configurable cron.

        tidp_dict: Dict[str, Tuple[int, int]] = {}

        if warehouse_name_pairs:
            sources: Dict[str, Source] = self.get_sources_by_name()
            widps: List[Tuple[int, int]] = [(sources[wnp[0]].id, sources[wnp[1]].id) for wnp in warehouse_name_pairs]

            if warehouse_id_pairs:
                warehouse_id_pairs.extend(widps)
            else:
                warehouse_id_pairs = widps

        if fq_schema_name_pairs:

            schema_id_pairs.extend(
                [(self.get_schemas_by_fq_name(fq_schema_names=[snp[0]])[snp[0]].id,
                  self.get_schemas_by_fq_name(fq_schema_names=[snp[1]])[snp[1]].id)
                 for snp in fq_schema_name_pairs]
            )

        if warehouse_id_pairs:
            for widp in warehouse_id_pairs:
                st = self.get_tables(warehouse_id=[widp[0]])
                tt = self.get_tables(warehouse_id=[widp[1]])

                m = match_tables_by_name(source_tables=st.tables, target_tables=tt.tables)
                tidp_dict.update(m)

        if schema_id_pairs:
            for sidp in schema_id_pairs:
                st = self.get_tables(schema_id=[sidp[0]])
                tt = self.get_tables(schema_id=[sidp[1]])

                m = match_tables_by_name(source_tables=st.tables, target_tables=tt.tables)
                tidp_dict.update(m)

        if table_id_pairs:
            st = self.get_tables(ids=[tid[0] for tid in table_id_pairs])
            tt = self.get_tables(ids=[tid[1] for tid in table_id_pairs])
            m = match_tables_by_name(source_tables=st.tables, target_tables=tt.tables)
            tidp_dict.update(m)

        created_deltas: List[SimpleDeltaConfiguration] = []

        for delta_name, tidp in tidp_dict.items():
            sdc = SimpleDeltaConfiguration(delta_name=delta_name, source_table_id=tidp[0], target_table_id=tidp[1])
            # TODO: Clunky
            r = self.create_deltas_from_simple_conf(sdcl=[sdc])[0]

            # TODO: See if we can move the builder logic over to SimpleDeltaConfiguration.from_response_object
            response_as_sdc = SimpleDeltaConfiguration(delta_id=r.id,
                                                       delta_name=r.name,
                                                       source_table_id=r.source_table_id,
                                                       target_table_id=r.target_table_id,
                                                       source_filters=r.source_filters,
                                                       target_filters=r.target_filters
                                                       )

            response_as_sdc.delta_column_mapping = [SimpleColumnMapping.from_datawatch_object(cm) for cm in
                                                    r.column_mappings]

            # TODO: create a function to get the metrics common to all column mappings, filter from each column mapping,
            # TODO: and add them to builder.all_column_metrics?

            response_as_sdc.group_bys = [SimpleColumnPair.from_datawatch_object(cp) for cp in r.group_bys]

            # TODO: way too cluncky.  We have to make another round trip just to get the cron.
            cron_resp = self.get_named_schedule(ids=[r.named_schedule.id])

            if cron_resp.named_schedules:
                response_as_sdc.cron_schedule = cron_resp.named_schedules[0]

            created_deltas.append(response_as_sdc)

        return SimpleDeltaConfigurationFile(type='DELTA_CONFIGURATION_FILE', deltas=created_deltas)

    def delete_deltas_by_name(self, delta_names: List[str]):
        """
        Deletes deltas by string name.
        :param delta_names: list of delta names
        :return:
        """

        existing_delta_ids = [d.comparison_table_configuration.id
                              for d in self.get_delta_information(delta_ids=[], exclude_comparison_metrics=True)
                              if d.comparison_table_configuration.name in delta_names]
        for deltaid in existing_delta_ids:
            self.delete_delta(comparison_table_id=deltaid)

    def create_deltas_from_simple_conf(self, sdcl: List[SimpleDeltaConfiguration]) -> List[ComparisonTableConfiguration]:
        """
        Creates Deltas from a SimpleDeltaConfigurationList.

        :param sdcl: Instance of SimpleDeltaConfigurationList

        :return: Resulting ComparisonTableConfiguration
        """

        # Delete if already exist.
        self.delete_deltas_by_name(delta_names=[sdc.delta_name for sdc in sdcl])

        responses = []

        for sdc in sdcl:

            tables = self.get_tables(ids=[sdc.source_table_id, sdc.target_table_id]).tables

            if len(tables) == 2:
                for t in tables:
                    if t.id == sdc.source_table_id:
                        source_table = t
                    elif t.id == sdc.target_table_id:
                        target_table = t
                    else:
                        # TODO: Create Named Exception!
                        raise Exception(f"Erroneous table id returned: {t.id}")
            else:
                # TODO: Create Named Exception!
                raise Exception(f"Cannot find table ids.  Source Table: {sdc.source_table_id}  "
                                f"Target Table: {sdc.target_table_id}")

            response_as_ctc = ComparisonTableConfiguration(name=sdc.delta_name, source_table_id=sdc.source_table_id,
                                                           target_table_id=sdc.target_table_id)

            if sdc.delta_column_mapping:
                """
                If mappings are declared then metrics will be taken from those mappings and no defaults will be applied.
                """
                response_as_ctc.column_mappings = [
                    build_ccm(scm=cm, source_table=source_table, target_table=target_table)
                    for cm in sdc.delta_column_mapping]
            else:
                """
                If no mappings are declared then column mappings will be inferred and metrics will be defaulted.
                """
                source_metric_types = self.get_delta_applicable_metric_types(table_id=sdc.source_table_id).metric_types
                target_metric_types = self.get_delta_applicable_metric_types(table_id=sdc.target_table_id).metric_types
                response_as_ctc.column_mappings = infer_column_mappings(source_metric_types=source_metric_types,
                                                                        target_metric_types=target_metric_types)

            if sdc.all_column_metrics:
                all_column_metrics = [m.get_metric_type() for m in sdc.all_column_metrics]
                """If SDC has defined all_column_metrics then the each columns metrics wil lbe extended with the metrics
                defined in all_column_metrics."""
                for m in response_as_ctc.column_mappings:
                    m.metrics.extend(all_column_metrics)

            response_as_ctc.group_bys = [gb.to_datawatch_object() for gb in sdc.group_bys]
            response_as_ctc.source_filters = sdc.source_filters
            response_as_ctc.target_filters = sdc.target_filters

            schedules = self.get_named_schedule().named_schedules

            for s in schedules:
                """Matches on cron value."""
                if s.cron == sdc.cron_schedule:
                    response_as_ctc.named_schedule = IdAndDisplayName(id=s.id, display_name=s.name)

            if response_as_ctc.named_schedule is None:
                ns = self.create_named_schedule(name=sdc.cron_schedule.name, cron=sdc.cron_schedule.cron)
                response_as_ctc.named_schedule = IdAndDisplayName(id=ns.id, display_name=ns.name)

            response = self.create_delta(comparison_table_configuration=response_as_ctc)

            responses.append(response.comparison_table_configuration)

        return responses

    def create_delta(
            self,
            name: str = None,
            source_table_id: int = None,
            target_table_id: int = None,
            metrics_to_enable: List[MetricType] = [],
            column_mappings: List[ComparisonColumnMapping] = [],
            named_schedule: IdAndDisplayName = None,
            group_bys: List[ColumnNamePair] = [],
            source_filters: List[str] = [],
            target_filters: List[str] = [],
            comparison_table_configuration: Optional["ComparisonTableConfiguration"] = None,
    ) -> CreateComparisonTableResponse:
        """

        Args:
            name: Required.  Name of delta
            source_table_id:  Required.  table id for source table
            target_table_id: Required. Table id for target table
            column_mappings: Optional. If not exists then will infer from applicable table mappings based on column name.
            named_schedule: Optional.  No schedule if not exists
            group_bys: Optional.  No group bys if not exists
            source_filters: Optional.  No filters if not exists
            target_filters: Optional.  No filters if not exists
            comparison_table_configuration: Optional.

        Returns:  CreateComparisonTableResponse

        """

        if metrics_to_enable and column_mappings:
            raise Exception('Column mappings defines the enabled metrics by column map.  Either define column mappings '
                            'OR metrics to enable -- not both.')

        url = '/api/v1/metrics/comparisons/tables'

        request = CreateComparisonTableRequest()
        if comparison_table_configuration:
            request.comparison_table_configuration = comparison_table_configuration
        elif name and source_table_id and target_table_id:
            request.comparison_table_configuration.name = name
            request.comparison_table_configuration.source_table_id = source_table_id
            request.comparison_table_configuration.target_table_id = target_table_id
            request.comparison_table_configuration.column_mappings = column_mappings
            if named_schedule:
                request.comparison_table_configuration.named_schedule = named_schedule
            request.comparison_table_configuration.group_bys = group_bys
            request.comparison_table_configuration.source_filters = source_filters
            request.comparison_table_configuration.target_filters = target_filters
            request.comparison_table_configuration.target_table_id = target_table_id
        else:
            raise Exception('Must supply either a ComparisonMetricConfiguration OR a name, '
                            'source table id, and target table id.')

        if not request.comparison_table_configuration.column_mappings:
            source_metric_types = self.get_delta_applicable_metric_types(
                table_id=request.comparison_table_configuration.source_table_id
            ).metric_types
            target_metric_types = self.get_delta_applicable_metric_types(
                table_id=request.comparison_table_configuration.target_table_id
            ).metric_types
            request.comparison_table_configuration.column_mappings = infer_column_mappings(
                source_metric_types=source_metric_types,
                target_metric_types=target_metric_types
            )
            if metrics_to_enable:
                for m in request.comparison_table_configuration.column_mappings:
                    m.metrics = metrics_to_enable

        response = self._call_datawatch(Method.POST, url, request.to_json())

        return CreateComparisonTableResponse().from_dict(response)

    def upsert_metric(
            self,
            *,
            id: int = 0,
            schedule_frequency: Optional[TimeInterval] = None,
            filters: List[str] = [],
            group_bys: List[str] = [],
            thresholds: List[Threshold] = [],
            notification_channels: List[NotificationChannel] = [],
            warehouse_id: int = 0,
            dataset_id: int = 0,
            metric_type: Optional[MetricType] = None,
            parameters: List[MetricParameter] = [],
            lookback: Optional[TimeInterval] = None,
            lookback_type: LookbackType = 0,
            metric_creation_state: MetricCreationState = 0,
            grain_seconds: int = 0,
            muted_until_epoch_seconds: int = 0,
            name: str = "",
            description: str = "",
            metric_configuration: MetricConfiguration = None
    ) -> MetricConfiguration:
        """Create or update metric"""

        if metric_configuration:
            request = metric_configuration
        else:
            request = MetricConfiguration()
            request.id = id
            if schedule_frequency is not None:
                request.schedule_frequency = schedule_frequency
            request.filters = filters
            request.group_bys = group_bys
            if thresholds is not None:
                request.thresholds = set_default_model_type_for_threshold(thresholds)
            if notification_channels is not None:
                request.notification_channels = notification_channels
            request.warehouse_id = warehouse_id
            request.dataset_id = dataset_id
            if metric_type is not None:
                request.metric_type = metric_type
            if parameters is not None:
                request.parameters = parameters
            if lookback is not None:
                request.lookback = lookback
            request.lookback_type = lookback_type
            request.metric_creation_state = metric_creation_state
            request.grain_seconds = grain_seconds
            request.muted_until_epoch_seconds = muted_until_epoch_seconds
            request.name = name
            request.description = description

        set_default_model_type_for_threshold(request.thresholds)

        url = "/api/v1/metrics"

        response = self._call_datawatch(Method.POST, url=url, body=request.to_json())

        return MetricConfiguration().from_dict(response)

    def upsert_metric_from_simple_template(
            self,
            sumr: SimpleUpsertMetricRequest,
            existing_metric_id: int = None
    ) -> int:
        """
        Takes a warehouse id and a SimpleUpsertMetricRequest, fills in reasonable defaults, and upserts a metric.

        :param sumr: SimpleUpsertMetricRequest object
        :param existing_metric_id: An existing metric ID on which to base the upsert

        :return: Id of the resulting metric.
        """
        # TODO Consider moving warehouse_id into sumr
        if sumr.metric_template.metric_name is None:
            raise Exception("Metric name must be present in configuration", sumr)

        tables = self.get_tables(warehouse_id=[sumr.warehouse_id], schema=[sumr.schema_name],
                                 table_name=[sumr.table_name]).tables

        if not tables:
            raise Exception(f"Could not find table: {sumr.schema_name}.{sumr.table_name}")
        elif len(tables) > 1:
            p = [f"Warehouse ID: {t.warehouse_id}.  FQ Table Name: " \
                 f"{t.database_name}.{t.schema_name}.{t.name}" for t in tables]
            raise Exception(f"Found multiple tables. {p}")
        else:
            table = tables[0]

        if existing_metric_id:
            existing_metric = self.get_metric_configuration(metric_id=existing_metric_id)
        else:
            existing_metric = self.get_existing_metric(
                warehouse_id=sumr.warehouse_id,
                table=table,
                column_name=sumr.column_name,
                user_defined_name=sumr.metric_template.user_defined_metric_name,
                metric_name=sumr.metric_template.metric_name,
                group_by=sumr.metric_template.group_by,
                filters=sumr.metric_template.filters)

        metric = sumr.to_datawatch_object(target_table=table, existing_metric=existing_metric)

        should_backfill = False
        if metric.id is None and not is_freshness_metric(sumr.metric_template.metric_name):
            should_backfill = True

        result = self.upsert_metric(metric_configuration=metric)

        log.info("Create result: %s", result.to_json())
        if should_backfill and result.id is not None and table_has_metric_time(table):
            self.backfill_metric(metric_ids=[result.id])

        return result.id

    def regen_autometrics(self, table_id: int):
        url = f'/statistics/suggestions/{table_id}/queue'
        log.info(url)
        response = self._call_datawatch(Method.GET, url=url)

    def backfill_autothresholds(self,
                                metric_ids: List[int] = []):
        """
        Runs posthoc autothresholds for existing metric runs.  Does not run metrics for past data.  Not destructive.
        Will run sync.
        :param metric_ids: list of metric ids
        :return: none.
        """
        for metric_id in metric_ids:
            log.info(f"Backfilling autothreshold: {metric_id}")
            url = f"/statistics/backfillAutoThresholds/{metric_id}"
            response = self._call_datawatch(Method.GET, url=url)

    def get_debug_queries(self, *, metric_ids: List[int]) -> List[MetricDebugQueries]:
        """
        Get queries for debug page
        :param metric_ids: List of metric ids for which to retrieve debug queries.
        :return: a dictionary of
        """
        r: List[MetricDebugQueries] = []

        for metric_id in metric_ids:
            url = f'/api/v1/metrics/{metric_id}/debug/queries'
            i = MetricDebugQueries(
                metric_id=metric_id,
                debug_queries=GetDebugQueriesResponse().from_dict(self._call_datawatch(Method.GET, url))
            )
            r.append(i)

        return r


class BasicAuthDatawatchClient(DatawatchClient):

    def __init__(self, api_conf: BasicAuthRequestLibConf):
        self._base_url = api_conf.base_url
        self._auth = HTTPBasicAuth(api_conf.user, api_conf.password)
        pass

    def _call_datawatch_impl(self, method: Method, url, body: str = None, params: dict = None):
        try:
            fq_url = f'{self._base_url}{url}'
            log.info(f'Request Type: {method.name}; URL: {fq_url}; Body: {body}')
            if method == Method.GET:
                response = requests.get(
                    fq_url,
                    auth=self._auth,
                    params=params
                )
            elif method == Method.POST:
                response = requests.post(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    auth=self._auth,
                    params=params
                )
            elif method == Method.PUT:
                response = requests.put(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    auth=self._auth,
                    params=params
                )
            elif method == Method.DELETE:
                response = requests.delete(f'{self._base_url}{url}',
                                           headers={"Content-Type": "application/json", "Accept": "application/json"},
                                           data=body,
                                           auth=self._auth, params=params)
            else:
                raise Exception(f'Unsupported http method {method}')
        except Exception as e:
            log.info(f'URL: {response.url}')
            log.error(f'Exception calling datawatch: {str(e)}')
            raise e
        else:
            log.info(f'URL: {response.url}')
            log.info(f'Return Code: {response.status_code}')
            if response.status_code < 200 or response.status_code >= 300:
                log.error(f'Error code returned from datawatch: {str(response)}')
                raise Exception(response.text)
            else:
                # Not empty response
                try:
                    if response.status_code != 204:
                        return response.json()
                except JSONDecodeError as e:
                    log.info(f'Cannot decode response.  {response}')
                    return ''


class BrowserAuthDatawatchClient(DatawatchClient):
    def __init__(self, api_conf: BrowserAuthConf):
        self._base_url = api_conf.base_url
        self.api_conf = api_conf
        self._cookies = self.api_conf.auth_factory().get_cookies()

    def _call_datawatch_impl(self, method: Method, url, body: str = None, params: dict = None):
        # TODO: This shouldn't repeat the above code when the only thing changing is a call to cookies, instead of auth.
        try:
            fq_url = f'{self._base_url}{url}'
            log.info(f'Request Type: {method.name}; URL: {fq_url}; Body: {body}')
            if method == Method.GET:
                response = requests.get(
                    fq_url,
                    cookies=self._cookies
                )
            elif method == Method.POST:
                response = requests.post(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    cookies=self._cookies
                )
            elif method == Method.PUT:
                response = requests.put(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    cookies=self._cookies
                )
            elif method == Method.DELETE:
                response = requests.delete(f'{self._base_url}{url}',
                                           headers={"Content-Type": "application/json", "Accept": "application/json"},
                                           data=body,
                                           cookies=self._cookies)
            else:
                raise Exception(f'Unsupported http method {method}')
        except Exception as e:
            log.error(f'Exception calling datawatch: {str(e)}')
            raise e
        else:
            log.info(f'Return Code: {response.status_code}')
            if response.status_code < 200 or response.status_code >= 300:
                log.error(f'Error code returned from datawatch: {str(response)}')
                raise Exception(response.text)
            else:
                # Not empty response
                if response.status_code != 204:
                    return response.json()
