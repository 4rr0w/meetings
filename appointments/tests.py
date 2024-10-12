from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime, timedelta
from .models import CalendarOwner, Availability, Appointment


def get_next_monday():
    """Get the date and time of the next upcoming Monday."""
    today = datetime.utcnow().date()
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    return datetime.combine(next_monday, datetime.min.time()) 


class CalendarAPIUnitTests(TestCase):
    
    def setUp(self):
        """Set up test data for calendar owner before running the tests."""
        self.client = APIClient()
        self.calendar_owner_data = {
            "owner_name": "Himanshu",
            "owner_email": "himanshu.anuragi@mail.com"
        }
        self.calendar_owner = CalendarOwner.objects.create(
            name=self.calendar_owner_data["owner_name"],
            email=self.calendar_owner_data["owner_email"]
        )

    def create_availability(self, day_of_week, start_time, end_time):
        """Helper function to create an availability for a specific day and time range."""
        return Availability.objects.create(
            calendar_owner=self.calendar_owner,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )

    def book_appointment(self, start_time, invitee_name="Invitee", invitee_email="invitee@mail.com"):
        """Helper function to book an appointment for a calendar owner."""
        return Appointment.objects.create(
            calendar_owner=self.calendar_owner,
            invitee_name=invitee_name,
            invitee_email=invitee_email,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1)
        )

    def get_availability_data(self):
        """Return sample availability data to be used in tests."""
        return {
            "owner_name": "Himanshu",
            "owner_email": "himanshu.anuragi@mail.com",
            "availability": {
                "Monday": [
                    {"start_time": "09:00:00", "end_time": "12:00:00"},
                    {"start_time": "13:00:00", "end_time": "15:00:00"}
                ],
                "Wednesday": [
                    {"start_time": "10:00:00", "end_time": "12:00:00"}
                ]
            }
        }

    def test_create_availability(self):
        """Test creating availability for a calendar owner."""
        url = reverse('availability-setup')
        response = self.client.post(url, self.get_availability_data(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 3)
        Availability.objects.all().delete()

    def test_create_availability_missing_data(self):
        """Test creating availability with missing owner data."""
        invalid_data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "availability": {
                "Monday": [
                    {"start_time": "09:00:00", "end_time": "12:00:00"}
                ]
            }
        }
        url = reverse('availability-setup')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 0)

    def test_create_availability_invalid_mail(self):
        """Test creating availability with an invalid email format."""
        invalid_data = {
            "owner_name": "himanshu",
            "owner_email": "himanshu.anuragimail.com",
            "availability": {
                "Monday": [
                    {"start_time": "09:00:00", "end_time": "12:00:00"}
                ]
            }
        }
        url = reverse('availability-setup')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 0)

    def test_search_available_slots(self):
        """Test searching for available time slots."""
        self.create_availability('Monday', '09:00:00', '12:00:00')
        url = reverse('search-available-slots')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email, 'date': '2024-10-14'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        Availability.objects.all().delete()

    def test_search_partial_available_slots(self):
        """Test searching for partially available slots."""
        self.create_availability('Monday', '09:15:00', '12:00:00')
        url = reverse('search-available-slots')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email, 'date': '2024-10-14'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        Availability.objects.all().delete()

    def test_search_past_date_availability(self):
        """Test searching for available slots in the past should return no availability."""
        past_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        url = reverse('search-available-slots')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email, 'date': past_date})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Cannot search availability for past dates.')

    def test_search_available_slots_no_availability(self):
        """Test searching for available slots when no availability exists."""
        url = reverse('search-available-slots')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email, 'date': '2024-10-15'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_doublebook_appointment_fail(self):
        """Test attempting to book an appointment that overlaps an existing one."""
        self.create_availability('Monday', '09:00:00', '10:00:00')
        self.book_appointment(datetime(2024, 10, 14, 9, 0))
        
        data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "invitee_name": "New Invitee",
            "invitee_email": "newinvitee@mail.com",
            "start_time": "2024-10-15T09:00:00"
        }
        url = reverse('book-appointment')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        Appointment.objects.all().delete()
        Availability.objects.all().delete()

    def test_unavailable_slot_appointment_fail(self):
        """Test booking an appointment in a time slot without availability."""
        self.create_availability('Monday', '11:00:00', '12:00:00')
        next_monday = get_next_monday() + timedelta(hours=9)
        
        data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "invitee_name": "New Invitee",
            "invitee_email": "newinvitee@mail.com",
            "start_time": next_monday.strftime("%Y-%m-%dT%H:%M:%S")
        }

        url = reverse('book-appointment')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        Appointment.objects.all().delete()
        Availability.objects.all().delete()

    def test_book_exactly_at_availability_boundary_fail(self):
        """Test booking an appointment at the exact end of an availability window."""
        self.create_availability('Monday', '09:00:00', '12:00:00')
        next_monday = get_next_monday().replace(hour=12)
        data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "invitee_name": "Boundary Time Booking",
            "invitee_email": "himanshuy@mail.com",
            "start_time": next_monday.strftime("%Y-%m-%dT%H:%M:%S")
        }
        url = reverse('book-appointment')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        Appointment.objects.all().delete()
        Availability.objects.all().delete()

    def test_invalid_slot_at_availability_fail(self):
        """Test booking an appointment in a time slot that overlaps partially."""
        self.create_availability('Monday', '09:00:00', '12:00:00')
        next_monday = get_next_monday().replace(hour=11, minute=15)
        data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "invitee_name": "Boundary Time Booking",
            "invitee_email": "himanshuy@mail.com",
            "start_time": next_monday.strftime("%Y-%m-%dT%H:%M:%S")
        }
        url = reverse('book-appointment')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        Appointment.objects.all().delete()
        Availability.objects.all().delete()

    def test_valid_slot_appointment_success(self):
        """Test successfully booking an appointment in a valid available slot."""
        self.create_availability('Monday', '11:00:00', '12:00:00')
        next_monday = get_next_monday() + timedelta(hours=11)
         
        data = {
            "owner_email": "himanshu.anuragi@mail.com",
            "invitee_name": "New Invitee",
            "invitee_email": "newinvitee@mail.com",
            "start_time": next_monday.strftime("%Y-%m-%dT%H:%M:%S")
        }

        url = reverse('book-appointment')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_double_appointment_fail(self):
        """Test successfully booking multiple appointments in valid slots."""
        self.create_availability('Monday', '11:00:00', '13:00:00')
        next_monday = get_next_monday() + timedelta(hours=11)

        for i in range(2):
            data = {
                "owner_email": "himanshu.anuragi@mail.com",
                "invitee_name": f"New Invitee {i+1}",
                "invitee_email": f"newinvitee{i+1}@mail.com",
                "start_time": next_monday.strftime("%Y-%m-%dT%H:%M:%S")
            }

            url = reverse('book-appointment')
            response = self.client.post(url, data, format='json')
            if i == 0:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Appointment.objects.count(), 1)

    def test_list_appointments(self):
        """Test if appointments are correctly listed for a calendar owner."""
        self.create_availability('Monday', '09:00:00', '12:00:00')
        appointment_1 = self.book_appointment(datetime(2024, 10, 14, 9, 0))
        appointment_2 = self.book_appointment(datetime(2024, 10, 14, 10, 0), invitee_name="Invitee 2")

        url = reverse('list-appointments')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 
        self.assertEqual(response.data[0]["invitee_name"], appointment_1.invitee_name)
        self.assertEqual(response.data[1]["invitee_name"], appointment_2.invitee_name)

        Appointment.objects.all().delete()

    def test_list_appointments_no_appointments(self):
        """Test if the system correctly handles listing when no appointments exist."""
        url = reverse('list-appointments')
        response = self.client.get(url, {'owner_email': self.calendar_owner.email})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 


    def tearDown(self):
        """Clean up test data after tests run."""
        Appointment.objects.all().delete()
        Availability.objects.all().delete()