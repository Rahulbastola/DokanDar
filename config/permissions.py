from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsApprovedVendor(BasePermission):
    """Admin (vendor) role, approved by a super admin."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.is_vendor and user.is_approved
        )


class IsVendorOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_super_admin or (user.is_vendor and user.is_approved)


class IsOwnerVendorOrSuperAdminOrReadOnly(BasePermission):
    """Read for everyone; write only for the product's own vendor or a super admin."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_super_admin or (user.is_vendor and user.is_approved))
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if user.is_super_admin:
            return True
        return obj.created_by_id == user.id
