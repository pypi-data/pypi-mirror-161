import importlib

from .file_helper import FileHelper
from .kat_printer import KATPrinter, KATExchange


class KATGenerator:
    """
    Class used to parse and check or generate and write KAT files.
    """

    def __init__(self, file_helper: FileHelper, arguments: list[str], considered_algs: list[str]) -> None:
        self.file_helper = file_helper
        self.arguments = arguments
        self.considered_algs = considered_algs

    def generate_kats(self, algorithm: str) -> None:
        my_module = importlib.import_module(f'src.{algorithm}', package=None)
        cryptography_generator = getattr(my_module, 'Factory').new(arguments=self.arguments)
        for test_case in cryptography_generator.test_cases():
            output = cryptography_generator.compute(test_case['data'])
            selected_filename = f'tv_{test_case["name"]}.kat'
            result_ = []
            for ou in output:
                exchange: KATExchange = cryptography_generator.to_exchange(ou)
                result_.append(exchange)
            kat_contents = KATPrinter().generate_as_string(result_)
            self.file_helper.write_file(selected_filename, kat_contents)

    def genkat(self) -> None:
        """Generate and write a testcase to KAT file for all supported algorithms
        """
        for alg in self.considered_algs:
            self.generate_kats(alg)
