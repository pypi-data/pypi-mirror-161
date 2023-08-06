import argparse
import random
from typing import Any


class GeneralArgumentsConfiguration:
    def __init__(self, arguments: argparse.Namespace) -> None:
        self.arguments = arguments

    def generate_random(self) -> random.Random:
        if self.arguments.fixed_randomness:
            random_random = random.Random(self.arguments.fixed_randomness)
            if self.arguments.verbose:
                print(f"Using fixed randomness. Seeding to {self.arguments.fixed_randomness}")
        else:
            random_random = random.Random()
            if self.arguments.verbose:
                print(f"Using proper randomness")
        return random_random


class ArgumentParserBuilder:
    def __init__(self) -> None:
        self.value = argparse.ArgumentParser()

    def withFixedRandomness(self) -> Any:
        self.value.add_argument('--fixed-randomness', default=None,
                                help="Fix the randomness, seeding with an INT (TEST ONLY)", type=int)
        return self

    def withVerbose(self) -> Any:
        self.value.add_argument("--verbose", default=False, help='Output verbose logging', action="store_true")
        return self

    def build(self) -> argparse.ArgumentParser:
        return self.value
