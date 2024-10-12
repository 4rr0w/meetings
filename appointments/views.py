from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import CalendarOwner, Availability, Appointment
from .serializers import CalendarOwnerSerializer, SearchAvailableSlotsSerializer, BookAppointmentSerializer, \
    AppointmentSerializer, UpcomingAppointmentsSerializer, AvailabilitySerializer
from django.utils.dateparse import parse_time
from datetime import datetime, timedelta
from django.test.client import RequestFactory

class AvailabilitySetupAPI(APIView):
    def post(self, request):
        """
        Set the availability for the calendar owner. This includes:
        - Owner details (owner_name and owner_email)
        - Availability (monday-sunday and time slots)
        -----------------------------------------------------------------
        Request Example:
            POST: /api/availability/setup/
            Body:
                {
                    "owner_name": "Himanshu",
                    "owner_email": "himanshu.anuragi@mail.com",
                    "availability": {
                        "Monday": [
                            {"start_time": "09:00:00", "end_time": "11:00:00"},
                            {"start_time": "13:00:00", "end_time": "15:00:00"}
                        ],
                        "Wednesday": [
                            {"start_time": "10:00:00", "end_time": "12:00:00"}
                        ]
                    }
                }
        ------------------------------------------------------------------
        ------------------------------------------------------------------
        Response Example:
            HTTP 201 Created
            {
                "message": "Availability set successfully!"
            }
        ------------------------------------------------------------------
        """

        availability_data = request.data.get("availability", {})
        normalized_availability = {day.lower(): slots for day, slots in availability_data.items()}

        owner_serializer = CalendarOwnerSerializer(data=request.data)
        availability_serializer = AvailabilitySerializer(data=normalized_availability)

        if not availability_serializer.is_valid():
            return Response({"message": "Availability errors", "errors": availability_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        if not owner_serializer.is_valid():
            return Response({"message": "Owner errors", "errors": owner_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        calendar_owner_name = owner_serializer.validated_data.get('owner_name')
        calendar_owner_email = owner_serializer.validated_data.get('owner_email').lower()

        calendar_owner, created = CalendarOwner.objects.get_or_create(
            email=calendar_owner_email,
            defaults={'name': calendar_owner_name}
        )

        for day, time_slots in availability_serializer.validated_data.items():
            Availability.objects.filter(calendar_owner=calendar_owner, day_of_week=day).delete()

            for time_slot in time_slots:
                start_time, end_time = time_slot['start_time'], time_slot['end_time']

                if start_time > end_time:
                    return Response({"message": "Invalid time slot: start time must be before end time."}, status=status.HTTP_400_BAD_REQUEST)

                Availability.objects.create(
                    calendar_owner=calendar_owner,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )

        return Response({"message": "Availability set successfully!"}, status=status.HTTP_201_CREATED)


class SearchAvailableSlotsAPI(APIView):
    def get(self, request):
        """
        Search for available time slots for a calendar owner on a specific date. 
        It returns all available slots where no appointment exists.
        --------------------------------------------------------------------------------------------------
        Request Example:
            GET /api/appointments/available-slots/?owner_email=himanshu.anuragi@mail.com&date=2024-10-15
        --------------------------------------------------------------------------------------------------
        --------------------------------------------------------------------------------------------------
        Response Example:
            [
                {
                    "start_time": "2024-10-15T09:00:00",
                    "end_time": "2024-10-15T10:00:00"
                },
                {
                    "start_time": "2024-10-15T13:00:00",
                    "end_time": "2024-10-15T14:00:00"
                }
            ]
        --------------------------------------------------------------------------------------------------
        """

        serializer = SearchAvailableSlotsSerializer(data=request.GET)

        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        calendar_owner_email = serializer.validated_data.get('owner_email')
        date = serializer.validated_data.get('date')

        calendar_owner_email = calendar_owner_email.lower()

        calendar_owner = CalendarOwner.objects.filter(email=calendar_owner_email).first()
        if not calendar_owner:
            return Response({"message": "Calendar owner not found"}, status=status.HTTP_404_NOT_FOUND)

        availability = Availability.objects.filter(calendar_owner=calendar_owner, day_of_week=date.strftime("%A"))

        appointments = Appointment.objects.filter(calendar_owner=calendar_owner, start_time__date=date)

        available_slots = []

        for slot in availability:
            start_time = datetime.combine(date, slot.start_time)
            end_time = datetime.combine(date, slot.end_time)

            while start_time + timedelta(hours=1) <= end_time:
                if not appointments.filter(start_time=start_time).exists():
                    available_slots.append({
                        'start_time': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        'end_time': (start_time + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
                    })
                start_time += timedelta(hours=1)

        return Response(available_slots, status=status.HTTP_200_OK)

class BookAppointmentAPI(APIView):
    def post(self, request):
        """
        Book an appointment for a calendar owner. This endpoint checks if the requested time slot is available.
        -----------------------------------------------------------------
        Request Example:
            POST /api/appointments/book/
            {
                "owner_email": "himanshu.anuragi@mail.com",
                "invitee_name": "Invitee",
                "invitee_email": "invitee@mail.com",
                "start_time": "2024-10-15T09:00:00"
            }
        -----------------------------------------------------------------
        -----------------------------------------------------------------
        Response Example:
            {
                "message": "Appointment booked successfully!"
            }
        -----------------------------------------------------------------
        """
        serializer = BookAppointmentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        calendar_owner_email = serializer.validated_data.get('owner_email')
        invitee_name = serializer.validated_data.get('invitee_name')
        invitee_email = serializer.validated_data.get('invitee_email')
        start_time = serializer.validated_data.get('start_time')

        if start_time.replace(tzinfo=None) < datetime.now():
            return Response({"message": "Appointments cannot be scheduled in the past."}, status=status.HTTP_400_BAD_REQUEST)

        calendar_owner_email = calendar_owner_email.lower()

        calendar_owner = CalendarOwner.objects.filter(email=calendar_owner_email).first()
        if not calendar_owner:
            return Response({"message": "Calendar owner not found"}, status=status.HTTP_404_NOT_FOUND)

        if start_time.minute != 0:
            return Response({"message": "Slot must start at the top of the hour."}, status=status.HTTP_400_BAD_REQUEST)

        end_time = start_time + timedelta(hours=1)

        existing_appointments = Appointment.objects.filter(
            calendar_owner=calendar_owner,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if existing_appointments.exists():
            return Response({"message": "This slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)

        factory = RequestFactory()
        search_request = factory.get('/appointments/search/', {'owner_email': calendar_owner_email, 'date': start_time.date()})
        search_response = SearchAvailableSlotsAPI().get(search_request)

        available_slots = search_response.data

        if isinstance(available_slots, dict) and 'message' in available_slots:
            return Response(available_slots, status=status.HTTP_400_BAD_REQUEST)

        if not any(slot['start_time'] == start_time.strftime("%Y-%m-%dT%H:%M:%S") for slot in available_slots):
            return Response({"message": "This slot is not available."}, status=status.HTTP_400_BAD_REQUEST)

        Appointment.objects.create(
            calendar_owner=calendar_owner,
            invitee_name=invitee_name,
            invitee_email=invitee_email,
            start_time=start_time,
            end_time=end_time
        )
        return Response({"message": "Appointment booked successfully!"}, status=status.HTTP_201_CREATED)

class ListUpcomingAppointmentsAPI(APIView):
    def get(self, request):
        """
        List all upcoming appointments for a specific calendar owner, 
        including today’s appointments. No backdated appointments will be shown.
        --------------------------------------------------------------------
        Request Example:
            GET /api/appointments?owner_email=john.doe@example.com
        --------------------------------------------------------------------
        --------------------------------------------------------------------
        Response Example:
            [
                {
                    "invitee_name": "Invitee",
                    "invitee_email": "invitee@mail.com",
                    "start_time": "2024-10-15T09:00:00",
                    "end_time": "2024-10-15T10:00:00"
                }
            ]
        --------------------------------------------------------------------
        """
        serializer = UpcomingAppointmentsSerializer(data=request.query_params)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        calendar_owner_email = serializer.validated_data['owner_email']
        calendar_owner_email = calendar_owner_email.lower()

        calendar_owner = CalendarOwner.objects.filter(email=calendar_owner_email).first()
        if not calendar_owner:
            return Response({"message": "Calendar owner not found"}, status=status.HTTP_404_NOT_FOUND)

        today = datetime.utcnow().date()

        upcoming_appointments = Appointment.objects.filter(
            calendar_owner=calendar_owner,
            start_time__date__gte=today
        ).order_by('start_time')

        serializer = AppointmentSerializer(upcoming_appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
