import unittest

from compare_for_testing.compare import compare


class TestCompareResult(unittest.TestCase):
    def test_diff_for_dict(self):
        json_1 = {
            'a': 1,
            'b': 2,
            'empty': '',
        }

        json_2 = {
            'aa': True,
            'b': 4,
            'empty': '!empty',
            'empty_failed': '!empty',
        }
        result = compare(json_2, json_1)

        verify = {
            'aa': {'Хотели': True, 'Получили': "Поля 'aa' нет в ответе"},
            'b': {'Хотели': 4, 'Получили': 2},
            'empty_failed': {'Хотели': '!empty', 'Получили': "Поля 'empty_failed' нет в ответе"}
        }
        self.assertDictEqual(result, verify)

    def test_diff_list(self):
        list_1 = [i for i in range(5)]
        list_2 = [i ** i for i in range(5)]

        result = compare(list_1, list_2)
        verify = {
            0: {'Хотели': 0, 'Получили': 1},
            2: {'Хотели': 2, 'Получили': 4},
            3: {'Хотели': 3, 'Получили': 27},
            4: {'Хотели': 4, 'Получили': 256}
        }

        self.assertDictEqual(result, verify)

    def test_diff_with_recursive(self):
        json_1 = {

            'c': [
                {
                    'sub_a': 1,
                    'sub_b': 3
                },
                {
                    'sub_a': 2,
                    'sub_b': 4
                },
                {
                    'sub_a': 3,
                    'sub_b': 5,
                    'sub_c': {
                        'name': 'test',
                        'id': 5,
                    }
                },
            ],
        }

        json_2 = {

            'c': [
                {
                    'sub_a': 11,
                    'sub_b': 43
                },
                {
                    'sub_a': 21,
                    'sub_b': 4
                },
                {
                    'sub_a': '!not_empty',
                    'sub_b': '!empty',
                    'sub_c': {
                        'name': 'test',
                        'name2': 'test',
                    }
                },
                {
                    'sub_a': '!not_empty',
                    'sub_b': 8,
                    'sub_c': {
                        'name': 'test',
                    }
                },
            ],
        }
        result = compare(json_2, json_1)
        verify = {
            'c': {
                0: {
                    'sub_a': {'Хотели': 11, 'Получили': 1},
                    'sub_b': {'Хотели': 43, 'Получили': 3}
                },
                1: {
                    'sub_a': {'Хотели': 21, 'Получили': 2}
                },
                2: {
                    'sub_b': {'Хотели': '!empty', 'Получили': 5},
                    'sub_c': {
                        'name2': {'Хотели': 'test', 'Получили': "Поля 'name2' нет в ответе"}
                    }
                },
                3: {
                    'Хотели': {'sub_a': '!not_empty', 'sub_b': 8, 'sub_c': {'name': 'test'}},
                    'Получили': None
                }
            }
        }
        self.assertDictEqual(result, verify)
