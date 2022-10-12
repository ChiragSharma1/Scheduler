from django.db import models

# Create your models here.


class Participant(models.Model):
    email = models.EmailField(unique=True, max_length=64)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Interview(models.Model):
    name = models.CharField(max_length=64)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Participant, related_name="interviews")

    def __str__(self):
        return self.name
