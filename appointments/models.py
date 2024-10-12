from django.db import models

class CalendarOwner(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Availability(models.Model):
    calendar_owner = models.ForeignKey(CalendarOwner, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('calendar_owner', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.calendar_owner.name} - {self.day_of_week} ({self.start_time} - {self.end_time})"

class Appointment(models.Model):
    calendar_owner = models.ForeignKey(CalendarOwner, on_delete=models.CASCADE, related_name='appointments')
    invitee_name = models.CharField(max_length=100)
    invitee_email = models.EmailField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    agenda = models.TextField(default="")

    def __str__(self):
        return f"Appointment with {self.invitee_name} from {self.start_time} to {self.end_time}"
