from django.db import models
from django import forms

# Create your models here.

class Sentence(models.Model):
    sentence = models.CharField(max_length=2000)
    syntactic_analysis = models.CharField(max_length=2000, default='')
    translation = models.CharField(max_length=2000)
    learned = models.BooleanField(default=False)
    add_date = models.DateTimeField('date added',auto_now_add=True)
    def __str__(self):
        return self.sentence

class Words(models.Model):
    word = models.CharField(max_length=200)
    pronunciation = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    mean = models.CharField(max_length=200)
    add_date = models.DateTimeField('date added',auto_now_add=True)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='words')

    def __str__(self):
        return self.word
