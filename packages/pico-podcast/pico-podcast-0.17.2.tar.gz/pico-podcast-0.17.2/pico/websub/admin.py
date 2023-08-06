from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'hub', 'expires')
    readonly_fields = ('topic', 'hub', 'confirmed', 'lease_seconds')
    exclude = ('secret',)

    def has_add_permission(self, request):
        return False

    def delete_model(self, request, obj):
        obj.unsubscribe()
