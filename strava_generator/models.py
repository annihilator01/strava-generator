import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Visitor(models.Model):
    ip = models.CharField(
        db_column='ip',
        max_length=39,
        null=False,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip


class Visit(models.Model):
    visitor = models.ForeignKey(
        'Visitor',
        on_delete=models.SET_NULL,
        null=True,
    )

    user_agent = models.TextField(
        db_column='user_agent',
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.visitor)


########################################################################################################################


class CustomUser(AbstractUser):
    class CustomUserStatus(models.TextChoices):
        ACTIVE = 'active', _('Active'),
        INACTIVE = 'inactive', _('Inactive')

    status = models.TextField(
        db_column='status',
        choices=CustomUserStatus.choices,
        default=CustomUserStatus.ACTIVE,
    )

    active_usage_token = models.ForeignKey(
        'UsageToken',
        on_delete=models.SET_NULL,
        null=True,
    )

    total_used_num = models.IntegerField(
        db_column='total_used_num',
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Custom user'
        verbose_name_plural = 'Custom users'

    def __str__(self):
        return self.username


class UsageToken(models.Model):
    value = models.UUIDField(
        db_column='value',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    uses_left = models.IntegerField(
        db_column='uses_left',
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.value)

########################################################################################################################


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
