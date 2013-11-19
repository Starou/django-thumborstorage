# -*- coding: utf-8 -*-

import mock
import os
import unittest

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
IMAGE_DIR = os.path.join(CURRENT_DIR, "..", "images")

class MockedGetResponse:
    status_code = 200

    def __init__(self, url):
        """Retrieve the file on the filesytem according to the name. """
        basename = os.path.basename(url)
        filename = os.path.join(IMAGE_DIR, basename)
        self.content = open(filename, "r").read()


def mocked_thumbor_get_response(url):
    response = MockedGetResponse(url)
    return response


class MockedPostResponse:
    headers = {}


def mocked_thumbor_post_response(url, data, headers):
    response = MockedPostResponse()
    response.headers["location"] = "/image/oooooo32chars_random_idooooooooo/%s" % headers["Slug"]
    return response


class ThumborStorageFileTest(unittest.TestCase):
    def setUp(self):
        super(ThumborStorageFileTest, self).setUp()
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
        self.patcher_get = mock.patch('django_thumborstorage.storages.requests.get')
        self.MockGetClass = self.patcher_get.start()
        self.MockGetClass.side_effect = mocked_thumbor_get_response

        self.patcher_post = mock.patch('django_thumborstorage.storages.requests.post')
        self.MockPostClass = self.patcher_post.start()
        self.MockPostClass.side_effect = mocked_thumbor_post_response

    def tearDown(self):
        self.patcher_get.stop()

    def test_get_file(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        thumbor_file.file
        self.MockGetClass.called_with("%s%s" % (settings.THUMBOR_SERVER, filename))

    def test_size(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        size = thumbor_file.size
        self.MockGetClass.called_with("%s%s" % (settings.THUMBOR_SERVER, filename))
        self.assertEqual(size, 9730)

    def test_write(self):
        from django_thumborstorage import storages
        from django.conf import settings
        from django.core.files.base import ContentFile
        filename = 'people/HannibalSmith.jpg'
        content = ContentFile(open('%s/HannibalSmith.jpg' % IMAGE_DIR))
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        thumbor_file.write(content=content)
        self.MockPostClass.called_with("%s/image" % settings.THUMBOR_WRITABLE_SERVER)


class ThumborStorageTest(unittest.TestCase):
    pass


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ThumborStorageTest)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborStorageFileTest))
    return suite
