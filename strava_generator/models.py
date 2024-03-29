import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models, transaction
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


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


########################################################################################################################


class CustomUser(AbstractUser):
    username_validator = ASCIIUsernameValidator()

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

    total_uses_num = models.IntegerField(
        db_column='total_uses_num',
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Custom user'
        verbose_name_plural = 'Custom users'

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.active_usage_token:
            if self.active_usage_token.status == UsageToken.UsageTokenStatus.INACTIVE:
                self.active_usage_token = None
            elif self.active_usage_token.status != UsageToken.UsageTokenStatus.INUSE:
                self.active_usage_token.status = self.active_usage_token.UsageTokenStatus.INUSE
                self.active_usage_token.save()
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


def create_unique_value():
    value = get_random_string(length=32)
    while UsageToken.objects.filter(value=value):
        value = get_random_string(length=32)
    return value


class UsageToken(models.Model):
    class UsageTokenStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INUSE = 'in-use', _('In use'),
        INACTIVE = 'inactive', _('Inactive'),

    value = models.CharField(
        db_column='value',
        max_length=32,
        default=create_unique_value,
        editable=False,
        unique=True,
    )

    status = models.TextField(
        db_column='status',
        choices=UsageTokenStatus.choices,
        default=UsageTokenStatus.ACTIVE,
    )

    uses_left = models.IntegerField(
        db_column='uses_left',
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.uses_left <= 0:
            self.status = self.UsageTokenStatus.INACTIVE
        super(UsageToken, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.value)


########################################################################################################################


class Action(models.Model):
    user = models.ForeignKey(
        'CustomUser',
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
        return str(self.user)


class GpxGenerationHistory(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
    )

    from_location = models.TextField(
        db_column='from_location',
        null=True,
    )

    to_location = models.TextField(
        db_column='to_location',
        null=True,
    )

    activity_type = models.CharField(
        db_column='activity_type',
        max_length=100,
        null=True,
    )

    distance = models.IntegerField(
        db_column='distance',
        null=True,
    )

    end_time = models.CharField(
        db_column='finish_time',
        max_length=100,
        null=True,
    )

    gpx = models.TextField(
        db_column='gpx',
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'GPX generation history'
        verbose_name_plural = 'GPX generation history'

    def __str__(self):
        return str(self.user)
