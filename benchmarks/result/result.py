"""Basic result classes for benchmarking."""

from __future__ import annotations

import sys

import importlib_metadata
from attrs import define, field
from attrs.validators import deep_mapping, instance_of
from pandas import DataFrame

from benchmarks.result import ResultMetadata
from benchmarks.serialization import BenchmarkSerialization


@define(frozen=True)
class Result(BenchmarkSerialization):
    """A single result of the benchmarking."""

    benchmark_identifier: str = field(validator=instance_of(str))
    """The identifier of the benchmark that produced the result."""

    data: DataFrame = field(validator=instance_of(DataFrame))
    """The result of the benchmarked callable."""

    metadata: ResultMetadata = field(validator=instance_of(ResultMetadata))
    """The metadata associated with the benchmark result."""

    python_env: dict[str, str] = field(
        validator=deep_mapping(instance_of(str), instance_of(str), instance_of(dict))
    )
    """The Python environment in which the benchmark was executed."""

    python_version: str = field(default=sys.version, validator=instance_of(str))
    """The Python version in which the benchmark was executed."""

    @python_env.default
    def _default_python_env(self) -> dict[str, str]:
        installed_packages = importlib_metadata.distributions()
        package_dict = {
            dist.metadata["Name"]: dist.version for dist in installed_packages
        }
        return package_dict
