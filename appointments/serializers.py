from rest_framework import serializers
from .models import CalendarOwner, Availability, Appointment


class CalendarOwnerSerializer(serializers.Serializer):
    owner_name = serializers.CharField(max_length=100)
    owner_email = serializers.EmailField(max_length=254)

    def validate_owner_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("The 'owner_name' must be at least 3 characters.")
        return value

    def validate_owner_email(self, value):
        return value
    
class TimeSlotSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

class AvailabilitySerializer(serializers.Serializer):
    monday = TimeSlotSerializer(many=True, required=False)
    tuesday = TimeSlotSerializer(many=True, required=False)
    wednesday = TimeSlotSerializer(many=True, required=False)
    thursday = TimeSlotSerializer(many=True, required=False)
    friday = TimeSlotSerializer(many=True, required=False)
    saturday = TimeSlotSerializer(many=True, required=False)
    sunday = TimeSlotSerializer(many=True, required=False)

    def validate(self, attrs):
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day, _ in attrs.items():
            if day.lower() not in valid_days:
                raise serializers.ValidationError(f"{day} is not a valid day.")
        return attrs


class SearchAvailableSlotsSerializer(serializers.Serializer):
    owner_email = serializers.EmailField()
    date = serializers.DateField()

class BookAppointmentSerializer(serializers.Serializer):
    owner_email = serializers.EmailField()
    invitee_name = serializers.CharField(max_length=100)
    invitee_email = serializers.EmailField(max_length=254)
    start_time = serializers.DateTimeField()


class UpcomingAppointmentsSerializer(serializers.Serializer):
    owner_email = serializers.EmailField()

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['invitee_name', 'invitee_email', 'start_time', 'end_time', 'calendar_owner']