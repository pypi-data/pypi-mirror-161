from django.db import models


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    sent = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ('-sent',)
        get_latest_by = 'sent'
