# -*- coding: utf-8 -*-

import mock
import os
import unittest
from django.core.files.base import ContentFile

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


class MockedDeleteAllowedResponse:
    status_code = 204
    content = ''

    def __init__(self, url):
        basename = os.path.basename(url)
        filename = os.path.join(IMAGE_DIR, basename)
        if not os.path.exists(filename):
            self.status_code = 404


def mocked_thumbor_delete_allowed_response(url):
    response = MockedDeleteAllowedResponse(url)
    return response


class MockedDeleteNotAllowedResponse:
    status_code = 405


def mocked_thumbor_delete_not_allowed_response(url):
    response = MockedDeleteNotAllowedResponse()
    return response


class DjangoThumborTestCase(unittest.TestCase):
    def setUp(self):
        super(DjangoThumborTestCase, self).setUp()
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
        self.patcher_get = mock.patch('django_thumborstorage.storages.requests.get')
        self.MockGetClass = self.patcher_get.start()
        self.MockGetClass.side_effect = mocked_thumbor_get_response

        self.patcher_post = mock.patch('django_thumborstorage.storages.requests.post')
        self.MockPostClass = self.patcher_post.start()
        self.MockPostClass.side_effect = mocked_thumbor_post_response

        self.patcher_delete = mock.patch('django_thumborstorage.storages.requests.delete')
        self.MockDeleteClass = self.patcher_delete.start()

    def tearDown(self):
        self.patcher_get.stop()
        self.patcher_post.stop()
        self.patcher_delete.stop()


class ThumborStorageFileTest(DjangoThumborTestCase):
    def test_get_file(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        thumbor_file.file
        self.MockGetClass.assert_called_with("%s%s" % (settings.THUMBOR_SERVER, filename))

    def test_size(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='r')
        size = thumbor_file.size
        self.MockGetClass.assert_called_with("%s%s" % (settings.THUMBOR_SERVER, filename))
        self.assertEqual(size, 9730)

    def test_write_jpeg(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = 'people/HannibalSmith.jpg'
        content = ContentFile(open('%s/HannibalSmith.jpg' % IMAGE_DIR))
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        thumbor_file.write(content=content)
        self.MockPostClass.assert_called_with("%s/image" % settings.THUMBOR_WRITABLE_SERVER,
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/jpeg", "Slug": filename})
        self.assertEqual(thumbor_file._location, '/image/oooooo32chars_random_idooooooooo/%s' % filename)

    def test_write_png(self):
        from django_thumborstorage import storages
        from django.conf import settings
        filename = 'foundations/gnu.png'
        content = ContentFile(open('%s/gnu.png' % IMAGE_DIR))
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        thumbor_file.write(content=content)
        self.MockPostClass.assert_called_with("%s/image" % settings.THUMBOR_WRITABLE_SERVER,
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/png", "Slug": filename})
        self.assertEqual(thumbor_file._location, '/image/oooooo32chars_random_idooooooooo/%s' % filename)

    def test_delete_allowed(self):
        self.MockDeleteClass.side_effect = mocked_thumbor_delete_allowed_response
        from django_thumborstorage import storages
        from django.conf import settings
        filename = '/image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        thumbor_file.delete()
        self.MockDeleteClass.assert_called_with("%s%s" % (settings.THUMBOR_WRITABLE_SERVER, filename))
        # TODO test status_code == 204 (how ?)

        from django_thumborstorage import exceptions
        filename = '/image/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        self.assertRaises(exceptions.NotFoundException, thumbor_file.delete)

    def test_delete_not_allowed(self):
        self.MockDeleteClass.side_effect = mocked_thumbor_delete_not_allowed_response
        from django_thumborstorage import storages
        from django.conf import settings
        from django_thumborstorage import exceptions
        filename = '/image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)

        filename = '/image/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)

class ThumborStorageTest(DjangoThumborTestCase):
    def setUp(self):
        super(ThumborStorageTest, self).setUp()
        from django_thumborstorage import storages
        self.storage = storages.ThumborStorage()

    def test_url(self):
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         '%s/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg' % settings.THUMBOR_SERVER)

    def test_size(self):
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        size = self.storage.size(filename)
        self.MockGetClass.assert_called_with("%s%s" % (settings.THUMBOR_SERVER, filename))
        self.assertEqual(size, 9730)

    def test_save(self):
        from django.conf import settings
        filename = 'people/HannibalSmith.jpg'
        content = ContentFile(open('%s/HannibalSmith.jpg' % IMAGE_DIR))
        response = self.storage.save(filename, content)
        self.MockPostClass.assert_called_with("%s/image" % settings.THUMBOR_WRITABLE_SERVER,
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/jpeg", "Slug": filename})
        self.assertEqual(response, '/image/oooooo32chars_random_idooooooooo/%s' % filename)


class ThumborMigrationStorageTest(DjangoThumborTestCase):
    def setUp(self):
        super(ThumborMigrationStorageTest, self).setUp()
        from django_thumborstorage import storages
        self.storage = storages.ThumborMigrationStorage()

    def test_url_thumbor(self):
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         '%s/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg' % settings.THUMBOR_SERVER)

    def test_url_filesystem(self):
        from django.conf import settings
        filename = 'images/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         '%simages/people/new/TempletonPeck.jpg' % settings.MEDIA_URL)

    def test_path_thumbor(self):
        from django.conf import settings
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        with self.assertRaises(NotImplementedError):
            self.storage.path(filename)

    def test_path_filesystem(self):
        from django.conf import settings
        filename = 'images/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.path(filename), '/media/images/people/new/TempletonPeck.jpg')


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ThumborStorageTest)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborStorageFileTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborMigrationStorageTest))
    return suite
