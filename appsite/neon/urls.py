from django.urls import path

from . import views

urlpatterns = [
    path('cir', views.cir, name="cir"),
    path('neon/<str:string>', views.neon),
    path('neon/compounds/<int:cid>', views.compounds, name="compounds"),
    path('neon/compound-images/<int:cid>', views.compound_images, name="compound-images"),
    path('neon/records/<int:rid>', views.records, name="records"),
    path('neon/record-images/<int:rid>', views.record_images, name="record-images"),
    #path('images/<str:string>', views.images, name="images-string"),
    path('sandbox/', views.sandbox, name="sandbox"),
    path('', views.cover, name="cover"),
]