from ..models import Role, ERole

def find_by_name(role_name):
    try:
        return Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        return None
