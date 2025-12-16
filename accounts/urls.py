from django.urls import path
from .views import RegisterView, LoginView, UserListView , MenuListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path("users/", UserListView.as_view(), name="users"),
    path("menu-list/", MenuListView.as_view(), name="menu-list"),
    path("menu-list/<int:id>/", MenuListView.as_view(), name="menu-detail"),

]