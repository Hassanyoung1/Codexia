import hashlib
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Category(models.Model):
    """Model to store predefined book categories."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Model to store custom tags for books."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    """Model to store uploaded books and prevent duplicates."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField(upload_to="books/")
    file_hash = models.CharField(max_length=64, unique=True, blank=True, default="")  # ✅ Prevent duplicates, no NULL
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Check for duplicate books before saving."""
        if self.file:
            self.file_hash = self.calculate_file_hash()
    
            # ✅ Instead of raising ValueError, use Django's validation system
            if Book.objects.filter(file_hash=self.file_hash).exists():
                raise ValidationError("This book has already been uploaded.")
        else:
            raise ValidationError("File is required to calculate the file hash.")

    def save(self, *args, **kwargs):
        """Override save method to calculate file hash and prevent duplicates."""
        if not self.file_hash and self.file:
            self.file_hash = self.calculate_file_hash()
        self.clean()  # ✅ Ensure validation is called before saving
        super().save(*args, **kwargs)

    def calculate_file_hash(self):
        """Calculates a SHA256 hash of the file to detect duplicates."""
        hasher = hashlib.sha256()
        for chunk in self.file.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()

    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"
