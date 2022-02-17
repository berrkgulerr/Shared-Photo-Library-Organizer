from django.db import models
# Create your models here.
from django.contrib.auth.models import User


class View_ids_of_photo(models.Model):
    iid = models.IntegerField(null=False, blank=False)


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Photo(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    image = models.ImageField(null=False, blank=False)
    tags = models.ManyToManyField(Tag, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    datetime = models.DateField(null=True, blank=True)
    photo_owner_id = models.IntegerField(null=True, blank=True)
    collection_id = models.IntegerField(null=True, blank=True)
    view_id = models.ManyToManyField(View_ids_of_photo, blank=True)
    current_view_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class View(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    photos = models.ManyToManyField(Photo, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    conjunctive = models.BooleanField(null=True, blank=True)
    startLatitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    startLongitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    endLatitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    endLongitude = models.DecimalField(max_digits=10, decimal_places=5, null=False, blank=False, default=0)
    startTime = models.DateField(null=False, blank=False)
    endTime = models.DateField(null=False, blank=False)
    view_owner_id = models.IntegerField(null=True, blank=True)
    collection_id = models.IntegerField(null=True, blank=True)
    shared_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    photos = models.ManyToManyField(Photo, blank=True)
    views = models.ManyToManyField(View, blank=True)
    collection_owner_id = models.IntegerField(null=True, blank=True)
    shared_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

