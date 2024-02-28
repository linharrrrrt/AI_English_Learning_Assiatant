from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Words, Sentence

admin.site.register(Words)
admin.site.register(Sentence)
