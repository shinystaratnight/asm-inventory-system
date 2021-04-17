from django.db import models
from django.contrib.auth.models import User

class CsvHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract = models.CharField(max_length=100)
    exported_at = models.DateTimeField(auto_now=True)
