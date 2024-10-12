# Calendar API Project

This project provides a calendar and appointment booking system using Django and Django Rest Framework (DRF). It allows users to set availability, search for available slots, and book appointments. The application is designed to manage availability on specific days of the week, provide real-time slot searching, and ensure no overlapping appointments. `sqlite` is being used to store the data.

---

## Table of Contents

1. [Project Setup](#project-setup)
2. [Django Project Setup](#django-project-setup)
3. [API Usage](#api-usage)
4. [Test Cases](#test-cases)

---

## Project Setup

### Prerequisites

Before setting up the project, make sure you have the following installed:

- Python 3.10+

### Step 1: Clone the Repository

Clone this repository to your local machine.

```bash
git clone https://github.com/4rr0w/meeting.git
cd meeting
```

### Step 2: Create and Activate Virtual Environment

Create a virtual environment to manage dependencies.

```bash
python3 -m venv venv
```

Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On Mac/Linux:

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

Install all required packages using `pip`.

```bash
pip install -r requirements.txt
```

### Step 4: Apply Migrations

Make sure to apply all migrations to set up the database schema.

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Step 5: Start the Development Server

Run the Django development server.

```bash
python3 manage.py runserver
```

The app should now be accessible at `http://127.0.0.1:8000/`.

---

## Project Components

The project is built with Django and Django Rest Framework (DRF) and includes the following main components:

- **Models**: Define the database structure for `CalendarOwner`, `Availability`, and `Appointment`.
- **Views**: Handle the logic for availability setup, searching available slots, and booking appointments.
- **URLs**: Define API endpoints for interacting with the availability and appointment system.
- **Serializers**: Handle the conversion of model instances to and from JSON format.

### Models

- **CalendarOwner**: Stores details of the owner of the calendar (name, email).
- **Availability**: Stores available time slots for a calendar owner on a specific day of the week.
- **Appointment**: Stores booked appointments, with reference to the calendar owner, invitee, and time.

### Views & APIs

- **Availability API** (`/availability/setup`): Allows owners to set their availability for specific days and times.
- **Search Available Slots API** (`/availability/search`): Allows users to search for available slots for a specific calendar owner on a given date.
- **Book Appointment API** (`/appointment/book`): Allows clients to book an appointment with the calendar owner.
- **Appointments API** (`/appointments`): Allows calendar owners to list their appointments.

---

## API Usage

### 1. **Create Availability** (POST `/availability/setup`)

This endpoint allows the calendar owner to set their availability for specific days and time slots.

#### Request

```json
{
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
```

#### Response

```json
{
  "status": "success",
  "message": "Availability created successfully"
}
```

### 2. **Search Available Slots** (GET `/api/search-slots/`)

This endpoint allows you to search for available slots for a calendar owner on a specific date.

#### Request

```json
GET /api/search-slots/?owner_email=himanshu.anuragi@mail.com&date=2024-10-14
```

#### Response

```json
[
  {"start_time": "09:00:00", "end_time": "10:00:00"},
  {"start_time": "10:00:00", "end_time": "11:00:00"},
  {"start_time": "11:00:00", "end_time": "12:00:00"}
]
```

### 3. **Book Appointment** (POST `/appointment/book`)

This endpoint allows you to book an appointment with the calendar owner.

#### Request

```json
{
  "owner_email": "himanshu.anuragi@mail.com",
  "invitee_name": "New Invitee",
  "invitee_email": "newinvitee@mail.com",
  "start_time": "2024-10-14T9:00:00"
}
```

#### Response

```json
{
  "status": "success",
  "message": "Appointment booked successfully"
}
```

### 4. **List Appointments** (GET `/appointments`)

This endpoint allows a calendar owner to list their appointments.

#### Request

```json
GET /api/appointments/?owner_email=himanshu.anuragi@mail.com
```

#### Response

```json
[
  {
    "invitee_name": "Invitee",
    "invitee_email": "invitee@mail.com",
    "start_time": "2024-10-14T09:00:00",
    "end_time": "2024-10-14T10:00:00"
  }
]
```

---

## Test Cases

- Create Availability: Tests if availability is correctly created for multiple days and time slots.
- Create Availability Invalid Data: Tests if the system returns a 400 Bad Request when required fields are missing.
- Create Availability Invalid Email: Tests if the system returns a 400 Bad Request for an invalid email format.
- Search Available Slots: Verifies that the correct available slots are returned based on the calendar owner's availability.
- Search Partial Available Slots: Checks that partial time slots are correctly handled and only valid slots are returned.
- Search Available Slots No Availability: Tests the scenario where no slots are available on a specific day.
- Double Book Appointment Fail: Ensures that attempting to book an appointment that overlaps an existing one fails with a 400 Bad Request.
- Unavailable Slot Appointment Fail: Tests that booking an appointment in a time slot without availability fails.
- Invalid Slot Appointment Fail: Tests booking an appointment that overlaps partially with an existing appointment fails.
- Valid Slot Appointment Success: Verifies successful appointment booking for an available slot.
- Valid Slot Appointment Multiple Success: Tests successfully booking multiple appointments in valid slots.
- List Appointments: Tests if appointments are correctly listed for a calendar owner.
- List Appointments No Appointments: Verifies the response when no appointments exist for the owner.

---

## Run Tests

To run the tests for this project, use the following command:

```bash
python manage.py test appointments
```
