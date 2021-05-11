from django.contrib import admin
from .models import Visitor, Visit, Action, CustomUser, UsageToken


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'created_at')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'created_at')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'status',
        'active_usage_token',
        'total_used_num',
        'created_at',
        'updated_at',
    )


@admin.register(UsageToken)
class UsageTokenAdmin(admin.ModelAdmin):
    list_display = (
        'value',
        'uses_left',
        'created_at',
        'updated_at',
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'short_action_url', 'created_at')
