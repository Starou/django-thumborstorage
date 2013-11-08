# -*- coding: utf-8 -*-

import unittest


class ThumborStorageTestCase(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(2 + 2, 4)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ThumborStorageTestCase)
    return suite
