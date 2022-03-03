# -*- coding: utf-8 -*-

import os
import unittest
import requests
import mock
from django.conf import settings
from django.core.files.base import ContentFile
from django_thumborstorage import storages
from django_thumborstorage import exceptions

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
IMAGE_DIR = os.path.join(CURRENT_DIR, "..", "images")


class MockedGetResponse:
    status_code = 200

    def __init__(self, url):
        """Retrieve the file on the filesytem according to the name. """
        # TODO: catch LocationParseError.
        basename = os.path.basename(url)
        filename = os.path.join(IMAGE_DIR, basename)
        if not os.path.exists(filename):
            self.status_code = 404
        else:
            self.content = open(filename, "rb").read()


def mocked_thumbor_get_response(url):
    response = MockedGetResponse(url)
    return response


class MockedPostResponse:
    status_code = 201
    headers = {}
    reason = ''


def mocked_thumbor_post_response(url, data, headers):
    response = MockedPostResponse()
    if len(data) < 10000:
        response.status_code = 412
        response.reason = "Image too small"
        return response
    response.headers["location"] = f"/image/oooooo32chars_random_idooooooooo/{headers['Slug']}"
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
        super().setUp()
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
        self.patcher_get = mock.patch('django_thumborstorage.storages.requests.get')
        self.MockGetClass = self.patcher_get.start()
        self.MockGetClass.side_effect = mocked_thumbor_get_response

        self.patcher_post = mock.patch('django_thumborstorage.storages.requests.post')
        self.MockPostClass = self.patcher_post.start()
        self.MockPostClass.side_effect = mocked_thumbor_post_response

        self.patcher_delete = mock.patch('django_thumborstorage.storages.requests.delete')
        self.MockDeleteClass = self.patcher_delete.start()
        self.MockDeleteClass.side_effect = mocked_thumbor_delete_allowed_response

    def tearDown(self):
        self.patcher_get.stop()
        self.patcher_post.stop()
        self.patcher_delete.stop()


