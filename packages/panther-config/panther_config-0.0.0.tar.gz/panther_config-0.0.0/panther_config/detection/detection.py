# coding=utf-8
# *** WARNING: generated file

import typing
import dataclasses

from .. import _utilities

__all__ = [
    "_BaseFilter",
    "PythonFilter",
    "_BaseUnitTest",
    "JSONUnitTest",
    "DictUnitTest",
    "Rule",
    "SeverityLow",
    "SeverityInfo",
    "SeverityMedium",
    "SeverityHigh",
    "SeverityCritical",
]


SeverityLow = "LOW"
SeverityInfo = "INFO"
SeverityMedium = "MEDIUM"
SeverityHigh = "HIGH"
SeverityCritical = "CRITICAL"


@dataclasses.dataclass(frozen=True)
class _BaseFilter(_utilities.ConfigNode):
    """
    Base filter
    """

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="_BaseFilter",
        )


@dataclasses.dataclass(frozen=True)
class PythonFilter(_BaseFilter):
    """
    Custom python filter

    Attributes:
    func -- Custom python filter
    """

    func: typing.Callable[[typing.Any], bool]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="PythonFilter",
            func=_utilities.config_node_dict_field_value(self.func),
        )


@dataclasses.dataclass(frozen=True)
class _BaseUnitTest(_utilities.ConfigNode):
    """
    Base unit test
    """

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="_BaseUnitTest",
        )


@dataclasses.dataclass(frozen=True)
class JSONUnitTest(_BaseUnitTest):
    """
    Unit test with json content

    Attributes:
    data -- json data
    """

    data: str

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="JSONUnitTest",
            data=_utilities.config_node_dict_field_value(self.data),
        )


@dataclasses.dataclass(frozen=True)
class DictUnitTest(_BaseUnitTest):
    """
    Unit test with python dict content

    Attributes:
    data -- json data
    """

    data: typing.Dict[str, typing.Any]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="DictUnitTest",
            data=_utilities.config_node_dict_field_value(self.data),
        )


@dataclasses.dataclass(frozen=True)
class Rule(_utilities.ConfigNode):
    """
    Define a rule

    Attributes:
    id -- ID for the rule
    severity -- Severity for the rule
    log_types -- Severity for the rule
    filters -- Define event filters for the rule
    unit_tests -- Define event filters for the rule
    """

    id: str
    severity: str
    log_types: typing.List[str]
    filters: typing.Union[_BaseFilter, typing.List[_BaseFilter]]
    unit_tests: typing.Optional[
        typing.Union[_BaseFilter, typing.List[_BaseFilter]]
    ] = None

    def __post_init__(self) -> None:
        _utilities.cache.add("rule", self)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dict(
            __typename="Rule",
            id=_utilities.config_node_dict_field_value(self.id),
            severity=_utilities.config_node_dict_field_value(self.severity),
            log_types=_utilities.config_node_dict_field_value(self.log_types),
            filters=_utilities.config_node_dict_field_value(self.filters),
            unit_tests=_utilities.config_node_dict_field_value(self.unit_tests),
        )
