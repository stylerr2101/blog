from django.contrib import admin
from .models import Category, Post, Profile, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'user', 'status', 'date')
    list_filter = ('status', 'category', 'date')
    search_fields = ('name', 'description')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'bio')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'date')
    list_filter = ('date',)
# Register your models here.
