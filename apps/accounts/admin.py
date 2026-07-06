from django.contrib import admin

# Register your models here.


from apps.accounts.models import (
    AccessGroup,
    AccessGroupPermission,
    UserAccessGroup,
    UserPermissionOverride,
)


class AccessGroupPermissionInline(admin.TabularInline):
    model = AccessGroupPermission
    extra = 0
    fields = ("permission_code", "allowed")


class UserAccessGroupInline(admin.TabularInline):
    model = UserAccessGroup
    extra = 0
    fields = ("user", "is_active", "assigned_by", "assigned_at")
    readonly_fields = ("assigned_at",)


@admin.register(AccessGroup)
class AccessGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school",
        "is_system_default",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = (
        "school",
        "is_system_default",
        "is_active",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "school__name",
    )
    inlines = [AccessGroupPermissionInline, UserAccessGroupInline]
    date_hierarchy = "created_at"


@admin.register(AccessGroupPermission)
class AccessGroupPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "permission_code",
        "allowed",
        "created_at",
    )
    list_filter = (
        "allowed",
        "group__school",
        "created_at",
    )
    search_fields = (
        "group__name",
        "group__school__name",
        "permission_code",
    )


@admin.register(UserAccessGroup)
class UserAccessGroupAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "group",
        "is_active",
        "assigned_by",
        "assigned_at",
    )
    list_filter = (
        "is_active",
        "group__school",
        "assigned_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "group__name",
        "group__school__name",
    )
    date_hierarchy = "assigned_at"


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "school",
        "permission_code",
        "allowed",
        "is_active",
        "assigned_by",
        "assigned_at",
    )
    list_filter = (
        "allowed",
        "is_active",
        "school",
        "assigned_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "school__name",
        "permission_code",
        "reason",
    )
    date_hierarchy = "assigned_at"
