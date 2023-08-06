from typing import Any


# https://stackoverflow.com/questions/750908/auto-repr-method
class AutoRepr(object):
    def __repr__(self) -> str:
        items: list[str] = []
        for k, v in self.__dict__.items():
            len_ = ''
            if isinstance(v, tuple({bytes, str})):
                len_ = str(len(v))
            if isinstance(v, bytes):
                v = v.hex()

            items.append("%s = %s (len %s)" % (k, v, len_))

        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))

    def __eq__(self, other: Any) -> bool:
        other_values = other.__dict__.items()
        self_values = self.__dict__.items()
        return len(self_values - other_values) == 0
