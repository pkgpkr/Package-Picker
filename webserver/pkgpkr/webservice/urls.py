from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("login", views.login, name="login"),
    path("callback", views.callback, name="callback"),
    path("logout", views.logout, name="logout"),
    path("repositories", views.repositories, name="repositories"),
    path("repositories/<str:name>", views.recommendations, name="recommendations"),
    path("reimport-model", views.reimport_model, name="reimport-model"),
]
