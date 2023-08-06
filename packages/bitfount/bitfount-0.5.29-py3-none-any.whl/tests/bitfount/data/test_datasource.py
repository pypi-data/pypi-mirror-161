"""Tests datasource.py."""
from functools import partial
from pathlib import Path
import re
from typing import Any, Callable, Dict
from unittest.mock import Mock, PropertyMock

from _pytest.tmpdir import TempPathFactory
from intermine.webservice import Service
import pandas as pd
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy
from sqlalchemy.exc import ArgumentError

from bitfount.data.datasources.csv_source import CSVSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasources.excel_source import ExcelSource
from bitfount.data.datasources.intermine_source import IntermineSource
from bitfount.data.exceptions import DataNotLoadedError
from bitfount.data.types import DataPathModifiers
from bitfount.data.utils import DatabaseConnection, _hash_str
from tests.utils import PytestRequest
from tests.utils.helper import (
    DATASET_ROW_COUNT,
    create_dataset,
    integration_test,
    unit_test,
)


@fixture(scope="module")
def dataframe() -> pd.DataFrame:
    """Dataframe fixture."""
    return create_dataset()


@unit_test
class TestBaseSource:
    """Tests core BaseSource functionality with a CSV file."""

    @fixture(scope="function", params=["pandas", "image"])
    def datasource_generator(
        self, request: PytestRequest
    ) -> Callable[..., DataFrameSource]:
        """Dataset loader for use in tests."""
        image = False
        if request.param == "image":
            image = True
        data = create_dataset(image=image)
        if image:
            return partial(DataFrameSource, data, seed=420)

        return partial(DataFrameSource, data, seed=420)

    def test_tabular_datasource_errors(self) -> None:
        """Checks BaseSource object errors via wrong first argument."""
        with pytest.raises(TypeError):
            DataFrameSource("test1", seed=420)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950

        with pytest.raises(TypeError):
            test_path = Path("/my/root/directory")
            DataFrameSource(test_path, seed=420)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950

    def test_datasource_modifiers_path_prefix(self, dataframe: pd.DataFrame) -> None:
        """Tests functionality for providing image path prefix."""
        dataframe["image"] = "image_file_name"
        modifiers = {"image": DataPathModifiers({"prefix": "/path/to/"})}
        datasource = DataFrameSource(dataframe, seed=420, modifiers=modifiers)
        datasource.load_data()
        assert len(datasource.data["image"].unique()) == 1
        assert datasource.data["image"].unique()[0] == "/path/to/image_file_name"

    def test_image_datasource_ext_suffix(self, dataframe: pd.DataFrame) -> None:
        """Tests functionality for finding images by file extension."""
        dataframe["image"] = "image_file_name"
        modifiers = {"image": DataPathModifiers({"suffix": ".jpeg"})}
        datasource = DataFrameSource(dataframe, seed=420, modifiers=modifiers)
        datasource.load_data()
        assert len(datasource.data["image"].unique()) == 1
        assert datasource.data["image"].unique()[0] == "image_file_name.jpeg"

    def test_image_datasource_ext_prefix_suffix(self, dataframe: pd.DataFrame) -> None:
        """Tests functionality for finding images by file extension."""
        dataframe["image"] = "image_file_name"
        modifiers = {
            "image": DataPathModifiers({"prefix": "/path/to/", "suffix": ".jpeg"})
        }
        datasource = DataFrameSource(dataframe, seed=420, modifiers=modifiers)
        datasource.load_data()
        assert len(datasource.data["image"].unique()) == 1
        assert datasource.data["image"].unique()[0] == "/path/to/image_file_name.jpeg"

    def test_multiple_img_datasource_modifiers(self) -> None:
        """Tests functionality for finding multiple images by file extension."""
        data = create_dataset(multiimage=True, img_size=1)
        data["image1"] = "image1_file_name"
        data["image2"] = "image2_file_name"
        modifiers = {
            "image1": DataPathModifiers({"prefix": "/path/to/"}),
            "image2": DataPathModifiers({"suffix": ".jpeg"}),
        }
        datasource = DataFrameSource(data, seed=420, modifiers=modifiers)
        datasource.load_data()
        assert len(datasource.data["image1"].unique()) == 1
        assert datasource.data["image1"].unique()[0] == "/path/to/image1_file_name"
        assert len(datasource.data["image2"].unique()) == 1
        assert datasource.data["image2"].unique()[0] == "image2_file_name.jpeg"

    def test_tabular_datasource_read_csv_correctly(
        self, dataframe: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Tests CSVSource loading from csv."""
        file_path = tmp_path / "tabular_data_test.csv"
        dataframe.to_csv(file_path)
        ds = CSVSource(file_path)
        ds.load_data()
        assert ds.data is not None

    def test_ignored_cols_list_excluded_from_df(self, dataframe: pd.DataFrame) -> None:
        """Tests that a list of ignore_cols are ignored in the data."""
        dataframe["image"] = "image_file_name"
        ignore_cols = ["N", "O", "P"]
        datasource = DataFrameSource(
            dataframe,
            seed=420,
            ignore_cols=ignore_cols,
        )
        datasource.load_data()
        assert not any(item in datasource.data.columns for item in ignore_cols)

    def test_ignored_single_col_list_excluded_from_df(
        self, dataframe: pd.DataFrame
    ) -> None:
        """Tests that a str ignore_cols is ignored in the data."""
        dataframe["image"] = "image_file_name"
        ignore_cols = "N"
        datasource = DataFrameSource(
            dataframe,
            seed=420,
            ignore_cols=ignore_cols,
        )
        datasource.load_data()
        assert ignore_cols not in datasource.data.columns

    def test_hash(
        self,
        datasource_generator: Callable[..., DataFrameSource],
        mocker: MockerFixture,
    ) -> None:
        """Tests hash is called on the dtypes."""
        datasource = datasource_generator()
        expected_hash = f"hash_{id(datasource._table_hashes)}"
        mock_hash_function: Mock = mocker.patch(
            "bitfount.data.datasources.base_source._generate_dtypes_hash",
            return_value=expected_hash,
            autospec=True,
        )
        datasource.get_dtypes()

        actual_hash = datasource.hash

        # Check hash is expected return and how it was called
        assert actual_hash == _hash_str(str([expected_hash]))
        mock_hash_function.assert_called_once()

    def test_get_dtypes_ignores_cols(
        self,
        datasource_generator: Callable[..., DataFrameSource],
        mocker: MockerFixture,
    ) -> None:
        """Tests get_dtypes drops _ignore_cols."""
        datasource = datasource_generator()
        datasource._ignore_cols = ["A"]
        assert "A" in datasource.get_data().columns

        result = datasource.get_dtypes()

        assert "A" not in result.keys()

    def test_get_column_applies_modifiers(
        self,
        datasource_generator: Callable[..., DataFrameSource],
        mocker: MockerFixture,
    ) -> None:
        """Tests get_column applies modifiers."""
        datasource = datasource_generator()
        prefix = "/path/to/"
        datasource._modifiers = {"A": DataPathModifiers({"prefix": prefix})}
        expected_result = prefix + datasource.get_data()["A"].astype(str)

        result = datasource.get_column("A")

        assert all(result == expected_result)

    def test_get_data_failes(self, mock_engine: Mock) -> None:
        """Test data raises error when data not set."""
        db_conn = DatabaseConnection(mock_engine)
        datasource = DatabaseSource(db_conn)
        with pytest.raises(
            DataNotLoadedError,
            match="Data is not loaded yet. Please call `load_data` first.",
        ):
            datasource.data


class TestDatabaseSource:
    """Tests DatabaseSource."""

    @unit_test
    @pytest.mark.parametrize(
        "params, result",
        [
            ({"table_names": ["dummy_data"]}, "SELECT * FROM dummy_data"),
            ({"query": "SELECT * FROM dummy_data"}, "SELECT * FROM dummy_data"),
        ],
    )
    def test_query(
        self, mock_engine: Mock, params: Dict[Any, Any], result: Any
    ) -> None:
        """Test query returns correct result."""
        db_conn = DatabaseConnection(mock_engine, **params)
        datasource = DatabaseSource(db_conn, seed=420)
        assert datasource.query == result

    @unit_test
    def test_query_datastructure_query(self, mock_engine: Mock) -> None:
        """Test query returns datastructure query."""
        db_conn = DatabaseConnection(
            mock_engine,
        )
        datastructure_query = "SELECT * FROM dummy_data"
        datasource = DatabaseSource(db_conn, seed=420)
        datasource.datastructure_query = datastructure_query
        assert datasource.query == datastructure_query

    @unit_test
    def test_hash_multitable_raises_value_error(self, mock_engine: Mock) -> None:
        """Tests hash function raises `DataNotLoadedError` if data is not loaded."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        datasource = DatabaseSource(db_conn, seed=420)
        with pytest.raises(DataNotLoadedError):
            datasource.hash

    @unit_test
    def test_value_error_raised_if_no_table_name_provided_for_multitable_datasource(
        self, mock_engine: Mock
    ) -> None:
        """Test ValueError raised if no table_name for multi-table DatabaseSource."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.load_data()
        with pytest.raises(
            ValueError, match="No table name provided for multi-table datasource."
        ):
            ds.get_dtypes()

    @unit_test
    def test_value_error_raised_if_table_not_found_for_multitable_datasource(
        self, mock_engine: Mock
    ) -> None:
        """Tests ValueError raised if table missing for multi-table DatabaseSource."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.load_data()
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Table name not_a_table not found in the data. "
                + "Available tables: ['dummy_data', 'dummy_data_2']"
            ),
        ):
            ds.get_dtypes(table_name="not_a_table")

    @unit_test
    def test_invalid_connection_string_errors(self) -> None:
        """Test DatabaseSource errors with invalid conn string."""
        invalid_connection_str = "random_str"
        with pytest.raises(
            ArgumentError,
            match=(
                f"Invalid db_conn. db_conn: {invalid_connection_str} "
                "must be sqlalchemy compatible database url, see: .*"
            ),
        ):
            DatabaseSource(invalid_connection_str)

    @integration_test
    def test_instantiation_works_with_db_conn_as_string(
        self, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Test DataSource can be created with valid connection string."""
        expected_table_names = ["dummy_data", "dummy_data_2"]
        connection_str = str(db_session.url)
        assert isinstance(connection_str, str)
        ds = DatabaseSource(connection_str)

        # Correctly read table from connection string
        assert ds.table_names == expected_table_names

    @integration_test
    def test_mock_get_dtypes_reads_and_returns_table_schema(
        self, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Tests that the `get_dtypes` method returns a dictionary.

        Also checks that the dtypes hash is added appropriately.
        """
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)

        assert len(ds._table_hashes) == 0
        assert isinstance(ds.get_dtypes(table_name="dummy_data"), dict)
        assert len(ds._table_hashes) == 1

    @integration_test
    def test_get_dtypes_reads_and_returns_table_schema(
        self, db_session: sqlalchemy.engine.base.Engine
    ) -> None:
        """Tests that the `get_dtypes` method returns a dictionary.

        Also checks that the dtypes hash is added appropriately.
        """
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        assert len(ds._table_hashes) == 0
        table = ds.get_dtypes(table_name="dummy_data")
        assert isinstance(table, dict)
        assert len(ds._table_hashes) == 1

    @unit_test
    def test_get_column(self, mock_engine: Mock, mocker: MockerFixture) -> None:
        """Test get_column returns column."""
        # Creates a multitable DatabaseConnection object
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        datasource = DatabaseSource(db_conn)
        col_name = "A"
        mock_table: Mock = mocker.patch(
            "bitfount.data.datasources.database_source.Table",
            autospec=True,
        )
        mock_table.return_value.columns = {col_name: None}
        mock_session: Mock = mocker.patch(
            "bitfount.data.datasources.database_source.Session",
            autospec=True,
        )
        mock_result = [(1,), (2,), (3,)]
        mock_session.return_value.__enter__.return_value.query.return_value = (
            mock_result
        )

        result = datasource.get_column(col_name=col_name, table_name="dummy_data")

        assert all(result == pd.Series([1, 2, 3]))
        mock_table.assert_called_once()
        mock_session.assert_called_once()

    @unit_test
    def test_len_magic_method(self, mock_engine: Mock, mocker: MockerFixture) -> None:
        """Tests that __len__ magic method returns correct row count."""
        # Mocks `execute` method on the SQLAlchemy connection object and the
        # `scalar_one` method on the resulting cursor result to return the
        # dataset row count
        mock_db_connection = Mock()
        mock_result = Mock()
        mock_result.scalar_one.return_value = DATASET_ROW_COUNT
        mock_db_connection.execute.return_value = mock_result
        mock_engine.execution_options.return_value = mock_engine

        # Creates a multitable DatabaseConnection object
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        # Mocks `connect` method and resulting context manager on SQLAlchemy Engine
        mocker.patch.object(
            db_conn.con, "connect"
        ).return_value.__enter__.return_value = mock_db_connection
        loader = DatabaseSource(db_conn)

        # Calls __len__ method on loader
        dataset_length = len(loader)

        # Makes assertions on call stack in order
        # Ignoring mypy errors because `connect` has been patched to return a Mock
        db_conn.con.connect.assert_called_once()  # type: ignore[attr-defined] # Reason: see above # noqa: B950
        db_conn.con.connect.return_value.__enter__.assert_called_once()  # type: ignore[attr-defined]  # Reason: see above # noqa: B950
        mock_db_connection.execute.assert_called_once()
        mock_result.scalar_one.assert_called_once()

        # Makes assertion on final result
        assert dataset_length == DATASET_ROW_COUNT

    @unit_test
    def test_validate_table_name_raises_value_error_if_table_name_is_none(
        self, mock_engine: Mock
    ) -> None:
        """Tests that ValueError is raised if there is no table name provided."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        datasource = DatabaseSource(db_conn)
        with pytest.raises(
            ValueError, match="No table name provided for multi-table datasource."
        ):
            datasource._validate_table_name(None)

    @unit_test
    def test_validate_table_name_raises_value_error_if_tables_dont_exist(
        self, mock_engine: Mock
    ) -> None:
        """Tests that ValueError is raised if there are no tables."""
        db_conn = DatabaseConnection(
            mock_engine,
            query="DUMMY QUERY",
        )
        loader = DatabaseSource(db_conn)
        with pytest.raises(
            ValueError, match="Database Connection is not aware of any tables."
        ):
            loader._validate_table_name("dummy_data")

    @unit_test
    def test_validate_table_name_raises_value_error_if_table_name_not_found(
        self, mock_engine: Mock
    ) -> None:
        """Tests that ValueError is raised if the table name is not found."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        loader = DatabaseSource(db_conn)
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Table name blah not found in the data. "
                "Available tables: ['dummy_data', 'dummy_data_2']",
            ),
        ):
            loader._validate_table_name("blah")


