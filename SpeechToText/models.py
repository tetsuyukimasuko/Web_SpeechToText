from django.db import models

# Create your models here.

class WAV(models.Model):
    wav=models.FileField(upload_to='SpeechToText')
