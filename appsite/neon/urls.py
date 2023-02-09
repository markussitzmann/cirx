from django.urls import path

from . import views

urlpatterns = [
    path('neon/<str:string>/', views.neon),
]