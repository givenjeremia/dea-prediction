
from django.urls import include, path

from . import views

urlpatterns = [
    path('predict/', views.LoadModelPredictionView.as_view(), name='loadModelPrediction'),
]