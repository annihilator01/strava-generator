from django.db import models
from django.template.defaultfilters import truncatechars


class Visitor(models.Model):
    ip = models.CharField(
        db_column='ip',
        max_length=39,
        null=False,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip


class Visit(models.Model):
    visitor = models.ForeignKey(
        'Visitor',
        on_delete=models.SET_NULL,
        null=True
    )

    user_agent = models.TextField(
        db_column='user_agent',
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.visitor)


class Action(models.Model):
    visitor = models.ForeignKey(
        'Visitor',
        on_delete=models.SET_NULL,
        null=True,
    )

    action_url = models.TextField(
        db_column='action_url',
        null=False,
    )

    user_agent = models.TextField(
        db_column='user_agent',
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def short_action_url(self):
        return truncatechars(self.action_url, 50)

    def __str__(self):
        return str(self.visitor)
