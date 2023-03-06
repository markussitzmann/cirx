from django.urls import path

from . import views

urlpatterns = [
    path('neon/<str:string>', views.neon),
    path('compounds/<int:cid>', views.compounds, name="compounds"),
    path('images/<int:cid>', views.images, name="images-cid"),
    path('images/<str:string>', views.images, name="images-string"),
    path('sandbox/', views.sandbox, name="sandbox"),
]