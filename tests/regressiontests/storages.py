# -*- coding: utf-8 -*-

import mock
import os
import unittest


class MockedGetResponse:
    _current_dir = os.path.abspath(os.path.split(__file__)[0])
    _image_dir = os.path.join(_current_dir, "..", "images")
    status_code = 200

    def __init__(self, url):
        """Retrieve the file on the filesytem according to the name. """
        basename = os.path.basename(url)
        filename = os.path.join(self._image_dir, basename)
        self.content = open(filename, "r").read()


def mocked_thumbor_get_response(url):
    response = MockedGetResponse(url)
    return response


class ThumborStorageFileTest(unittest.TestCase):
    def setUp(self):
        super(ThumborStorageFileTest, self).setUp()
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
        self.patcher = mock.patch('django_thumborstorage.storages.requests.get')
        self.MockClass = self.patcher.start()
        self.MockClass.side_effect = mocked_thumbor_get_response

    def tearDown(self):
        self.patcher.stop()

    def test_get_file(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        thumbor_file.file
        self.MockClass.called_with("%s%s" % (settings.THUMBOR_SERVER, filename))

    def test_size(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        size = thumbor_file.size
        self.MockClass.called_with("%s%s" % (settings.THUMBOR_SERVER, filename))
        self.assertEqual(size, 9730)


class ThumborStorageTest(unittest.TestCase):
    pass


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ThumborStorageTest)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborStorageFileTest))
    return suite
