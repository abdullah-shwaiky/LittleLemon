from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        l = request.user.groups.values_list('name',flat = True) # QuerySet Object
        groups = list(l)
        if 'Manager' in groups:
            return True
        return False