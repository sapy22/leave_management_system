from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


def create_group_with_permission(group_name, permission_codename):
    permission = Permission.objects.get(codename=permission_codename)

    group, created = Group.objects.get_or_create(name=group_name)
    group.permissions.add(permission)

    print(f'Group: ({group}) with Permission: ({permission}) created successfully.')


class Command(BaseCommand):
    help = 'Create groups with permissions'

    def handle(self, *args, **kwargs):
        create_group_with_permission('Officer', 'Officer')
        create_group_with_permission('Manager', 'Manager')
        create_group_with_permission('HR', 'HR')
