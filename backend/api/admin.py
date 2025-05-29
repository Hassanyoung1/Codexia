from django.contrib import admin
from api.models.reading import ReadingGoal

admin.site.register(ReadingGoal)  # ✅ Ensure Django detects the model
