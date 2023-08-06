"""Private SQL query algorithm."""
from __future__ import annotations

import math
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Final,
    List,
    Mapping,
    Optional,
    Tuple,
    cast,
)

from marshmallow import fields
import pandas as pd
import snsql
from snsql import Privacy
import sqlparse

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import SemanticType, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.exceptions import PrivateSqlError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _ModellessAlgorithmMixIn
from bitfount.federated.privacy.differential import (
    DPModellerConfig,
    DPPodConfig,
    _DifferentiallyPrivate,
)
from bitfount.types import T_FIELDS_DICT

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerAlgorithm):
    """Modeller side of the PrivateSqlQuery algorithm."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: Mapping[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Simply returns results."""
        return dict(results)


class _WorkerSide(_BaseWorkerAlgorithm):
    """Worker side of the PrivateSqlQuery algorithm."""

    _SMART_NOISE_TYPE: Final[Mapping[str, Tuple[str, Optional[int]]]] = {
        "int": ("int", 1_000),
        "int32": ("int", 1_000),
        "int64": ("int", 1_000),
        "float": ("float", 1),
        "float32": ("float", 1),
        "float64": ("float", 1),
        "string": ("string", None),
    }

    def __init__(
        self,
        *,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: dict,
        hub: BitfountHub,
        table: Optional[str],
        **kwargs: Any,
    ) -> None:
        self.datasource: BaseSource
        self.pod_identifier: Optional[str] = None
        self.pod_dp: Optional[DPPodConfig] = None
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.hub = hub
        self.table = table
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        datasource.load_data()
        self.datasource = datasource
        if pod_identifier:
            self.pod_identifier = pod_identifier
        if pod_dp:
            self.pod_dp = pod_dp

    def map_types(self, schema: BitfountSchema) -> None:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the single-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        for column in self.column_ranges:
            mapped_type = None
            default_max = None
            for table_name in schema.table_names:
                # Determine what type we have in the schema for the column
                for stype in SemanticType:
                    for feature in schema.get_table_schema(
                        table_name
                    ).get_feature_names(stype):
                        if feature == column:
                            mapped_type = (
                                schema.get_table_schema(table_name)
                                .features[cast(_SemanticTypeValue, stype.value)][
                                    feature
                                ]
                                .dtype.name
                            )
                            break

            if mapped_type is None:
                logger.warning(
                    f"No field named '{column}' present in the schema"
                    "will proceed assuming it is a string."
                )
                mapped_type = "str"

            # Map the type we have to an equivalent for SmartNoise SQL
            sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                mapped_type.lower(), (None, None)
            )
            if not sn_mapped_type:
                logger.warning(
                    f"Type {mapped_type} for column '{column}' is not supported"
                    "defaulting to string type."
                )
                sn_mapped_type = "string"

            self.column_ranges[column]["type"] = sn_mapped_type
            # if there is no specified lower/upper for int/float set defaults
            if "lower" not in self.column_ranges[column] and default_max is not None:
                logger.warning(
                    "Using default lower and upper bound of "
                    f"(0, {default_max}) for field [{column}]"
                )
                self.column_ranges[column]["lower"] = 0
                self.column_ranges[column]["upper"] = default_max

    def map_types_multi(self, schema: BitfountSchema) -> List[str]:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the multi-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        features_added = []
        for table_name, columns in self.column_ranges.items():
            for column in columns:
                mapped_type = None
                default_max = None
                if table_name in schema.table_names:
                    # Determine what type we have in the schema for the column
                    for stype in SemanticType:
                        for feature in schema.get_table_schema(
                            table_name
                        ).get_feature_names(stype):
                            if feature == column:
                                mapped_type = (
                                    schema.get_table_schema(table_name)
                                    .features[cast(_SemanticTypeValue, stype.value)][
                                        feature
                                    ]
                                    .dtype.name
                                )
                                break
                else:
                    logger.warning(
                        f"No table named '{table_name}' present in the schema. "
                        "SQL query will probably fail if a query attempts "
                        "to use this table."
                    )

                if mapped_type is None:
                    logger.warning(
                        f"No field named '{column}' present in the schema"
                        "will proceed assuming it is a string."
                    )
                    mapped_type = "str"

                # Map the type we have to an equivalent for SmartNoise SQL
                sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                    mapped_type.lower(), (None, None)
                )
                if not sn_mapped_type:
                    logger.warning(
                        f"Type {mapped_type} for column '{column}' is not supported"
                        "defaulting to string type."
                    )
                    sn_mapped_type = "string"

                self.column_ranges[table_name][column]["type"] = sn_mapped_type
                features_added.append(column)
                # if there is no specified lower/upper for int/float set defaults
                if (
                    "lower" not in self.column_ranges[table_name][column]
                    and default_max is not None
                ):
                    logger.warning(
                        "Using default lower and upper bound of "
                        f"(0, {default_max}) for field [{column}]"
                    )
                    self.column_ranges[table_name][column]["lower"] = 0
                    self.column_ranges[table_name][column]["upper"] = default_max

        return features_added

    def extend_types(self, schema: BitfountSchema, already_added: List[str]) -> None:
        """Add SmartNoise types for remaining features from Pandas DataTypes.

        In this case, for the features are not all specified in the modeller-supplied
        metadata, map to the appropriate type.
        """
        for table_name in schema.table_names:
            for stype in SemanticType:
                for feature in schema.get_table_schema(table_name).get_feature_names(
                    stype
                ):
                    f_cat = str(stype.value)
                    if feature not in already_added:
                        default_max = None
                        mapped_type = (
                            schema.get_table_schema(table_name)
                            .features[
                                f_cat  # type: ignore[literal-required] # Reason: below
                            ][feature.replace('"', "")]
                            .dtype.name
                        )
                        # Reason: enum value is valid
                        # Only need to deal with numeric types, others already string
                        mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                            mapped_type.lower(), (None, None)
                        )

                        if table_name not in self.column_ranges:
                            self.column_ranges[table_name] = {}
                        self.column_ranges[table_name][feature] = {"type": mapped_type}
                        # If there is no specified lower/upper for int/float, default
                        if default_max is not None:
                            logger.warning(
                                "Using default lower and upper bound of "
                                f"(0,{default_max}) for field [{feature}]"
                            )
                            self.column_ranges[table_name][feature].update({"lower": 0})
                            self.column_ranges[table_name][feature].update(
                                {"upper": default_max}
                            )

    def run(self) -> pd.DataFrame:
        """Executes the SQL query on the `BaseSource`."""
        logger.info("Executing query...")

        if self.pod_identifier is None:
            raise ValueError("No pod identifier - cannot get schema to infer types.")

        # Get the schema from the hub, needed for getting the column data types.
        schema = self.hub.get_pod_schema(self.pod_identifier)
        # Check that modeller-side dp parameters are within the pod config range.
        dp = _DifferentiallyPrivate(
            {"max_epsilon": self.epsilon, "target_delta": self.delta}
        )
        # We initialise dp explicitly above, so dp._dp_config will be of
        # type DPModellerConfig, making it safe to cast.
        dp._dp_config = cast(DPModellerConfig, dp._dp_config)
        if self.pod_dp:
            dp.apply_pod_dp(self.pod_dp)
        else:
            # If there is no pod_pd, we assign to it the epsilon and delta values
            # from the Modeller, as they have been previously checked by the AM.
            self.pod_dp = DPPodConfig(
                max_epsilon=self.epsilon, max_target_delta=self.delta
            )

        # Extract the metadata from the column ranges.
        if self.datasource.multi_table and isinstance(self.datasource, DatabaseSource):
            # Check if there is a join in the query and error out appropriately
            parsed = sqlparse.parse(self.query)
            # If token in query [0] is a keyword, and a join, raise an error
            for tok in parsed[0].tokens:
                if tok.is_keyword:
                    if "JOIN" in tok.value.upper():
                        raise ValueError("JOIN clauses are not supported.")

            # Map the dtypes to types understood by SmartNoise SQL
            already_added = self.map_types_multi(schema)
            # Add the mappings for remaining columns
            self.extend_types(schema, already_added)
            # Set up the metadata dictionary required for SmartNoise SQL
            meta: Dict[str, Dict[str, Dict[str, Dict[str, int]]]] = {
                # "Collection" name
                "Database": {
                    # "Schema" name
                    "public": {
                        # "Table" name - added later
                    }
                }
            }
            # We update the metadata with a copy so we don't modify
            # the original column ranges.
            meta["Database"]["public"].update(self.column_ranges.copy())

            for table in meta["Database"]["public"]:
                meta["Database"]["public"][table]["row_privacy"] = False
        else:
            # Single-table/in-memory path - load the data into memory
            self.datasource.load_data(table_name=self.table)
            df = self.datasource.data

            # Map the dtypes to types understood by SmartNoise SQL
            self.map_types(schema)
            # Set up the metadata dictionary required for SmartNoise SQL
            meta = {
                "Database": {
                    "df": {"df": {"row_privacy": True, "rows": int(len(df.index))}}
                }
            }
            # We update the metadata with a copy so we don't modify
            # the original column ranges.
            meta["Database"]["df"]["df"].update(self.column_ranges.copy())

        # Set default values for the used_epsilon and used_delta
        used_epsilon = float("inf")
        used_delta = float("inf")

        # Initialise epsilon and delta divisors as 1
        delta_div = 1.0
        epsilon_div = 1.0
        # Parameters used for rounding up the divisors
        delta_n = 10
        epsilon_n = 10

        try:
            while (
                used_epsilon > self.pod_dp.max_epsilon
                or used_delta > self.pod_dp.max_target_delta
            ):
                # Configure privacy
                # Note that the parameters are per-column maximums
                privacy = Privacy(
                    epsilon=dp._dp_config.max_epsilon / epsilon_div,
                    delta=dp._dp_config.target_delta / delta_div,
                )
                # Pre-flight the sql query, and compute the privacy cost
                if self.datasource.multi_table and isinstance(
                    self.datasource, DatabaseSource
                ):

                    # Now connect to the database and execute the query.
                    conn = self.datasource.db_conn.con.raw_connection()
                    reader = snsql.from_connection(
                        conn, privacy=privacy, metadata=meta, engine="postgres"
                    )
                    used_epsilon, used_delta = reader.get_privacy_cost(self.query)

                else:

                    reader = snsql.from_df(df, privacy=privacy, metadata=meta)

                    used_epsilon, used_delta = reader.get_privacy_cost(self.query)

                if used_epsilon > self.pod_dp.max_epsilon:
                    # Update epsilon_div to be the result of dividing the used_epsilon
                    # by the maximum allowed value by the pod, rounded up to eps_n
                    # decimals
                    epsilon_div = (
                        math.ceil(
                            used_epsilon / self.pod_dp.max_epsilon * 10**epsilon_n
                        )
                        / 10**epsilon_n
                    )
                    epsilon_n -= 1

                if used_delta > self.pod_dp.max_target_delta and delta_n > 1:
                    # Update delta_div to be the result of dividing the used_delta
                    # by the maximum allowed value by the pod, rounded up to delta_n
                    # decimals
                    delta_div = (
                        math.ceil(
                            used_delta / self.pod_dp.max_target_delta * 10**delta_n
                        )
                        / 10**delta_n
                    )
                    delta_n -= 1
                elif used_delta > self.pod_dp.max_target_delta and delta_n <= 1:
                    # On the last loop, do a bigger division for the delta.
                    delta_div = (
                        math.ceil(
                            used_delta / self.pod_dp.max_target_delta * 10**delta_n
                        )
                        / 10**delta_n
                    ) * 10
                    delta_n -= 1
                # If any of delta_n or epsilon_n are 0, then we have reached
                # the end of our loop, and we raise an error to the user.
                if delta_n < 0:
                    raise PrivateSqlError(
                        "Cannot execute current query given the provided privacy "
                        f"parameter delta={self.delta}). Try again using a "
                        f"smaller value of delta."
                    )
                if epsilon_n < 0:
                    raise PrivateSqlError(
                        "Cannot execute current query given the provided privacy "
                        f"parameter epsilon={self.epsilon}. Try again using a "
                        f"smaller epsilon value."
                    )
            # Log the total values of the privacy budget used.
            logger.federated_info(
                "Total privacy cost for query will be "
                f"(epsilon={used_epsilon}, delta={used_delta})"
            )
            # Log the values of the privacy budget used per column.
            logger.federated_info(
                f"Executing SQL query with epsilon {privacy.epsilon} "
                f"and delta {privacy.delta} applied on each queried column."
            )
            # Execute the Private SQL query
            output = reader.execute(self.query)

        except Exception as ex:
            raise PrivateSqlError(
                "Error executing PrivateSQL query: " f"[{self.query}], got error [{ex}]"
            )
        return cast(pd.DataFrame, output)


