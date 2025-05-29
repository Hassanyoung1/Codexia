from django.core.management.base import BaseCommand
from api.models.focus import FocusSession
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Manage focus sessions via console."

    def add_arguments(self, parser):
        parser.add_argument("action", type=str, choices=["start", "end", "stats"])
        parser.add_argument("--user", type=str, help="Username of the user")
        parser.add_argument("--duration", type=int, default=25, help="Focus session duration")

    def handle(self, *args, **options):
        user = User.objects.get(username=options["user"])
        action = options["action"]

        if action == "start":
            session = FocusSession.objects.create(user=user, duration_minutes=options["duration"])
            self.stdout.write(f"Started focus session for {user.username} ({session.duration_minutes} min).")

        elif action == "end":
            session = FocusSession.objects.filter(user=user, completed=False).last()
            if not session:
                self.stdout.write("No active session found.")
                return
            session.end_session()
            self.stdout.write(f"Ended session. Focus Score: {session.calculate_focus_score()}%")

        elif action == "stats":
            sessions = FocusSession.objects.filter(user=user)
            total_time = sum([s.duration_minutes for s in sessions])
            avg_score = sum([s.calculate_focus_score() for s in sessions]) / max(1, len(sessions))
            self.stdout.write(f"Total Focus Time: {total_time} min, Avg Focus Score: {avg_score}%")
