from __future__ import annotations

import json
from abc import ABC
from typing import List, Optional, TypeVar, Union

import betterproto

from bigeye_sdk.exceptions import InvalidConfigurationException
from pydantic_yaml import YamlModel


from bigeye_sdk.functions.table_functions import get_table_column_id
from bigeye_sdk.generated.com.torodata.models.generated import Threshold, SimpleBoundType, ConstantThreshold, \
    SimpleBound, NamedSchedule, ComparisonColumnMapping, Table, IdAndDisplayName, ColumnNamePair, TimeInterval, \
    MetricParameter, MetricType, PredefinedMetric, TemplateMetric, AutoThreshold, ForecastModelType, RelativeThreshold, \
    StandardDeviationThreshold, FreshnessScheduleThreshold, NotificationChannel, MetricDefinition, MetricConfiguration
from bigeye_sdk.model.base_datawatch_facade import DatawatchFacade
from bigeye_sdk.model.protobuf_enum_facade import SimplePredefinedMetricName, SimpleTimeIntervalType, \
    SimpleAutothresholdSensitivity, SimpleLookbackType, SimpleAggregationType
from bigeye_sdk.serializable import PydanticSubtypeSerializable


class SimpleMetricType(PydanticSubtypeSerializable, DatawatchFacade, ABC):
    type: str

    @classmethod
    def from_datawatch_object(cls, obj: MetricType) -> SimpleMetricType:
        mtd = obj.to_dict()  # TODO: this is the only way it would work.  beterproto has defaults that create 0 int placeholders.  Works for now but try a new way later.
        if 'templateMetric' in mtd:
            tm = obj.template_metric
            return SimpleTemplateMetric(type='TEMPLATE',
                                        template_id=tm.template_id,
                                        aggregation_type=SimpleAggregationType.from_datawatch_object(
                                            tm.aggregation_type),
                                        template_name=tm.template_name)
        elif 'predefinedMetric' in mtd:
            return SimplePredefinedMetric(
                type='PREDEFINED',
                metric=SimplePredefinedMetricName.from_datawatch_object(obj.predefined_metric.metric_name)
            )


class SimplePredefinedMetric(SimpleMetricType, type='PREDEFINED'):
    metric: SimplePredefinedMetricName

    def to_datawatch_object(self, **kwargs) -> MetricType:
        return MetricType(predefined_metric=PredefinedMetric(metric_name=self.metric.to_datawatch_object()))


class SimpleTemplateMetric(SimpleMetricType, type='TEMPLATE'):
    template_id: int
    aggregation_type: SimpleAggregationType
    template_name: Optional[str] = None

    def to_datawatch_object(self, **kwargs) -> MetricType:
        return MetricType(template_metric=TemplateMetric(template_id=self.template_id,
                                                         aggregation_type=self.aggregation_type.to_protpbuf(),
                                                         template_name=self.template_name))


class SimpleNamedSchedule(YamlModel, DatawatchFacade):
    name: str
    cron: str
    id: Optional[int] = None

    @classmethod
    def from_datawatch_object(cls, obj: NamedSchedule, **kwargs) -> SimpleNamedSchedule:
        return SimpleNamedSchedule(name=obj.name, cron=obj.cron, id=obj.id)

    def to_datawatch_object(self) -> NamedSchedule:
        return NamedSchedule(name=self.name, cron=self.cron, id=self.id)


class SimpleColumnMapping(YamlModel, DatawatchFacade):
    source_column_name: str
    target_column_name: str
    metrics: List[SimpleMetricType]

    @classmethod
    def from_datawatch_object(cls, obj: ComparisonColumnMapping) -> SimpleColumnMapping:
        smt_list: List[SimpleMetricType] = [SimpleMetricType.from_datawatch_object(om) for om in obj.metrics]
        return SimpleColumnMapping(source_column_name=obj.source_column.display_name,
                                   target_column_name=obj.target_column.display_name,
                                   metrics=smt_list)

    def to_datawatch_object(self, source_table: Table, target_table: Table) -> ComparisonColumnMapping:
        cm = ComparisonColumnMapping()
        cm.source_column = IdAndDisplayName(id=get_table_column_id(source_table, self.source_column_name),
                                            display_name=self.source_column_name)
        cm.target_column = IdAndDisplayName(id=get_table_column_id(target_table, self.target_column_name),
                                            display_name=self.target_column_name)
        cm.metrics = [m.to_datawatch_object() for m in self.metrics]
        return cm


