# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_text_name.py
"""

import sys
import unittest
import random

sys.path.append(".")

from itb_text_name import \
    and_list, \
    capitalize_name, \
    get_gender, \
    leet, \
    sort_names

names = {
    'Georg Pfolz': {
        'lowercase': 'georg pfolz',
        'gender': 'male',
        'is_a_name': True
    },
    'Patrizia Höfstädter': {
        'lowercase': 'patrizia höfstädter',
        'gender': 'female',
        'is_a_name': True
    },
    'Eugénie Caraçon': {
        'lowercase': 'eugénie caraçon',
        'gender': 'female',
        'is_a_name': True
    },
    'Joanna MacArthur': {
        'lowercase': 'joanna macarthur',
        'gender': 'female',
        'is_a_name': True
    },
    'Sandra de Vitt': {
        'lowercase': 'sandra de vitt',
        'gender': 'female',
        'is_a_name': True
    },
    'Roland Meier-Lansky': {
        'lowercase': 'roland meier-lansky',
        'gender': 'male',
        'is_a_name': True
    },
    'Bogumila Österreicher': {
        'lowercase': 'bogumila österreicher',
        'gender': 'unknown',
        'is_a_name': True
    },
    'DsZHkfNijWFPrET JGLAjuaqZ': {
        'lowercase': 'dszhkfnijwfpret jglajuaqz',
        'gender': 'unknown',
        'is_a_name': False
    }
}

names_sorted = [
    'Eugénie Caraçon',
    'Patrizia Höfstädter',
    'DsZHkfNijWFPrET JGLAjuaqZ',
    'Joanna MacArthur',
    'Roland Meier-Lansky',
    'Bogumila Österreicher',
    'Georg Pfolz',
    'Sandra de Vitt'
]

lower_text = 'das ist ein Beispiel-Text, der kapitalisiert werden kann.'


class TestTextName(unittest.TestCase):
    def test_and_list(self):
        a_list = [1, 'Georg', 'Haus', True]
        correct_str = '1, Georg, Haus and True'

        and_str = and_list(a_list)

        self.assertEqual(and_str, correct_str)

    def test_leet(self):
        string_to_leet = random.choice(list(names))
        max_length = random.randint(6, 12)
        start_at_begin = random.randint(0, 1)
        print(f'{string_to_leet} --> {leet(string_to_leet)}')
        leeted_text = leet(
            text=string_to_leet,
            max_length=max_length,
            start_at_begin=start_at_begin
        )
        print(
            f'{string_to_leet}, {max_length = }  {start_at_begin = } --> {leeted_text}'
        )

        # because of the use of random, using Asserts does not make any sense here

    def test_capitalize_name(self):
        for name, name_dict in names.items():
            capitalized_name = capitalize_name(text=name_dict.get('lowercase'))
            self.assertEqual(name, capitalized_name)

    def test_get_gender(self):
        for name, name_dict in names.items():
            correct_gender = name_dict.get('gender')
            gender = get_gender(name.split()[0])  # prename

            try:
                self.assertEqual(gender, correct_gender)
            except AssertionError:
                msg = f'{gender} != {correct_gender} for {name}'
                raise AssertionError(msg)

    def test_sort_names(self):
        names_list = list(names)
        sorted_names = sort_names(names=names_list)

        self.assertEqual(sorted_names, names_sorted)


if __name__ == '__main__':
    unittest.main()

    print('finished format tests.')
