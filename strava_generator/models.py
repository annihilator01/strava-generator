from django.db import models


class Visitor(models.Model):
    ip = models.CharField('ip', max_length=39)

    def __str__(self):
        return self.ip
