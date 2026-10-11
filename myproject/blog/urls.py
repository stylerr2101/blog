from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login',views.login_view, name='login'),
    path('register',views.register, name="register"),
    path('create_post', views.create_post, name="create_post"),
    path('logout', views.logout_view, name='logout'),
    path("post/<int:id>/", views.post_detail, name="post"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("post/<int:id>/like/", views.like_post, name="like_post"),
    path("post/<int:id>/comment/", views.add_comment, name="add_comment"),
    path("drafts/", views.drafts, name="drafts"),
    path("post/<int:id>/edit/", views.edit_post, name="edit_post"),
    path("post/<int:id>/delete/", views.delete_post, name="delete_post"),
]