class SimpleColumnPair(YamlModel, DatawatchFacade):
    source_column_name: str
    target_column_name: str

    @classmethod
    def from_datawatch_object(cls, obj: ColumnNamePair) -> SimpleColumnPair:
        return SimpleColumnPair(source_column_name=obj.source_column_name, target_column_name=obj.target_column_name)

    def to_datawatch_object(self) -> ColumnNamePair:
        return ColumnNamePair(
            source_column_name=self.source_column_name,
            target_column_name=self.target_column_name
        )


class SimpleUpsertIssueRequest(YamlModel):
    pass


class SimpleTimeInterval(YamlModel, DatawatchFacade):
    interval_type: SimpleTimeIntervalType
    interval_value: int

    @classmethod
    def from_datawatch_object(cls, obj: TimeInterval) -> Optional[SimpleTimeInterval]:
        if obj.interval_type == 0 and obj.interval_value == 0:
            return None
        return SimpleTimeInterval(interval_type=SimpleTimeIntervalType.from_datawatch_object(obj.interval_type),
                                  interval_value=obj.interval_value)

    def to_datawatch_object(self, **kwargs) -> TimeInterval:
        return TimeInterval(interval_type=self.interval_type.to_datawatch_object(), interval_value=self.interval_value)


ST = TypeVar('ST', bound='SimpleThreshold')


class SimpleThreshold(PydanticSubtypeSerializable, DatawatchFacade, ABC):
    type: str

    @classmethod
    def from_datawatch_object(cls, obj: List[Threshold]) -> ST:
        type = betterproto.which_one_of(obj[0], "threshold_type")[0]
        if type == 'auto_threshold':
            sat = SimpleAutoThreshold(
                type="AUTO",
                sensitivity=SimpleAutothresholdSensitivity.from_datawatch_object(obj[0].auto_threshold.sensitivity)
            )
            return sat
        elif type == 'constant_threshold':
            lower_bound = 0.0
            upper_bound = 0.0
            for i in obj:
                if i.constant_threshold.bound.bound_type == SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE:
                    lower_bound = i.constant_threshold.bound.value
                if i.constant_threshold.bound.bound_type == SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE:
                    upper_bound = i.constant_threshold.bound.value

            sct = SimpleConstantThreshold(type="CONSTANT", lower_bound=lower_bound, upper_bound=upper_bound)

            return sct
        elif type == 'relative_threshold':
            """Relative Threshold"""
            lower_bound = None
            upper_bound = None
            lookback = SimpleTimeInterval.from_datawatch_object(obj[0].relative_threshold.lookback)
            for i in obj:
                if i.relative_threshold.bound.bound_type == SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE:
                    lower_bound = i.relative_threshold.bound.value
                if i.relative_threshold.bound.bound_type == SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE:
                    upper_bound = i.relative_threshold.bound.value

            srt = SimpleRelativeThreshold(type="RELATIVE",
                                          lower_bound=lower_bound, upper_bound=upper_bound, lookback=lookback)

            return srt
        elif type == 'standard_deviation_threshold':
            """StdDev Threshold"""
            lower_bound = None
            upper_bound = None
            lookback = SimpleTimeInterval.from_datawatch_object(obj[0].standard_deviation_threshold.lookback)
            for i in obj:
                if i.standard_deviation_threshold.bound.bound_type == SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE:
                    lower_bound = i.standard_deviation_threshold.bound.value
                if i.standard_deviation_threshold.bound.bound_type == SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE:
                    upper_bound = i.standard_deviation_threshold.bound.value

            ssdt = SimpleStdDevThreshold(type="STDDEV",
                                         lower_bound=lower_bound, upper_bound=upper_bound, lookback=lookback)

            return ssdt
        elif type == 'freshness_schedule_threshold':
            """Freshness Schedule Threshold"""
            t = obj[0].freshness_schedule_threshold
            bound = t.bound.value
            dau = None if not t.delay_at_update else SimpleTimeInterval.from_datawatch_object(t.delay_at_update)
            ft = SimpleFreshnessThreshold(
                type='FRESHNESS',
                cron=t.cron, timezone=t.timezone, upper_bound=bound, delay_at_update=dau)
            return ft
        else:
            InvalidConfigurationException(f'Format does not match known configuration: {json.dumps(obj)}')


