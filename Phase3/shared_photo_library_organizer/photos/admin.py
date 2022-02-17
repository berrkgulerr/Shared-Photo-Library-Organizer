from django.contrib import admin

# Register your models here.

from .models import Photo, Collection, View, Tag

admin.site.register(Photo)
admin.site.register(Collection)
admin.site.register(View)
admin.site.register(Tag)