@unit_test
class TestCSVSource:
    """Tests CSVSource."""

    @fixture
    def csv_source(self, dataframe: pd.DataFrame, tmp_path: Path) -> CSVSource:
        """CSVSource."""
        file_path = tmp_path / "tabular_data_test.csv"
        dataframe.to_csv(file_path, index=False)
        datasource = CSVSource(file_path, read_csv_kwargs={"parse_dates": ["Date"]})
        return datasource

    def test_len(self, csv_source: CSVSource) -> None:
        """Tests that __len__ magic method returns correct row count."""
        assert len(csv_source) == DATASET_ROW_COUNT

    def test_get_data(self, csv_source: CSVSource, dataframe: pd.DataFrame) -> None:
        """Test get_data returns dataframe."""
        dataframe["Date"] = pd.to_datetime(dataframe["Date"])
        result = csv_source.get_data()
        pd.testing.assert_frame_equal(dataframe, result)

    def test_get_column(self, csv_source: CSVSource, dataframe: pd.DataFrame) -> None:
        """Test get_column returns column."""
        column = "A"
        result = csv_source.get_column(column)
        assert all(dataframe[column] == result)

    def test_get_dtypes(self, csv_source: CSVSource, dataframe: pd.DataFrame) -> None:
        """Test get_dtypes works."""
        result = csv_source.get_dtypes()
        assert isinstance(result, dict)
        for col in dataframe.columns:
            assert col in result.keys()

    def test_multitable(self, csv_source: CSVSource) -> None:
        """Test multi_table for CSVSource."""
        assert not csv_source.multi_table


