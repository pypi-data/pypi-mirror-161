from typing import List

from generate_kat_core.utils import KATError


class AlgorithmValidator:
    @staticmethod
    def validate(existing_algorithms: List[str], algorithms: List[str]) -> list[str]:
        if not algorithms or 'all' in algorithms:
            return list(existing_algorithms)

        result = []
        for alg in algorithms:
            if alg.upper() in existing_algorithms:
                result.append(alg.upper())
            else:
                raise KATError('Unsupported algorithm : ', alg.upper())
        algorithms = result
        return algorithms
