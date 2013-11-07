# -*- coding: utf-8 -*-

from django.contrib import admin
from my_app import models


admin.site.register(models.Person)
admin.site.register(models.PersonNew)
admin.site.register(models.PersonFileSystem)
