from django.contrib import admin

from apps.auditlog.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "school",
        "actor_user",
        "actor_role",
        "action",
        "module",
        "object_type",
        "object_repr",
        "ip_address",
    )
    list_filter = (
        "action",
        "module",
        "school",
        "created_at",
    )
    search_fields = (
        "actor_user__username",
        "actor_user__email",
        "actor_role",
        "module",
        "object_type",
        "object_id",
        "object_repr",
        "ip_address",
    )
    readonly_fields = (
        "school",
        "actor_user",
        "actor_role",
        "action",
        "module",
        "object_type",
        "object_id",
        "object_repr",
        "changes_before",
        "changes_after",
        "metadata",
        "ip_address",
        "user_agent",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