@unit_test
class TestDataFrameSource:
    """Tests DataFrameSource."""

    def test_len(self, dataframe: pd.DataFrame) -> None:
        """Tests that __len__ magic method returns correct row count."""
        loader = DataFrameSource(dataframe)
        assert len(loader) == DATASET_ROW_COUNT


@unit_test
class TestIntermineSource:
    """Tests IntermineSource."""

    @fixture
    def intermine_source(
        self, dataframe: pd.DataFrame, mocker: MockerFixture
    ) -> IntermineSource:
        """IntermineSource."""
        service_url = "https://beta.humanmine.org/humanmine"
        mock_service = mocker.patch(
            "bitfount.data.datasources.intermine_source.Service"
        )
        mock_service.get_template_by_user.return_value = Service(
            "https://beta.humanmine.org/humanmine"
        ).get_template("Gene_Protein")
        datasource = IntermineSource(service_url, None)
        mocker.patch.object(
            IntermineSource, "table_names", PropertyMock(return_value=["table_name"])
        )
        mocker.patch.object(IntermineSource, "_template_to_df", return_value=dataframe)

        datasource.template_to_user_map = {"table_name": "user1"}
        return datasource

    def test_len(self, intermine_source: IntermineSource) -> None:
        """Tests that __len__ magic method returns correct row count."""
        intermine_source.load_data(table_name="table_name")
        assert len(intermine_source) == DATASET_ROW_COUNT

    def test_get_data(self, intermine_source: IntermineSource) -> None:
        """Test get_data returns dataframe."""
        result = intermine_source.get_data(table_name="table_name")
        assert isinstance(result, pd.DataFrame)

    def test__validate_table_name_no_table_name(
        self, intermine_source: IntermineSource
    ) -> None:
        """Test get_data raises ValueError when no table_name specified."""
        with pytest.raises(
            ValueError, match="No table name provided for Intermine service."
        ):
            intermine_source._validate_table_name()

    def test_get_data_service_with_no_templates(
        self, intermine_source: IntermineSource, mocker: MockerFixture
    ) -> None:
        """Test get_data raises ValueError the service has no templates."""
        mock_table_names = PropertyMock(return_value=[])
        mocker.patch.object(IntermineSource, "table_names", mock_table_names)
        with pytest.raises(
            ValueError, match="Service .* did not return any templates."
        ):
            intermine_source.get_data(table_name="table_name")

    def test_get_data_service_with_invalid_table_name(
        self, intermine_source: IntermineSource
    ) -> None:
        """Test get_data raises ValueError with invalid table name."""
        with pytest.raises(
            ValueError,
            match=(
                "Template name invalid_table_name not found in service: .*. "
                "Available tables: .*"
            ),
        ):
            intermine_source.get_data(table_name="invalid_table_name")

    def test_get_column(self, intermine_source: IntermineSource) -> None:
        """Test get_column returns column."""
        column = "A"
        result = intermine_source.get_column(column, table_name="table_name")
        assert isinstance(result, pd.Series)

    def test_get_column_no_table_name(self, intermine_source: IntermineSource) -> None:
        """Test get_column raises ValueError when no table_name specified."""
        column = "Gene.symbol"
        with pytest.raises(ValueError, match="Expected parameter: table_name."):
            intermine_source.get_column(column)

    def test_get_dtypes(self, intermine_source: IntermineSource) -> None:
        """Test get_dtypes works."""
        result = intermine_source.get_dtypes(table_name="table_name")
        assert isinstance(result, dict)

    def test_get_values(self, intermine_source: IntermineSource) -> None:
        """Test get_values works."""
        result = intermine_source.get_values(col_names=["A"], table_name="table_name")
        assert isinstance(result, dict)

    def test_multitable(
        self, intermine_source: IntermineSource, mocker: MockerFixture
    ) -> None:
        """Test multi_table for IntermineSource."""
        mock_table_names = PropertyMock(return_value=["table_1", "table_2"])
        mocker.patch.object(IntermineSource, "table_names", mock_table_names)
        assert intermine_source.multi_table

    def test_multitable_false_for_single_template(
        self, intermine_source: IntermineSource
    ) -> None:
        """Test multi_table for single table IntermineSource."""
        assert not intermine_source.multi_table

    def test__check_duplicate_templates(self, mocker: MockerFixture) -> None:
        """Test ValueError raised when there are duplicate template names."""
        service_url = "https://beta.humanmine.org/humanmine"
        mock_service = mocker.patch(
            "bitfount.data.datasources.intermine_source.Service"
        )
        duplicate_table_names = ["table_name"] * 2
        mocker.patch.object(
            IntermineSource,
            "table_names",
            PropertyMock(return_value=duplicate_table_names),
        )
        expected_err = (
            "Duplicated template name: 'table_name', found in service. "
            "Template names must have unique names."
        )
        with pytest.raises(ValueError, match=expected_err):
            IntermineSource(service_url, None)
        mock_service.assert_called_once_with(service_url, token=None)


