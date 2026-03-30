from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('book/<int:train_id>/', views.book_train, name="book"),
    path('cancel/<int:booking_id>/', views.cancel_booking, name="cancel"),
    path('mybookings/', views.my_bookings, name="mybookings"),
    path('download/<int:booking_id>/', views.download_ticket, name="download"),
    path('logout/', views.logout_view, name="logout"),
]