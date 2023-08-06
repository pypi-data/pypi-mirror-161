# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_data.py
"""

import sys
import unittest

from itb_email_phone import create_email_message, process_phonenumber

sys.path.append(".")

phonenumbers = {
    '(699) 123 456 789': {
        'international': '+43 699 123456789',
        'national': '0699 123456789',
        'E164': '+43699123456789'
    },
    '01 456 789': {
        'international': '+43 1 456789',
        'national': '01 456789',
        'E164': '+431456789'
    },
    '+12124567890': {
        'international': '+1 212-456-7890',
        'national': '(212) 456-7890',
        'E164': '+12124567890'
    },
    '+32 460224965': {
        'international': '+32 460 22 49 65',
        'national': '0460 22 49 65',
        'E164': '+32460224965'
    }
}


class TestEmailPhone(unittest.TestCase):
    def test_create_email_message(self):
        pass

    def test_process_phonenumber(self):
        for pn, data in phonenumbers.items():
            for fmt in ('international', 'national', 'E164'):
                self.assertEqual(data[fmt], process_phonenumber(pn, numberfmt=fmt, country='AT'))


if __name__ == '__main__':
    unittest.main()

    print('finished format tests.')
