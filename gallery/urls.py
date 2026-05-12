from django.urls import path
from .views import (
    artwork_list,
    upload_artwork,
    delete_artwork,
    get_events,
    create_event,
    delete_event,
)
from . import views

urlpatterns = [
    path('artworks/', artwork_list),
    path('upload/', upload_artwork),
    path('delete/<int:id>/', delete_artwork),

    path('events/', get_events),
    path('events/create/', create_event),
    path('events/delete/<int:id>/', delete_event),

    path('register/', views.register),
    path('login/', views.login),
]