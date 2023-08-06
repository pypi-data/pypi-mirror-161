from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent')
    readonly_fields = ('name', 'email', 'subject', 'body', 'sent')

    def has_add_permission(self, request):
        return False
