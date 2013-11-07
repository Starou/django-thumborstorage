from django.db import models
from django_thumborstorage.storages import ThumborStorage, ThumborMigrationStorage


class PersonManager(models.Manager):
    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)


class Person(models.Model):
    """A model that used to store images on the file-system and has been moved to Thumbor."""
    objects = PersonManager()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    def upload_path(instance, filename):
        return 'people/%s' % filename
    photo = models.ImageField('image', upload_to=upload_path,
                              storage=ThumborMigrationStorage(),
                              height_field='photo_height',
                              width_field='photo_width')
    photo_height = models.IntegerField(blank=True, null=True)
    photo_width = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def natural_key(self):
        return (self.first_name, self.last_name)

    def get_full_name(self):
        return u"%s %s" % (self.first_name, self.last_name)


class PersonNew(models.Model):
    """A model that always stored images on Thumbor."""
    objects = PersonManager()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    def upload_path(instance, filename):
        return 'people/new/%s' % filename
    photo = models.ImageField('image', upload_to=upload_path,
                              storage=ThumborStorage(),
                              height_field='photo_height',
                              width_field='photo_width')
    photo_height = models.IntegerField(blank=True, null=True)
    photo_width = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def natural_key(self):
        return (self.first_name, self.last_name)

    def get_full_name(self):
        return u"%s %s" % (self.first_name, self.last_name)


class PersonFileSystem(models.Model):
    """A model that still store images on the file-system."""
    objects = PersonManager()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    def upload_path(instance, filename):
        return 'people/fs/%s' % filename
    photo = models.ImageField('image', upload_to=upload_path,
                              height_field='photo_height',
                              width_field='photo_width')
    photo_height = models.IntegerField(blank=True, null=True)
    photo_width = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def natural_key(self):
        return (self.first_name, self.last_name)

    def get_full_name(self):
        return u"%s %s" % (self.first_name, self.last_name)