@unit_test
class TestExcelSource:
    """Tests ExcelSource."""

    @fixture(scope="class")
    def single_table_excel_file(
        self, tmp_path_factory: TempPathFactory, dataframe: pd.DataFrame
    ) -> Path:
        """Path to single table excel file."""
        tmp_path = tmp_path_factory.mktemp("temp_excel")
        filename = tmp_path / "test.xlsx"
        dataframe.to_excel(filename, index=False, sheet_name="Sheet1")
        return filename

    @fixture(scope="class")
    def multi_table_excel_file(
        self, tmp_path_factory: TempPathFactory, dataframe: pd.DataFrame
    ) -> Path:
        """Path to multi table excel file."""
        tmp_path = tmp_path_factory.mktemp("temp_excel")
        filename = tmp_path / "test.xlsx"
        with pd.ExcelWriter(filename) as writer:  # type: ignore[abstract] # Reason: This is the documented usage. # noqa: B950
            dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
            dataframe.to_excel(writer, index=False, sheet_name="Sheet2")

        return filename

    @fixture(scope="class")
    def single_table_excel_source(self, single_table_excel_file: Path) -> ExcelSource:
        """Single Table ExcelSource."""
        source = ExcelSource(single_table_excel_file, sheet_name="Sheet1")
        assert not source.multi_table
        return source

    @fixture(scope="class")
    def multi_table_excel_source(self, multi_table_excel_file: Path) -> ExcelSource:
        """Multi Table ExcelSource."""
        source = ExcelSource(multi_table_excel_file, sheet_name=["Sheet1", "Sheet2"])
        assert source.multi_table
        return source

    def test_excel_source_raises_type_error_if_wrong_file_extension(self) -> None:
        """Test ExcelSource raises TypeError if wrong file extension."""
        with pytest.raises(
            TypeError, match="Please provide a Path or URL to an Excel file."
        ):
            ExcelSource("test.txt")

    def test_multi_table_excel_source_raises_value_error_if_column_names_provided(
        self, multi_table_excel_file: Path
    ) -> None:
        """Test Multi Table ExcelSource raises ValueError if column names provided."""
        with pytest.raises(
            ValueError,
            match="Column names can only be provided if a single sheet name is provided.",  # noqa: B950
        ):
            ExcelSource(
                multi_table_excel_file,
                sheet_name=["Sheet1", "Sheet2"],
                column_names=["A"],
            )

    @pytest.mark.parametrize("multi_table", [True, False])
    def test_excel_source_raises_value_error_if_referenced_sheets_are_missing(
        self,
        multi_table: bool,
        multi_table_excel_file: Path,
        single_table_excel_file: Path,
    ) -> None:
        """Test ExcelSource raises ValueError if referenced sheets are missing."""
        with pytest.raises(
            ValueError,
            match=re.escape("Sheet(s) Sheet3 were not found in the Excel file."),
        ):
            if multi_table:
                ExcelSource(
                    multi_table_excel_file,
                    sheet_name=["Sheet1", "Sheet2", "Sheet3"],  # Sheet3 is missing
                )
            else:
                ExcelSource(
                    single_table_excel_file,
                    sheet_name=["Sheet3"],  # Sheet3 is missing
                )

    def test_column_names_override_the_ones_in_the_excel_file(
        self, single_table_excel_file: Path
    ) -> None:
        """Test column names override the ones in the excel file."""
        new_column_names = [str(i) for i in range(16)]
        datasource = ExcelSource(
            single_table_excel_file,
            column_names=new_column_names,
            read_excel_kwargs={"skiprows": 1},
        )

        df = datasource.get_data()
        assert df is not None
        assert list(df.columns) == new_column_names

    def test_multi_table_get_data_raises_value_error_if_table_name_not_provided(
        self, multi_table_excel_source: ExcelSource
    ) -> None:
        """Test Multi Table ExcelSource raises ValueError if table name not provided."""
        with pytest.raises(
            ValueError,
            match="No table name provided for multi-table datasource.",
        ):
            multi_table_excel_source.get_data()

    def test_multi_table_get_data_raises_value_error_if_table_name_not_recognised(
        self, multi_table_excel_source: ExcelSource
    ) -> None:
        """Test Multi-Table ExcelSource raises ValueError if table name not recognised."""  # noqa: B950
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Table name Table3 not found in the data. "
                "Available tables: Sheet1, Sheet2"
            ),
        ):
            multi_table_excel_source.get_data("Table3")

    @pytest.mark.parametrize("multi_table", [True, False])
    def test_get_values(
        self,
        multi_table: bool,
        multi_table_excel_source: ExcelSource,
        single_table_excel_source: ExcelSource,
    ) -> None:
        """Test get_values method works as expected."""
        if multi_table:
            values = multi_table_excel_source.get_values(["A"], "Sheet1")
        else:
            values = single_table_excel_source.get_values(["A"])

        assert isinstance(values, dict)
        assert len(values["A"]) == len(set(values["A"]))  # type: ignore[arg-type] # Reason: Len methods is available. # noqa: B950

    @pytest.mark.parametrize("multi_table", [True, False])
    def test_get_column(
        self,
        multi_table: bool,
        multi_table_excel_source: ExcelSource,
        single_table_excel_source: ExcelSource,
    ) -> None:
        """Test get_column method works as expected."""
        if multi_table:
            values = multi_table_excel_source.get_column("A", "Sheet1")
        else:
            values = single_table_excel_source.get_column("A")

        assert isinstance(values, pd.Series)
        assert len(values) == DATASET_ROW_COUNT

    @pytest.mark.parametrize("multi_table", [True, False])
    def test_get_dtypes(
        self,
        multi_table: bool,
        multi_table_excel_source: ExcelSource,
        single_table_excel_source: ExcelSource,
    ) -> None:
        """Test get_dtypes method works as expected."""
        if multi_table:
            dtypes = multi_table_excel_source.get_dtypes("Sheet1")
        else:
            dtypes = single_table_excel_source.get_dtypes()

        assert isinstance(dtypes, dict)

    @pytest.mark.parametrize("multi_table", [True, False])
    def test_len_magic_method(
        self,
        multi_table: bool,
        multi_table_excel_source: ExcelSource,
        single_table_excel_source: ExcelSource,
    ) -> None:
        """Test len magic method works as expected."""
        if multi_table:
            with pytest.raises(
                ValueError, match="Can't ascertain length of multi-table Excel dataset."
            ):
                len(multi_table_excel_source)

            multi_table_excel_source.load_data(table_name="Sheet1")
            length = len(multi_table_excel_source)
        else:
            length = len(single_table_excel_source)

        assert length == DATASET_ROW_COUNT
