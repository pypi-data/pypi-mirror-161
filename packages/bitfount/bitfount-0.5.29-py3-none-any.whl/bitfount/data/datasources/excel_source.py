"""Module containing ExcelSource class.

ExcelSource class handles loading of Excel data.
"""
import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Union, cast

import pandas as pd
from pydantic import AnyUrl

from bitfount.data.datasources.base_source import MultiTableSource
from bitfount.data.types import _SingleOrMulti
from bitfount.types import _Dtypes

logger = logging.getLogger(__name__)


class ExcelSource(MultiTableSource):
    """Data source for loading excel files.

    Args:
        path: The path or URL to the excel file.
        sheet_name: The name(s) of the sheet(s) to load. If not provided, the
            all sheets will be loaded.
        column_names: The names of the columns if not using the first row of the sheet.
            Can only be used for single sheet excel files.
        dtype: The dtypes of the columns.
        **read_excel_kwargs: Additional arguments to be passed to `pandas.read_excel`.

    Raises:
        TypeError: If the path does not have the correct extension denoting an excel
            file.
        ValueError: If multiple sheet names are provided and column names are also
            provided.
        ValueError: If sheets are referenced which do not exist in the excel file.

    :::info

    You must install a backend library to read excel files to use this data source.
    Currently supported engines are “xlrd”, “openpyxl”, “odf” and “pyxlsb”.

    :::

    :::info

    By default, the first row is used as the column names unless `column_names` or the
    `header` keyword argument is provided.

    :::
    """

    def __init__(
        self,
        path: Union[os.PathLike, AnyUrl, str],
        sheet_name: Optional[_SingleOrMulti[str]] = None,
        column_names: Optional[List[str]] = None,
        dtype: Optional[_Dtypes] = None,
        read_excel_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        if not str(path).endswith(
            (".xls", ".xlsx", "xlsm", "xlsb", "odf", "ods", "odt")
        ):
            raise TypeError("Please provide a Path or URL to an Excel file.")
        self.file = pd.ExcelFile(str(path))
        self.sheet_name = sheet_name

        if not set(self.table_names).issubset(set(self.file.sheet_names)):
            raise ValueError(
                f"Sheet(s) "
                f"{', '.join([i for i in self.table_names if i not in self.file.sheet_names])}"  # noqa: B950
                f" were not found in the Excel file."
            )

        if not read_excel_kwargs:
            read_excel_kwargs = {}

        if self.multi_table and column_names:
            raise ValueError(
                "Column names can only be provided "
                "if a single sheet name is provided."
            )

        if column_names:
            read_excel_kwargs["names"] = column_names
            read_excel_kwargs["header"] = None

        if dtype:
            read_excel_kwargs["dtype"] = dtype

        self.read_excel_kwargs = read_excel_kwargs
        self.datastructure_table_name: Optional[str] = None

    @property
    def table_names(self) -> List[str]:
        """Excel sheet names in datasource."""
        if self.sheet_name is not None:
            if isinstance(self.sheet_name, list):
                return [i for i in self.sheet_name]

            elif isinstance(self.sheet_name, str):
                return [self.sheet_name]

        return cast(List[str], self.file.sheet_names)

    def _validate_table_name(self, table_name: Optional[str]) -> None:
        """Validate the table name exists in the excel workbook.

        Args:
            table_name: The name of the table.

        Raises:
            ValueError: If the data is multi-table but no table name provided.
            ValueError: If the table name is not found in the data.
        """
        if table_name is None:
            raise ValueError("No table name provided for multi-table datasource.")
        elif table_name not in self.table_names:
            raise ValueError(
                f"Table name {table_name} not found in the data. "
                f"Available tables: {', '.join(self.table_names)}"
            )

    def get_data(
        self, table_name: Optional[str] = None, **kwargs: Any
    ) -> Optional[pd.DataFrame]:
        """Loads and returns data from Excel dataset.

        Returns:
            A DataFrame-type object which contains the data.

        Raises:
            ValueError: If the table name provided does not exist.
        """
        df: pd.DataFrame
        if not self.multi_table:

            # If `sheet_name` is not a string, `pd.read_excel` returns a dictionary
            # of DataFrames instead of a single DataFrame so we ensure it is a string
            if isinstance(self.sheet_name, str):
                table_name = self.sheet_name
            elif isinstance(self.sheet_name, list):
                table_name = self.sheet_name[0]
            else:
                table_name = self.table_names[0]

            df = pd.read_excel(
                self.file, sheet_name=table_name, **self.read_excel_kwargs
            )

        else:
            self._validate_table_name(table_name)
            df = pd.read_excel(
                self.file, sheet_name=table_name, **self.read_excel_kwargs
            )

        return df

    def get_values(
        self,
        col_names: List[str],
        table_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in Excel dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.

        Raises:
            ValueError: If the table name provided does not exist.
        """
        df = cast(pd.DataFrame, self.get_data(table_name))
        return {col: df[col].unique() for col in col_names}

    def get_column(
        self, col_name: str, table_name: Optional[str] = None, **kwargs: Any
    ) -> pd.Series:
        """Loads and returns single column from Excel dataset.

        Args:
            col_name: The name of the column which should be loaded.

        Returns:
            The column request as a series.

        Raises:
            ValueError: If the table name provided does not exist.
        """
        df = cast(pd.DataFrame, self.get_data(table_name))
        return df[col_name]

    def get_dtypes(self, table_name: Optional[str] = None, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types of the Excel dataset.

        Returns:
            A mapping from column names to column types.

        Raises:
            ValueError: If the table name provided does not exist.
        """
        df = cast(pd.DataFrame, self.get_data(table_name))
        data = df.convert_dtypes()
        dtypes: _Dtypes = data.dtypes.to_dict()
        return dtypes

    def __len__(self) -> int:
        if self._data_is_loaded:
            return len(self.data)
        elif not self.multi_table:
            data = self.get_data()
            assert data is not None  # nosec[assert_used]
            self.data = data
            return len(self.data)

        raise ValueError("Can't ascertain length of multi-table Excel dataset.")

    @property
    def multi_table(self) -> bool:
        """Attribute to specify whether the datasource is multi table."""
        if self.sheet_name is not None:
            return not isinstance(self.sheet_name, str) and len(self.sheet_name) > 1

        return len(self.table_names) > 1
