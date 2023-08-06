from typing import List, Union

ParsingType = dict[str, Union[str, int, bytes]]


class GeneralParsing:
    @staticmethod
    def parse(alg: str, filepath: str) -> List[ParsingType]:
        """Parse a KAT file list for testcases. Each testcase is added to an array being the value
        in a dict where each key is a supported algorithm
        """
        with open(filepath) as file:
            lines = file.readlines()
        result: List[ParsingType] = []
        for line_counter, line in enumerate(lines):
            if 'Count' in line:
                continue
            if len(line.strip()) == 0 or line.startswith('#') or line.startswith('['):
                continue

            parts = line.split('=', 1)
            keyword_ = parts[0].strip()
            value_ = parts[1].strip()
            if keyword_ == 'TITLE':
                result.append(dict())
                result[len(result) - 1][keyword_] = value_
            else:
                if keyword_ == 'ACTION':
                    result[len(result) - 1][keyword_] = value_
                elif ['SECURITY_LEVEL', 'DIGEST_LENGTH'].__contains__(keyword_):
                    result[len(result) - 1][keyword_] = int(value_)
                else:
                    try:
                        result[len(result) - 1][keyword_] = bytes.fromhex(value_)
                    except Exception as e:
                        raise ValueError(
                            f"Line {filepath}:{line_counter}: '{line}', alg: '{alg}', keyword = '{keyword_}', value = '{value_}'",
                            e)
        return result
