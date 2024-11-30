
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index-data'),
    path('predict/', views.LoadModelPredictionView.as_view(), name='loadModelPrediction'),
]