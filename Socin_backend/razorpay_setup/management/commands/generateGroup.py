# core/management/commands/setup_plans.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Setup SaaS plan groups and permissions"

    def handle(self, *args, **kwargs):
        pro, _ = Group.objects.get_or_create(name="premium_plan")
        free, _ = Group.objects.get_or_create(name="free_plan")
        perm1 = Permission.objects.get(codename="premium_plan")
        perm2 = Permission.objects.get(codename="free_plan")
        free.permissions.add(perm2)
        pro.permissions.add(perm1)