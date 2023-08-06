"""Tests `bitfount_model.py`."""
from pathlib import Path
from typing import List, Type

from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.models.bitfount_model import BitfountModel
from tests.utils.helper import unit_test


@unit_test
class TestBitfountModel:
    """Tests BitfountModel class."""

    @fixture
    def bitfount_model_class(self) -> Type[BitfountModel]:
        """Returns a BitfountModel instance."""

        class MyModel(BitfountModel):
            """A test model."""

            @staticmethod
            def _get_import_statements() -> List[str]:
                """Returns a list of import statements."""
                return ["import random_library"]

        return MyModel

    def test_serialize_model_source_code(
        self,
        bitfount_model_class: Type[BitfountModel],
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Tests serialize_model_source_code method."""
        mock_os = mocker.patch("bitfount.models.bitfount_model.os")
        mock_isort = mocker.patch("bitfount.models.bitfount_model.isort")

        filename = tmp_path / "model.py"
        bitfount_model_class.serialize_model_source_code(
            filename, extra_imports=["from blah import blah"]
        )

        mock_os.system.assert_called()  # Called twice
        mock_isort.file.assert_called_once()

        with open(filename, "r") as f:
            model_code = f.read()
            assert "from blah import blah" in model_code
            assert "import random_library" in model_code
