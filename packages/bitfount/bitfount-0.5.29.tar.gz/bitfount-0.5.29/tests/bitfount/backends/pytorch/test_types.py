"""Tests for backends/pytorch/types.py."""
import torch

from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from tests.utils.helper import backend_test, unit_test


@backend_test
@unit_test
class TestAdaptorForPyTorchTensor:
    """Tests for _AdaptorForPyTorchTensor."""

    def test_squeeze(self) -> None:
        """Tests squeeze method."""
        adaptor = _AdaptorForPyTorchTensor(torch.tensor([[1, 2, 3]]))
        new_adaptor = adaptor.squeeze()
        assert isinstance(new_adaptor, _AdaptorForPyTorchTensor)
        # Testing that shape has been reduced from 2 dimensions to 1
        assert len(adaptor.torchtensor.shape) == 2
        assert len(new_adaptor.torchtensor.shape) == 1

    def test_squeeze_axis(self) -> None:
        """Tests squeeze method with axis."""
        adaptor = _AdaptorForPyTorchTensor(torch.zeros(2, 1, 2, 1, 2))
        assert list(adaptor.torchtensor.shape) == [2, 1, 2, 1, 2]

        # Shape does not change because the tensor has not been squeezed
        # in the right dimension
        new_adaptor = adaptor.squeeze(axis=0)
        assert list(new_adaptor.torchtensor.shape) == [2, 1, 2, 1, 2]

        # Shape only changes in dimension 1
        new_adaptor = adaptor.squeeze(axis=1)
        assert list(new_adaptor.torchtensor.shape) == [2, 2, 1, 2]
