"""RSA Blinding Private Set intersection.

Order of operations:
    1. Modeller sends the task request to the worker, containing
        the columns on which the intersection should be performed.
    2. Worker generates an RSA key pair, and sends the public key
        to the modeller, keeping the private key to themself.
    3 (Worker Side). Worker hashes and uses his private key to encrypt each
        row for the relevant columns, and then hashes again the obtained values.
    3 (Modeller Side). Modeller receives the public key from the pod. Then he
        chooses random factors (as many as the size of the rows
        in his data), which he encrypts using the public key.
        He then hashes each row of his input and multiplies it
        with the encrypted random factors, which is referred
        to as blinding.
    4. Modeller sends his blinded inputs to the worker.
    5. Worker receives the blinded inputs from the modeller.
        He first encrypts the blinded values using his private
        key, and then hashes each of the results. He then sends
        the list of blinded hashed values and the list of
        hashed values from step 3 to the modeller.
    6. Modeller receives the two lists from the pod.
        He then can compute the private set intersection.
    For more details see: https://eprint.iacr.org/2009/491.pdf
"""
import secrets
from typing import Any, List, Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import pandas as pd

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.base import (
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.exceptions import (
    BlindingError,
    OutOfBoundsError,
    PSIMultiTableError,
    UnBlindingError,
)
from bitfount.federated.mixins import _PSIAlgorithmsMixIn
from bitfount.federated.types import _DataLessAlgorithm
from bitfount.federated.utils import hash_set
from bitfount.utils import _powinv, _powmod


class _ModellerSide(_BaseModellerAlgorithm):
    """Modeller side of the RSABlind algorithm.

    Attributes:
        first_hash_function: The first hash function used in the psi algorithm.
        second_hash_function: The second hash function used in the psi algorithm.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.first_hash_function = hashes.SHA256()
        self.second_hash_function = hashes.SHA512_256()

    def initialise(
        self,
        datasource: BaseSource,
        public_key: RSAPublicKey,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ) -> List[int]:
        """Initialize the psi algorithm on the modeller side.

        More specifically, set the public key parameters,
        load and hash the data, generate random factors, and blind the dataset.

        Args:
            public_key: The public key received from the pod.
            datasource: The datasource on which the psi will be performed.
            columns_to_intersect: Either a list of column names for a
            single-table datasource, or a mapping of table name
            to columns for multi-table datasources.

        Returns:
            The hashed and blinded set.

        Raises:
            PSIColumnsError if you are trying to load columns from more than one table,
                or if the format of `columns_to_intersect` is not supported.
        """
        # Public key consists of `n`, the modulus, and `e`, the encryption key.
        self.n, self.e = self._get_public_key_numbers(public_key)
        # Load the data; `self.data` should be a dataframe.
        if datasource.multi_table and table is None:
            raise PSIMultiTableError(
                "You are trying to perform a PrivateSetIntersection task on a "
                "multitable datasource. Please specify the target table on which "
                "the Private Set Intersection should be performed."
            )
        elif columns_to_intersect and table:
            self.data = datasource.get_data(table)[columns_to_intersect]
        elif columns_to_intersect:
            self.data = datasource.get_data()[columns_to_intersect]
        elif table:
            self.data = datasource.get_data(table)
        else:
            self.data = datasource.get_data()

        # Compute the hashes
        self.hashed_data = hash_set(self.data, self.first_hash_function)
        # Generate random factors for blinding
        self.random_factors = self.generate_random_factors(len(self.data))

        return self.blind_set()

    def _get_public_key_numbers(self, public_key: RSAPublicKey) -> Tuple[int, int]:
        """Get the public key parameters from the RSA public key.

        Returns:
            `n`, the modulus for the public key, and `e`, the public encryption key.
        """
        return public_key.public_numbers().n, public_key.public_numbers().e

    def generate_random_factors(self, n_elements: int) -> List[Tuple[int, int]]:
        """Generate n_elements random factors, then invert and encrypt them.

        Args:
           n_elements: number of random factors to generate.

        Returns:
           A list of tuples, each tuple is composed of the inverse and
           encryption of a random factor.
        """
        random_factors = []
        iteration = 0
        while iteration < n_elements:
            r = secrets.randbelow(self.n)
            try:
                r_inv = _powinv(r, self.n)
            except ValueError:
                # If the random value is not invertible continue and try again
                continue
            r_encrypted = _powmod(r, self.e, self.n)
            iteration += 1
            random_factors.append((r_inv, r_encrypted))
        return random_factors

    def blind(self, record: int, rf_tuple: Tuple[int, int]) -> int:
        """Blind an element using the encryption of a random factor.

        Args:
            record: integer in the range [0, n), where n is the RSA modulus.
            rf_tuple: tuple composed of the inverse and encryption of a random
                factor.

        Returns:
            The blinded version of the element integer x.
        """
        rf_encrypted = rf_tuple[1]
        return (record * rf_encrypted) % self.n

    def unblind(self, integer: int, random_factor_tuple: Tuple[int, int]) -> int:
        """Blind an element using the inverse of a random factor.

        Args:
            integer: integer in the range [0, n), where n is the RSA modulus.
            random_factor_tuple: tuple composed of the inverse and
                encryption of a random factor.

        Returns:
            The unblinded version of the blinded element x.
        """
        rf_inv = random_factor_tuple[0]
        return (integer * rf_inv) % self.n

    def blind_set(self) -> List[int]:
        """Blind a set of elements using the encryption of random factors.

        Returns:
            A list of integers representing the blinded set.
        """
        if len(self.hashed_data) > len(self.random_factors):
            raise BlindingError("There are more elements than random factors")

        blinded_set = []
        for x, rf in zip(self.hashed_data, self.random_factors):
            b = self.blind(x, rf)
            blinded_set.append(b)

        return blinded_set

    def unblind_set(self, dataset: List[int]) -> List[int]:
        """Unblind a set of elements using the inverse of random factors.

        Args:
            dataset: list of integers in the range [0, n), where n is the RSA modulus.

        Returns:
            A list of integers representing the unblinded set X.
        """
        if len(dataset) > len(self.random_factors):
            raise UnBlindingError("There are more elements than random factors")

        unblinded_set = []
        for record, rf_tuple in zip(dataset, self.random_factors):
            unblinded = self.unblind(record, rf_tuple)
            unblinded_set.append(unblinded)
        return unblinded_set

    def intersect(
        self,
        modeller_orig_df: pd.DataFrame,
        blinded_modeller_set: List[int],
        pod_set: List[int],
    ) -> pd.DataFrame:
        """Compute the intersection of the client and server set.

        Args:
            modeller_orig_df: ordered client set.
            blinded_modeller_set: ordered signatures of the client set (unblinded).
            pod_set: signed server set.

        Returns:
            A list of integers representing the intersection of the client and
            server set.
        """
        result = []
        for index in range(len(blinded_modeller_set)):
            if blinded_modeller_set[index] in pod_set:
                result.append(modeller_orig_df.iloc[index])
        return pd.DataFrame(result)

    def run(self, pod_set: List[int], modeller_set: List[int]) -> pd.DataFrame:
        """Runs the modeller side of the algorithm.

        First, it unblinds the modeller set obtained from the worker.
        Then, it hashes the obtained set, and finally performs the intersection.
        """
        unblinded_set = self.unblind_set(modeller_set)
        hashed_modeller_set = hash_set(unblinded_set, self.second_hash_function)
        return self.intersect(self.data, hashed_modeller_set, pod_set)


class _WorkerSide(_BaseWorkerAlgorithm):
    """Worker side of the RSABlind algorithm."""

    def __init__(self, **kwargs: Any) -> None:
        # Set up hash functions algorithms to use
        self.first_hash_function = hashes.SHA256()
        self.second_hash_function = hashes.SHA512_256()
        # Set up private and public key parameters
        self.private_key, self.public_key = _RSAEncryption.generate_key_pair()
        self.n = self.public_key.public_numbers().n
        self.d = self.private_key.private_numbers().d

    def initialise(
        self,
        datasource: BaseSource,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> List[int]:
        """Initialise the worker-side algorithm.

        Args:
            datasource: The datasource of the worker on which the
                intersection will be performed.
            columns_to_intersect: The columns from the worker datasource
                on which to perform the intersection.

        Returns:
            The pod's double hashed set.

        Raises:
            PSIColumnsError if you are trying to load columns from more than one table,
                or if the format of `columns_to_intersect` is not supported.
        """
        if datasource.multi_table and table is None:
            raise PSIMultiTableError(
                "You are trying to perform a PrivateSetIntersection task on a "
                "multitable datasource. Please specify the target table on which "
                "the Private Set Intersection should be performed."
            )
        elif columns_to_intersect and table:
            self.data = datasource.get_data(table)[columns_to_intersect]
        elif columns_to_intersect:
            self.data = datasource.get_data()[columns_to_intersect]
        elif table:
            self.data = datasource.get_data(table)
        else:
            self.data = datasource.get_data()

        hashed_data = hash_set(self.data, self.first_hash_function)
        decrypted_set = self.decrypt_set(hashed_data)
        return hash_set(decrypted_set, self.second_hash_function)

    def run(self, modeller_set: List[int]) -> List[int]:
        """Runs the worker-side of the algorithm."""
        return self.decrypt_set(modeller_set)

    def decrypt(self, item: int) -> int:
        """Sign a single element using the RSA private key.

        Args:
            item: integer in the range [0, n), where n is the RSA modulus.

        Returns:
            The signature of item, computed as item^d modulus n.
        """
        if item < 0 or item >= self.n:
            raise OutOfBoundsError(f"x should be in range [0, {self.n})")
        return _powmod(item, self.d, self.n)

    def decrypt_set(self, data: List[int]) -> List[int]:
        """Decrypt a set of elements using the RSA private key.

        Args:
            data: list of integers in the range [0, n), where n is the RSA modulus.

        Returns:
            A list of integers representing the signatures of the set X.
        """
        return [self.decrypt(item) for item in data]


class ComputeIntersectionRSA(
    _BaseAlgorithmFactory, _PSIAlgorithmsMixIn, _DataLessAlgorithm
):
    """Algorithm for computing the private set intersection with rsa blinding."""

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__()

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the SqlQuery algorithm."""
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the SqlQuery algorithm."""
        return _WorkerSide(**kwargs)
