from django.contrib import admin

from apps.communications.models import Message, MessageReadReceipt, MessageRecipient


class MessageRecipientInline(admin.TabularInline):
    model = MessageRecipient
    extra = 0
    fields = (
        "user",
        "student",
        "status",
        "delivered_at",
        "first_read_at",
        "last_read_at",
        "read_count",
    )
    readonly_fields = (
        "delivered_at",
        "first_read_at",
        "last_read_at",
        "read_count",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "sender",
        "audience",
        "priority",
        "status",
        "requires_read_confirmation",
        "sent_at",
        "created_at",
    )
    list_filter = (
        "status",
        "audience",
        "priority",
        "requires_read_confirmation",
        "school",
        "created_at",
    )
    search_fields = (
        "title",
        "body",
        "sender__username",
        "sender__email",
        "school__name",
    )
    date_hierarchy = "created_at"
    inlines = [MessageRecipientInline]


@admin.register(MessageRecipient)
class MessageRecipientAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "user",
        "student",
        "status",
        "delivered_at",
        "first_read_at",
        "last_read_at",
        "read_count",
    )
    list_filter = (
        "status",
        "message__school",
        "created_at",
    )
    search_fields = (
        "message__title",
        "user__username",
        "user__email",
        "student__first_name",
        "student__last_name",
    )
    date_hierarchy = "created_at"


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "read_by",
        "read_at",
        "ip_address",
    )
    list_filter = (
        "read_at",
        "recipient__message__school",
    )
    search_fields = (
        "recipient__message__title",
        "read_by__username",
        "read_by__email",
        "ip_address",
    )
    readonly_fields = (
        "recipient",
        "read_by",
        "read_at",
        "ip_address",
        "user_agent",
        "metadata",
    )
    date_hierarchy = "read_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
