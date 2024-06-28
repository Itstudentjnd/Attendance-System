from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=255)
    rno = models.CharField(max_length=20)
    stream = models.CharField(max_length=255)
    std = models.CharField(max_length=10)
    mobile = models.CharField(max_length=13, default='')

    def __str__(self):
        return self.name