class SimpleAutoThreshold(SimpleThreshold, type='AUTO'):
    sensitivity: SimpleAutothresholdSensitivity

    def to_datawatch_object(self, **kwargs) -> List[Threshold]:
        lb = SimpleBound(bound_type=SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE, value=-1.0)
        ub = SimpleBound(bound_type=SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE, value=-1.0)
        mt = ForecastModelType.BOOTSTRAP_THRESHOLD_MODEL_TYPE
        s = self.sensitivity.to_datawatch_object()
        fv = -1.0

        lbat = AutoThreshold(
            bound=lb,
            model_type=mt,
            sensitivity=s,
            forecast_value=fv
        )
        ubat = AutoThreshold(
            bound=ub,
            model_type=mt,
            sensitivity=s,
            forecast_value=fv
        )

        return [Threshold(auto_threshold=lbat), Threshold(auto_threshold=ubat)]


class SimpleConstantThreshold(SimpleThreshold, type='CONSTANT'):
    upper_bound: float
    lower_bound: float = 0.0

    def to_datawatch_object(self) -> List[Threshold]:
        """
        Creates a list of protobuf Threshold objects from an instance of SimpleConstantThreshold
        :return: a List of Thresholds
        """
        lb = ConstantThreshold()
        sb = SimpleBound()
        sb.bound_type = SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE
        sb.value = self.lower_bound
        lb.bound = sb
        sb = SimpleBound()
        sb.bound_type = SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE
        sb.value = self.upper_bound
        ub = ConstantThreshold()
        ub.bound = sb
        lbt = Threshold()
        lbt.constant_threshold = lb
        ubt = Threshold()
        ubt.constant_threshold = ub
        return [lbt, ubt]


class SimpleFreshnessThreshold(SimpleThreshold, type='FRESHNESS'):
    cron: str
    upper_bound: float
    timezone: Optional[str] = None
    delay_at_update: Optional[SimpleTimeInterval] = SimpleTimeInterval(interval_type=SimpleTimeIntervalType.HOURS,
                                                                       interval_value=0)

    def to_datawatch_object(self, **kwargs) -> List[Threshold]:
        ub = SimpleBound(bound_type=SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE, value=self.upper_bound)
        dau = self.delay_at_update.to_datawatch_object()
        ft = FreshnessScheduleThreshold(cron=self.cron, bound=ub, timezone=self.timezone, delay_at_update=dau)

        return [Threshold(freshness_schedule_threshold=ft)]


class SimpleRelativeThreshold(SimpleThreshold, type='RELATIVE'):
    lookback: SimpleTimeInterval
    upper_bound: float
    lower_bound: float = 0.0

    def to_datawatch_object(self, **kwargs) -> List[Threshold]:
        lkbk = self.lookback.to_datawatch_object()
        lb = SimpleBound(bound_type=SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE, value=self.lower_bound)
        ub = SimpleBound(bound_type=SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE, value=self.upper_bound)
        lrt = RelativeThreshold(lookback=lkbk, bound=lb)
        urt = RelativeThreshold(lookback=lkbk, bound=ub)

        return [Threshold(relative_threshold=lrt), Threshold(relative_threshold=urt)]


class SimpleStdDevThreshold(SimpleThreshold, type='STDDEV'):
    lookback: SimpleTimeInterval
    upper_bound: float
    lower_bound: float = 0.0

    def to_datawatch_object(self, **kwargs) -> List[Threshold]:
        lkbk = self.lookback.to_datawatch_object()
        lb = SimpleBound(bound_type=SimpleBoundType.LOWER_BOUND_SIMPLE_BOUND_TYPE, value=self.lower_bound)
        ub = SimpleBound(bound_type=SimpleBoundType.UPPER_BOUND_SIMPLE_BOUND_TYPE, value=self.upper_bound)
        lsdt = StandardDeviationThreshold(lookback=lkbk, bound=lb)
        usdt = StandardDeviationThreshold(lookback=lkbk, bound=ub)

        return [Threshold(standard_deviation_threshold=lsdt), Threshold(standard_deviation_threshold=usdt)]


SNC = TypeVar('SNC', bound='SimpleNotificationChannel')


class SimpleNotificationChannel(PydanticSubtypeSerializable, DatawatchFacade, ABC):
    type: str

    @classmethod
    def from_datawatch_object(cls, obj: NotificationChannel) -> SNC:
        if 'email' in obj.to_json():
            return EmailNotificationChannel(type='EMAIL', value=obj.email)
        elif 'slackChannel' in obj.to_json():
            return SlackNotificationChannel(type='SLACK', value=obj.slack_channel)
        else:
            InvalidConfigurationException(f'Format does not match known configuration: {json.dumps(obj)}')


