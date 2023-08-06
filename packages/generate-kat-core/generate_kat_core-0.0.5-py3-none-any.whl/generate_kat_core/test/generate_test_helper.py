import os
import shutil
import tempfile
import unittest
from difflib import Differ

from generate_kat_core.file_utils import PositionIndependentFileLocator


class GenerateTestHelper:
    def __init__(self, path_to_algorithm: str, path_expected: str):
        self.path_actual: str = tempfile.TemporaryDirectory().name
        self.path_to_algorithm = path_to_algorithm
        self.path_expected = path_expected
        self.test_helper = unittest.TestCase()

    def createFolders(self) -> None:
        os.makedirs(self.path_actual)
        self.delete_file_if_exists(self.path_actual)
        os.makedirs(self._folder_at_primitive_folder(self.path_expected), exist_ok=True)

    def _folder_at_primitive_folder(self, folder: str) -> str:
        prefix = PositionIndependentFileLocator.find_path_to_current_path(self.path_to_algorithm, selected=None)
        return os.path.join(prefix, folder)

    @property
    def algorithm(self) -> str:
        return PositionIndependentFileLocator.find_last_folder_of(self.path_to_algorithm)

    def diff_multiple_kat_files(self, file_names: list[str]) -> None:
        list(map(self.diff_single_kat_files, file_names))

    def diff_single_kat_files(self, filename: str) -> None:
        prefix = PositionIndependentFileLocator.find_path_to_current_path(self.path_to_algorithm, selected=None)
        self.path_expected = os.path.join(prefix, self.path_expected)
        path_expected = os.path.join(self.path_expected, filename)
        path_actual = os.path.join(self.path_actual, filename)
        self._diff_files(path_expected, path_actual)

    def _diff_files(self, path_expected: str, path_actual: str) -> None:
        differ = Differ()
        copy = False
        try:
            self.test_helper.assertTrue(os.path.exists(path_actual), f"File at {path_actual} does not exist")
            self.test_helper.assertTrue(os.path.exists(path_expected), f"File at {path_expected} does not exist")
            with open(path_actual) as actual, open(path_expected) as expected:
                differences = 0
                for line in differ.compare(actual.readlines(), expected.readlines()):
                    if line.startswith('  '):
                        continue
                    print(line.rstrip())
                    differences += 1

                if differences > 0:
                    copy = True
                    self.test_helper.fail(
                        f"There are {differences} differences in the file contents expected: {path_expected}, actual: {path_actual}")
        except OSError:
            if copy:
                destination = f"{path_expected}.tmp"
                print(f"Copying {path_actual} to {destination}")
                shutil.copy(path_actual, destination)
            raise

    def delete_actual_files(self, file_names: list[str]) -> None:
        for file_name in file_names:
            self.delete_actual_file(file_name)

    def delete_actual_file(self, file_name: str) -> None:
        file_path = os.path.join(self.path_actual, file_name)
        self.delete_file_if_exists(file_path)
        if os.path.exists(file_path):
            raise ValueError(f"{file_path} could not be deleted")

    @staticmethod
    def delete_file_if_exists(file_path: str) -> None:
        try:
            os.remove(file_path)
        except OSError:
            # might not exist
            pass

    def delete_folders(self) -> None:
        self.delete_file_if_exists(self.path_actual)
