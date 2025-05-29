from django.core.management.base import BaseCommand
from api.models.badge import Badge

BADGES = [
    {"name": "First Streak", "description": "Read for 2 days in a row", "streak_required": 2},
    {"name": "Reading Champ", "description": "Read for 5 days in a row", "streak_required": 5},
    {"name": "Book Lover", "description": "Read for 10 days in a row", "streak_required": 10},
    {"name": "Bookworm", "description": "Read for 20 days in a row", "streak_required": 20},
    {"name": "Book Wizard", "description": "Read for 30 days in a row", "streak_required": 30},
    {"name": "Book Enthusiast", "description": "Read for 50 days in a row", "streak_required": 50},
    {"name": "Book Adventurer", "description": "Read for 100 days in a row", "streak_required": 100},
    {"name": "Book Explorer", "description": "Read for 200 days in a row", "streak_required": 200},
    {"name": "Book Scholar", "description": "Read for 300 days in a row", "streak_required": 300},
    {"name": "Book Connoisseur", "description": "Read for 500 days in a row", "streak_required": 500},
    {"name": "Book Expert", "description": "Read for 1000 days in a row", "streak_required": 1000},
    {"name": "Book Guru", "description": "Read for 2000 days in a row", "streak_required": 2000},
]

class Command(BaseCommand):
    help = "Seed badges into database"

    def handle(self, *args, **kwargs):
        for badge_data in BADGES:
            badge, created = Badge.objects.get_or_create(name=badge_data["name"], defaults=badge_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Badge created: {badge.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Badge already exists: {badge.name}"))