class EmailNotificationChannel(SimpleNotificationChannel, type='EMAIL'):
    value: str

    def to_datawatch_object(self, **kwargs) -> NotificationChannel:
        return NotificationChannel(email=self.value)


class SlackNotificationChannel(SimpleNotificationChannel, type='SLACK'):
    value: str

    def to_datawatch_object(self, **kwargs) -> NotificationChannel:
        return NotificationChannel(slack_channel=self.value)


class SimpleMetricParameter(YamlModel, DatawatchFacade):
    key: str
    string_value: Optional[str] = None
    column_name: Optional[str] = None
    number_value: Optional[float] = None

    @classmethod
    def from_datawatch_object(cls, obj: MetricParameter) -> SimpleMetricParameter:
        return SimpleMetricParameter(key=obj.key,
                                     string_value=obj.string_value,
                                     column_name=obj.column_name,
                                     number_value=obj.number_value)

    def to_datawatch_object(self, **kwargs) -> MetricParameter:
        return MetricParameter(key=self.key,
                               string_value=self.string_value,
                               column_name=self.column_name,
                               number_value=self.number_value)


class SimpleMetricDefinition(YamlModel, DatawatchFacade):
    saved_metric_id: Optional[str] = None
    metric_type: Optional[SimpleMetricType] = None
    metric_name: Optional[str] = None
    description: Optional[str] = None
    schedule_frequency: Optional[SimpleTimeInterval] = SimpleTimeInterval(interval_type=SimpleTimeIntervalType.HOURS,
                                                                          interval_value=6)
    conditions: Optional[List[str]] = None
    group_by: Optional[List[str]] = None
    threshold: Optional[SimpleThreshold] = None
    notification_channels: Optional[List[SimpleNotificationChannel]] = None
    parameters: Optional[List[SimpleMetricParameter]] = None
    lookback: Optional[SimpleTimeInterval] = None
    lookback_type: Optional[SimpleLookbackType] = None
    grain_seconds: Optional[int] = 0
    muted_until_epoch_seconds: Optional[int] = None

    # @validator
    #     # TODO: must either have a metric_type OR saved_metric_id
    #     pass

    @classmethod
    def from_datawatch_object(cls, obj: Union[MetricDefinition, MetricConfiguration]) -> SimpleMetricDefinition:
        builder = SimpleMetricDefinition()
        builder.metric_type = SimpleMetricType.from_datawatch_object(obj.metric_type)
        builder.metric_name = obj.name
        builder.description = obj.description

        builder.schedule_frequency = SimpleTimeInterval.from_datawatch_object(obj.schedule_frequency)

        builder.conditions = obj.filters
        builder.group_by = obj.group_bys

        builder.threshold = SimpleThreshold.from_datawatch_object(obj.thresholds)

        builder.notification_channels = [SimpleNotificationChannel.from_datawatch_object(nc)
                                         for nc in obj.notification_channels]

        builder.parameters = [SimpleMetricParameter.from_datawatch_object(p) for p in obj.parameters]

        builder.lookback = SimpleTimeInterval.from_datawatch_object(obj.lookback)

        builder.lookback_type = SimpleLookbackType.from_datawatch_object(obj.lookback_type)

        builder.grain_seconds = obj.grain_seconds
        builder.muted_until_epoch_seconds = obj.muted_until_epoch_seconds

        return builder

    def to_datawatch_object(self, **kwargs) -> MetricDefinition:
        builder = MetricDefinition()

        # Verifying that metric_type has been set before serializing to datawatch object.
        if self.metric_type:
            builder.metric_type = self.metric_type.to_datawatch_object()
        else:
            InvalidConfigurationException(
                "Metric Type cannot be None.  Verify that Saved Metric IDs have been applied.")

        builder.name = self.metric_name
        builder.description = self.description

        if self.schedule_frequency:
            builder.schedule_frequency = self.schedule_frequency.to_datawatch_object()

        builder.filters = self.conditions
        builder.group_bys = self.group_by

        if self.threshold:
            builder.thresholds = self.threshold.to_datawatch_object()

        if self.notification_channels:
            builder.notification_channels = [nc.to_datawatch_object() for nc in self.notification_channels]

        if self.parameters:
            builder.parameters = [p.to_datawatch_object() for p in self.parameters]

        if self.lookback:
            builder.lookback = self.lookback.to_datawatch_object()

        if self.lookback_type:
            builder.lookback_type = self.lookback_type.to_datawatch_object()

        builder.grain_seconds = self.grain_seconds
        builder.muted_until_epoch_seconds = self.muted_until_epoch_seconds

        return builder
