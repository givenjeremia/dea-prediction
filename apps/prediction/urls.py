
from django.urls import include, path

from . import views

urlpatterns = [
    path('predict/', views.loadModelPrediction, name='loadModelPrediction'),
]