from django.contrib import admin
from .models import Visitor, Visit, Action


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'created_at')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'created_at')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'short_action_url', 'created_at')
