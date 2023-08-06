# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_text_name.py
"""

import sys
import unittest
import random

sys.path.append(".")

from itb_www import \
    change_query_string

change_query_string_data = [
    {
        'url': 'http://qawebsite.com/search?q=question&x=irgendwas',
        'query': 'q=question&x=irgendwas',
        'params': {
            'lang':'en',
            'tag':'python',
            'q': 'frage',
            'nummer:int': 4},
        'new_url': 'http://qawebsite.com/search?q=frage&x=irgendwas&lang=en&tag=python&nummer:int=4',
        'new_query': 'q=frage&x=irgendwas&lang=en&tag=python&nummer:int=4',
        'new_url_fresh': 'http://qawebsite.com/search?lang=en&tag=python&q=frage&nummer:int=4',
        'new_query_fresh': 'lang=en&tag=python&q=frage&nummer:int=4'
    }
]

class TestTextName(unittest.TestCase):
    def test_change_query_string(self):
        for datum in change_query_string_data:
            new_url = change_query_string(
                url=datum.get('url'),
                params=datum.get('params'),
                returning='url'
            )
            self.assertEqual(new_url, datum.get('new_url'))

            new_url = change_query_string(
                url=datum.get('url'),
                params=datum.get('params'),
                returning='url',
                delete_remaining=True
            )
            self.assertEqual(new_url, datum.get('new_url_fresh'))

            new_query = change_query_string(
                query_string=datum.get('query'),
                params=datum.get('params'),
                returning='query_string'
            )
            self.assertEqual(new_query, datum.get('new_query'))

            new_query = change_query_string(
                query_string=datum.get('query'),
                params=datum.get('params'),
                returning='query_string',
                delete_remaining=True
            )
            self.assertEqual(new_query, datum.get('new_query_fresh'))

            new_query = change_query_string(
                url=datum.get('url'),
                params=datum.get('params'),
                returning='query_string'
            )
            self.assertEqual(new_query, datum.get('new_query'))

            new_query = change_query_string(
                url=datum.get('url'),
                params=datum.get('params'),
                returning='query_string',
                delete_remaining=True
            )
            self.assertEqual(new_query, datum.get('new_query_fresh'))

            try:
                change_query_string(
                    query_string=datum.get('query'),
                    params=datum.get('params'),
                    returning='url'
                )
                raise Exception('Error: returning url with query string provided')
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
