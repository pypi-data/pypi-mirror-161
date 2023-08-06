from collections.abc import Iterator
from dataclasses import dataclass
from itertools import zip_longest
from typing import Union

from math import isclose


@dataclass
class CompareJson:
    start_index: int = 0
    accuracy: int = 3
    exclude_fields: list = ()
    format_number: bool = False
    use_delta_for_checksum: bool = False

    @staticmethod
    def is_instance(v_iter, v_type):
        return all(map(lambda t: isinstance(t, v_type), v_iter))

    def _compare(self, *values):
        return CompareJson(
            self.start_index,
            self.accuracy,
            self.exclude_fields,
            self.format_number,
            self.use_delta_for_checksum
        )(*values)

    @staticmethod
    def _strip_values(v_in, v_out):
        if isinstance(v_out, str):
            v_out = v_out.strip()
        if isinstance(v_in, str):
            v_in = v_in.strip()
        return v_in, v_out

    def _compare_array(self, v_in, v_out, mismatch_items):
        for key, value in enumerate(zip_longest(v_in, v_out), start=self.start_index):
            result = self._compare(*value)
            if result:
                mismatch_items[key] = result

    def _compare_number(self, v_in, v_out):
        if round(v_in, self.accuracy) != round(v_out, self.accuracy):
            if self.use_delta_for_checksum:
                return abs(round(v_in, 2) - round(v_out, 2)) >= .1 ** 2
            return True
        return False

    @staticmethod
    def _is_equal(v_in, v_out):
        return any((
            v_in == v_out,
            v_in == '!not_empty' and v_out != 'нет в ответе' and v_out,
            v_in == '!empty' and not v_out
        ))

    def _compare_dict(self, v_in, v_out, mismatch_items):
        for key, value_in in v_in.items():
            if key in self.exclude_fields:
                continue
            result = self._compare(
                value_in,
                v_out.get(key, 'Поля %r нет в ответе' % key)
            )
            if result:
                mismatch_items[key] = result

    def __call__(self, v_in, v_out) -> Union[None, dict]:
        v_in, v_out = self._strip_values(v_in, v_out)
        mismatch_items = dict()

        if v_in is None or self._is_equal(v_in, v_out):
            pass

        # Сначала проверяем что пришел не список или другой похожий итератор
        elif self.is_instance((v_in, v_out), (list, tuple, Iterator)):
            self._compare_array(v_in, v_out, mismatch_items)

        elif isinstance(v_in, set) and v_in.symmetric_difference(v_out):
            return self.formation_error(list(v_in), v_out)

        elif self.is_instance((v_in, v_out), (int, float)):
            if self._compare_number(v_in, v_out):
                if self.format_number and v_in >= 10000:
                    return self.formation_error(f'{v_in:,}', f'{v_out:,}')
                return self.formation_error(v_in, v_out)

        elif self.is_instance((v_in, v_out), dict):
            self._compare_dict(v_in, v_out, mismatch_items)

        else:
            return self.formation_error(v_in, v_out)

        return mismatch_items

    @staticmethod
    def formation_error(v_in, v_out):
        return {
            'Хотели': v_in,
            'Получили': v_out
        }


compare = CompareJson()
