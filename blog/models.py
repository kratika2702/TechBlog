from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    cont = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blogs')

    def __str__(self):
        return self.title
