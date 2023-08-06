"""
encode
~~~~~~

A Python object to YADN encoder.
"""
from yadr.model import CompoundResult, Result


class Encoder:
    def __init__(self, yadn: str = '') -> None:
        self.yadn = yadn

    # Public methods.
    def encode(self, data: Result | CompoundResult) -> str:
        """Turn computed Python object results into a YADN string."""
        if isinstance(data, bool):
            self._encode_bool(data)
        elif isinstance(data, int):
            self._encode_int(data)
        elif isinstance(data, str):
            self._encode_str(data)
        elif isinstance(data, CompoundResult):
            self._encode_compound_result(data)
        elif isinstance(data, tuple):
            self._encode_tuple(data)
        return self.yadn

    # Private methods.
    def _encode_bool(self, data: bool) -> None:
        if data:
            self.yadn = f'{self.yadn}T'
        else:
            self.yadn = f'{self.yadn}F'

    def _encode_compound_result(self, data: CompoundResult) -> None:
        for result in data[:-1]:
            self.encode(result)
            self.yadn += '; '
        else:
            self.encode(data[-1])

    def _encode_int(self, data: int) -> None:
        self.yadn = f'{self.yadn}{data}'

    def _encode_tuple(self, data: tuple) -> None:
        if isinstance(data[0], int):
            members = ', '.join(str(m) for m in data)
        else:
            quoted = [f'"{m}"' for m in data]
            members = ', '.join(str(m) for m in quoted)
        self.yadn = f'{self.yadn}[{members}]'

    def _encode_str(self, data: str) -> None:
        self.yadn = f'{self.yadn}"{data}"'
