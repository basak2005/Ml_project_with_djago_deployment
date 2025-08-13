from django.urls import path
from . import views

app_name = 'ml_predictor'

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict_form, name='predict_form'),
]
