from django.db import models
from django.conf import settings
from api.models.book import Book

class Bookmark(models.Model):
    """
    Model to store bookmarks for books.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    note = models.TextField(blank=True, null=True)  # Optional user note
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book", "page_number")  # 🔥 Prevent duplicate bookmarks

    def __str__(self):
        return f"Bookmark - {self.book.title} (Page {self.page_number})"



class Highlight(models.Model):
    """
    Model to store multiple highlights per book page.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    text = models.TextField()  # 🔥 The highlighted text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["page_number", "created_at"]  # 🔥 Order highlights by page & time

    def __str__(self):
        return f"Highlight - {self.book.title} (Page {self.page_number}): {self.text[:30]}..."