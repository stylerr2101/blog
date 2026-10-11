from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    STATUS = (
        ("draft", "Черновик"),
        ("published", "Опубликован"),
    )
    status = models.CharField(max_length=15, choices=STATUS, default="draft")
    name = models.CharField(max_length=200)
    description = models.TextField()
    img = models.ImageField(upload_to="posts/", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.name}"
