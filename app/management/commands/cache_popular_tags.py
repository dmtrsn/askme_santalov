from typing import Any
from django.core.management.base import BaseCommand
from app.views import cache_popular_tags



class Command(BaseCommand):
    def handle(self, *args, **options):
        cache_popular_tags()
