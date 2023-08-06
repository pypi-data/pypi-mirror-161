import os
import unittest

from generate_kat_core.file_utils import PositionIndependentFileLocator
from generate_kat_core.general_parsing import ParsingType
from generate_kat_core.kat_verification import KATVerifier


class VerifyTestHelper:
    def __init__(self, path_to_algorithm: str):
        self.path_to_algorithm = path_to_algorithm
        self._test_helper = unittest.TestCase()

    @property
    def algorithm(self) -> str:
        return PositionIndependentFileLocator.find_last_folder_of(self.path_to_algorithm)

    def assert_test_cases_have_keys(self, parsing_types: list[ParsingType], expected_keys: set[str]) -> None:
        for index, value in enumerate(parsing_types):
            actual_keys = set(value.keys())
            if expected_keys != actual_keys:
                print(actual_keys)
            self._test_helper.assertEqual(expected_keys, actual_keys)

    def verify(self, kat: KATVerifier, path: str, kat_files: list[str], expected_length_of_testcases: int,
               expected_keys_in_test_case: set[str]) -> None:
        kat.parse([os.path.join(path, x) for x in kat_files])

        actual_test_cases: list[ParsingType] = kat.test_kat()[self.algorithm]

        algorithm_test_cases = kat.testcases[self.algorithm]

        self._test_helper.assertEqual(len(algorithm_test_cases), expected_length_of_testcases)
        self.assert_test_cases_have_keys(actual_test_cases, expected_keys_in_test_case)