class ThumborStorageFileTest(DjangoThumborTestCase):
    def test_get_file(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        thumbor_file.file
        self.MockGetClass.assert_called_with("%s%s" % (settings.THUMBOR_RW_SERVER, filename))

    def test_get_file_post_django_3_2_11(self):
        # See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        thumbor_file.file
        self.MockGetClass.assert_called_with("%s/%s" % (settings.THUMBOR_RW_SERVER, filename))

    def test_size(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        size = thumbor_file.size
        self.MockGetClass.assert_called_with(f'{settings.THUMBOR_RW_SERVER}{filename}')
        self.assertEqual(size, 9730)

    def test_size_post_django_3_2_11(self):
        # See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        size = thumbor_file.size
        self.MockGetClass.assert_called_with(f'{settings.THUMBOR_RW_SERVER}/{filename}')
        self.assertEqual(size, 9730)

    def test_read(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        content = thumbor_file.read()
        self.MockGetClass.assert_called_with(f'{settings.THUMBOR_RW_SERVER}{filename}')
        self.assertEqual(len(content), 9730)

    def test_read_post_django_3_2_11(self):
        # See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        thumbor_file = storages.ThumborStorageFile(filename, mode='rb')
        content = thumbor_file.read()
        self.MockGetClass.assert_called_with(f'{settings.THUMBOR_RW_SERVER}/{filename}')
        self.assertEqual(len(content), 9730)

    def test_write_jpeg(self):
        filename = 'people/HannibalSmith.jpg'
        content = ContentFile(open(f'{IMAGE_DIR}/HannibalSmith.jpg', "rb").read())
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        thumbor_file.write(content=content)
        self.MockPostClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/image",
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/jpeg", "Slug": filename})
        self.assertEqual(thumbor_file._location, f'/image/oooooo32chars_random_idooooooooo/{filename}')

    def test_write_png(self):
        filename = 'foundations/gnu.png'
        content = ContentFile(open(f'{IMAGE_DIR}/gnu.png', "rb").read())
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        thumbor_file.write(content=content)
        self.MockPostClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/image",
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/png", "Slug": filename})
        self.assertEqual(thumbor_file._location, f'/image/oooooo32chars_random_idooooooooo/{filename}')

    def test_write_image_too_small(self):
        filename = 'beasts/bouboune.png'
        content = ContentFile(open(f'{IMAGE_DIR}/bouboune.png', "rb").read())
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.ThumborPostException, thumbor_file.write, content=content)

    def test_write_unicode(self):
        filename = u'foundations/呵呵.png'
        filename_encoded = 'foundations/%E5%91%B5%E5%91%B5.png'
        content = ContentFile(open(f'{IMAGE_DIR}/gnu.png', "rb").read())
        thumbor_file = storages.ThumborStorageFile(filename, mode="w")
        thumbor_file.write(content=content)
        self.MockPostClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/image",
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/png", "Slug": filename_encoded})
        self.assertEqual(thumbor_file._location, f'/image/oooooo32chars_random_idooooooooo/{filename}')

    def test_delete_allowed(self):
        filename = '/image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        thumbor_file.delete()
        self.MockDeleteClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")
        # TODO test status_code == 204 (how ?)

        filename = '/image/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.NotFoundException, thumbor_file.delete)

    def test_delete_allowed_post_django_3_2_11(self):
        # See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        filename = 'image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        thumbor_file.delete()
        self.MockDeleteClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/{filename}")
        # TODO test status_code == 204 (how ?)

        filename = '/image/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.NotFoundException, thumbor_file.delete)

    def test_delete_not_allowed(self):
        self.MockDeleteClass.side_effect = mocked_thumbor_delete_not_allowed_response
        filename = '/image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)

        filename = '/image/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)

    def test_delete_not_allowed_post_django_3_2_11(self):
        # See https://github.com/django/django/commit/6d343d01c57eb03ca1c6826318b652709e58a76e
        self.MockDeleteClass.side_effect = mocked_thumbor_delete_not_allowed_response
        filename = 'image/oooooo32chars_random_idooooooooo/foundations/gnu.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)

        filename = '/mage/oooooo32chars_random_idooooooooo/does_not_exists.png'
        thumbor_file = storages.ThumborStorageFile(filename, mode="wb")
        self.assertRaises(exceptions.MethodNotAllowedException, thumbor_file.delete)


class ThumborStorageTest(DjangoThumborTestCase):
    def setUp(self):
        super().setUp()
        self.storage = storages.ThumborStorage()

    def test_url(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         f'{settings.THUMBOR_SERVER}/qn6d7XNEzldMxgE8t4oVjEbEsDg=/5247a82854384f228c6fba432c67e6a8')

    def test_url_post_django_3_2_11(self):
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         f'{settings.THUMBOR_SERVER}/qn6d7XNEzldMxgE8t4oVjEbEsDg=/5247a82854384f228c6fba432c67e6a8')

    def test_key(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.key(filename), '5247a82854384f228c6fba432c67e6a8')

        filename = '/image/5247a82854384f228c6fba432c67e6a8'
        self.assertEqual(self.storage.key(filename), '5247a82854384f228c6fba432c67e6a8')

    def test_key_post_django_3_2_11(self):
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.key(filename), '5247a82854384f228c6fba432c67e6a8')

        filename = 'image/5247a82854384f228c6fba432c67e6a8'
        self.assertEqual(self.storage.key(filename), '5247a82854384f228c6fba432c67e6a8')

    def test_size(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        size = self.storage.size(filename)
        self.MockGetClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")
        self.assertEqual(size, 9730)

    def test_save(self):
        filename = 'people/HannibalSmith.jpg'
        content = ContentFile(open(f'{IMAGE_DIR}/HannibalSmith.jpg', "rb").read())
        response = self.storage.save(filename, content)
        self.MockPostClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/image",
                                              data=content.file.read(),
                                              headers={"Content-Type": "image/jpeg", "Slug": filename})
        self.assertEqual(response, f'image/oooooo32chars_random_idooooooooo/{filename}')

    def test_delete(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.storage.delete(filename)
        self.MockDeleteClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")

    def test_delete_post_django_3_2_11(self):
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.storage.delete(filename)
        self.MockDeleteClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/{filename}")

    def test_exists(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertTrue(self.storage.exists(filename))
        self.MockGetClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/DoesNoyExists.jpg'
        self.assertFalse(self.storage.exists(filename))
        filename = 'people/new/TempletonPeck.jpg'
        self.assertFalse(self.storage.exists(filename))

    def test_exists_post_django_3_2_11(self):
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertTrue(self.storage.exists(filename))
        self.MockGetClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}/{filename}")
        filename = 'image/5247a82854384f228c6fba432c67e6a8/people/new/DoesNoyExists.jpg'
        self.assertFalse(self.storage.exists(filename))
        filename = 'people/new/TempletonPeck.jpg'
        self.assertFalse(self.storage.exists(filename))


class ThumborMigrationStorageTest(DjangoThumborTestCase):
    def setUp(self):
        super().setUp()
        self.storage = storages.ThumborMigrationStorage()

    def test_is_thumbor(self):
        self.assertTrue(self.storage.is_thumbor('/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'))
        self.assertTrue(self.storage.is_thumbor('/image/5247a82854384f228c6fba432c67e6a8'))
        self.assertTrue(self.storage.is_thumbor('/image/5247a82854384f228c6fba432c67e6a8.jpg'))
        self.assertFalse(self.storage.is_thumbor('images/people/new/TempletonPeck.jpg'))
        self.assertFalse(self.storage.is_thumbor('/image/5247a82854384f228c6fba432c67e6a8BlahBlahBlah'))

    def test_is_thumbor_post_django_3_2_11(self):
        self.assertTrue(self.storage.is_thumbor('image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'))
        self.assertTrue(self.storage.is_thumbor('image/5247a82854384f228c6fba432c67e6a8'))
        self.assertTrue(self.storage.is_thumbor('image/5247a82854384f228c6fba432c67e6a8.jpg'))
        self.assertFalse(self.storage.is_thumbor('images/people/new/TempletonPeck.jpg'))
        self.assertFalse(self.storage.is_thumbor('image/5247a82854384f228c6fba432c67e6a8BlahBlahBlah'))

    def test_url_thumbor(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         f'{settings.THUMBOR_SERVER}/qn6d7XNEzldMxgE8t4oVjEbEsDg=/5247a82854384f228c6fba432c67e6a8')

    def test_key_thumbor(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.key(filename), '5247a82854384f228c6fba432c67e6a8')

    def test_path_thumbor(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        with self.assertRaises(NotImplementedError):
            self.storage.path(filename)

    def test_delete_thumbor(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.storage.delete(filename)
        self.MockDeleteClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")

    def test_exists_thumbor(self):
        filename = '/image/5247a82854384f228c6fba432c67e6a8/people/new/TempletonPeck.jpg'
        self.assertTrue(self.storage.exists(filename))
        self.MockGetClass.assert_called_with(f"{settings.THUMBOR_RW_SERVER}{filename}")

    def test_url_filesystem(self):
        filename = 'images/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.url(filename),
                         f'{settings.MEDIA_URL}images/people/new/TempletonPeck.jpg')

    def test_key_filesystem(self):
        filename = 'images/people/new/TempletonPeck.jpg'
        with self.assertRaises(NotImplementedError):
            self.storage.key(filename)

    def test_path_filesystem(self):
        filename = 'images/people/new/TempletonPeck.jpg'
        self.assertEqual(self.storage.path(filename), '/media/images/people/new/TempletonPeck.jpg')

    def test_delete_filesytem(self):
        filename = 'images/people/new/TempletonPeck.jpg'
        # Note: FileSystemStorage does not raises exception if the file does not exists.
        self.storage.delete(filename)
        assert not self.MockDeleteClass.called, "Should not DELETE on Thumbor."

    def test_exists_filesystem(self):
        filename = 'images/people/new/TempletonPeck.jpg'
        self.storage.exists(filename)
        assert not self.MockGetClass.called, "Should not GET on Thumbor."


class UtilsTest(DjangoThumborTestCase):
    def test_readonly_to_rw_url(self):
        readonly_url = f"{settings.THUMBOR_SERVER}/a3JtvxkedrrhuuCZo39Sxe0aTYY=/e8a82fa321e344dfaddcbaa997845302"
        self.assertEqual(storages.readonly_to_rw_url(readonly_url),
                         f'{settings.THUMBOR_RW_SERVER}/image/e8a82fa321e344dfaddcbaa997845302')

        readonly_url = f"{settings.THUMBOR_SERVER}/a3JtvxkedrrhuuCZo39Sxe0aTYY=/e8a82fa321e344dfaddcbaa997845302.jpg"
        self.assertEqual(storages.readonly_to_rw_url(readonly_url),
                         f'{settings.THUMBOR_RW_SERVER}/image/e8a82fa321e344dfaddcbaa997845302.jpg')

        readonly_url = f"{settings.THUMBOR_SERVER}/a3JtvxkedrrhuuCZo39Sxe0aTYY=/e8a82fa321e344dfaddcbaa997845302/foo.jpg"
        self.assertEqual(storages.readonly_to_rw_url(readonly_url),
                         f'{settings.THUMBOR_RW_SERVER}/image/e8a82fa321e344dfaddcbaa997845302/foo.jpg')

    def test_request_with_unicode_name(self):
        filename = '/image/oooooo32chars_random_idooooooooo/foundations/呵呵.png'
        filename_encoded = '/image/oooooo32chars_random_idooooooooo/foundations/%E5%91%B5%E5%91%B5.png'
        self.patcher_get.stop()
        # checks that requests encodes a unicode url as expected
        with mock.patch('requests.sessions.Session.send') as mocked_send:
            requests.get(storages.thumbor_original_image_url(filename))
            [prepared_request], _ = mocked_send.call_args
            self.assertEqual(
                prepared_request.url,
                storages.thumbor_original_image_url(filename_encoded))
        self.patcher_get.start()


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ThumborStorageTest)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborStorageFileTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ThumborMigrationStorageTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UtilsTest))
    return suite
