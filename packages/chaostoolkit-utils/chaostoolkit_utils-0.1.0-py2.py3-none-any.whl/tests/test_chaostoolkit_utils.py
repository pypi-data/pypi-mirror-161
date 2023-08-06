#!/usr/bin/env python

import unittest
import requests
import requests_mock

from chaostoolkit_utils.probes import check_site_content


class TestChaostoolkit_utils(unittest.TestCase):

    def test_check_site_content(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', text="Lorem ipsum dolor sit amet, consectetur adipiscing elit")
            self.assertTrue(check_site_content(url="http://test.com", pattern="dolor"))
            self.assertFalse(check_site_content(url="http://test.com", pattern="foo"))