class PrivateSqlQuery(_BaseAlgorithmFactory, _ModellessAlgorithmMixIn):
    """Simple algorithm for running a SQL query on a table, with privacy.

    Args:
        query: The SQL query to execute.
        epsilon: The maximum epsilon to use for the privacy budget.
        delta: The target delta to use for the privacy budget.
        column_ranges: A dictionary of column names and their ranges.

    Raises:
        PrivateSqlError: If there is an error executing the private SQL query (e.g. DP
            misconfiguration or bad query specified).
        ValueError: If a pod identifier is not supplied, or if a join is attempted.

    :::note
    The values provided for the privacy budget (i.e. epsilon and delta)
    will be applied individually to all columns included in the SQL query provided.
    If the total values of the epsilon and delta exceed the maximum allowed by the pod,
    the provided values will be reduced to the maximum values required to remain
    within the allowed privacy budget.
    :::
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "query": fields.Str(),
        "epsilon": fields.Float(allow_nan=True),
        "delta": fields.Float(allow_nan=True),
        "column_ranges": fields.Dict(),
        "table": fields.Str(allow_none=True),
    }
    query: str
    """The SQL query to execute."""
    epsilon: float
    """The maximum epsilon to use for the privacy budget."""
    delta: float
    """The target delta to use for the privacy budget."""
    column_ranges: dict
    """A dictionary of column names and their ranges."""
    table: Optional[str]
    """The table on which the query will be executed."""

    def __init__(
        self,
        *,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: dict,
        **kwargs: Any,
    ):
        super().__init__()
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.table: Optional[str] = kwargs.get("table")

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the PrivateSqlQuery algorithm.

        Args:
            **kwargs: Additional keyword arguments to pass to the modeller side.
        """
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the PrivateSqlQuery algorithm.

        Args:
            **kwargs: Additional keyword arguments to pass to the worker side. `hub`
                must be one of these keyword arguments which provides a `BitfountHub`
                instance.
        """
        return _WorkerSide(
            query=self.query,
            epsilon=self.epsilon,
            delta=self.delta,
            column_ranges=self.column_ranges,
            table=self.table,
            **kwargs,
        )
