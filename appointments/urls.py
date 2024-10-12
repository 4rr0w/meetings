from django.urls import path
from .views import AvailabilitySetupAPI, SearchAvailableSlotsAPI, BookAppointmentAPI, ListUpcomingAppointmentsAPI

urlpatterns = [
    path('availability/setup/', AvailabilitySetupAPI.as_view(), name='availability-setup'),
    path('availability/search/', SearchAvailableSlotsAPI.as_view(), name='search-available-slots'),
    path('appointment/book/', BookAppointmentAPI.as_view(), name='book-appointment'),
    path('appointments', ListUpcomingAppointmentsAPI.as_view(), name='list-appointments'),
]
