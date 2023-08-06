import os
from typing import Optional


class PositionIndependentFileLocator:
    @staticmethod
    def find_path_to_test_folder(path: str) -> str:
        dir_path = os.path.dirname(os.path.realpath(path))
        # https://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
        path_parts = os.path.normpath(dir_path).split(os.sep)
        # test folder is a sibling to src
        return os.sep.join(path_parts[0:path_parts.index('src')] + ['test'])

    @staticmethod
    def find_path_to_current_path(path: str, selected: Optional[int] = None) -> str:
        dir_path = os.path.dirname(path)
        # https://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
        path_parts = os.path.normpath(dir_path).split(os.sep)
        # test folder is a child of src
        if selected is None:
            selected_ = path_parts
        else:
            selected_ = path_parts[0:selected]
        return os.sep.join(selected_)

    @classmethod
    def find_last_folder_of(cls, path: str) -> str:
        dir_path = os.path.realpath(path)
        dir_path = os.path.dirname(dir_path)
        path_parts = os.path.normpath(dir_path).split(os.sep)
        return path_parts[-1]
