from django.contrib import admin
from .models import (
    Visit,
    Visitor,
    CustomUser,
    UsageToken,
    Action,
    GpxGenerationHistory,
)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        'visitor',
        'user_agent',
        'created_at',
    )


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'created_at')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'status',
        'active_usage_token',
        'total_uses_num',
        'created_at',
        'updated_at',
    )


@admin.register(UsageToken)
class UsageTokenAdmin(admin.ModelAdmin):
    list_display = (
        'value',
        'status',
        'uses_left',
        'created_at',
        'updated_at',
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'short_action_url',
        'user_agent',
        'created_at',
    )


@admin.register(GpxGenerationHistory)
class GpxGenerationHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'from_location',
        'to_location',
        'end_time',
        'distance',
        'activity_type',
        'created_at',
    )
