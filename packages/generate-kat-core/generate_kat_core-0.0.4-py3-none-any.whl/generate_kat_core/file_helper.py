"""File helper module"""
import os
from pathlib import Path


class FileHelper:
    """Provides file operations methods"""

    def __init__(self, outdir_path: Path) -> None:
        self.outdir_path = outdir_path

    def write_file(self, outkat_file: str, kat_data: str) -> None:
        """Writes files

        Args:
            outkat_file (str): name of the file to be written
            kat_data (str): data to be written
        """
        output_path = os.path.join(self.outdir_path, outkat_file)
        if os.path.exists(output_path):
            try:
                raise ValueError(f"{output_path} already exists")
            except ValueError as e:
                print(e)
                raise e

        with open(output_path, "w+") as file_buffer:
            file_buffer.write(kat_data)
