from django.db import models


class Visitor(models.Model):
    ip = models.CharField(
        db_column='ip',
        max_length=39,
        null=False,
        unique=True
    )

    def __str__(self):
        return self.ip


class Action(models.Model):
    visitor = models.ForeignKey(
        'Visitor',
        on_delete=models.SET_NULL,
        null=True
    )

    action_url = models.TextField(
        db_column='action_url',
        null=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.visitor)
