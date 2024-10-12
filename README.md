# Calendar API Project

This project provides a calendar and appointment booking system using Django and Django Rest Framework (DRF). It allows users to set availability, search for available slots, and book appointments. The application is designed to manage availability on specific days of the week, provide real-time slot searching, and ensure no overlapping appointments. `sqlite` is being used to store the data.

---

## Table of Contents

1. [Project Setup](#project-setup)
2. [Project Components](#project-components)
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
git clone https://github.com/4rr0w/meetings.git
cd meetings
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

- **Availability API** (`/api/availability/setup`): Allows owners to set their availability for specific days and times.
- **Search Available Slots API** (`/api/availability/search`): Allows users to search for available slots for a specific calendar owner on a given date.
- **Book Appointment API** (`/api/appointment/book`): Allows clients to book an appointment with the calendar owner.
- **Appointments API** (`/api/appointments`): Allows calendar owners to list their appointments.

---

## API Usage

You can also use `/swagger` endpoint that will show you existing api's request-response example.

### 1. **Create Availability** (POST `/api/availability/setup`)

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

### 3. **Book Appointment** (POST `/api/appointment/book`)

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

### 4. **List Appointments** (GET `/api/appointments`)

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

- **test_create_availability**: Tests creating availability for a calendar owner.
- **test_create_availability_missing_data**: Tests creating availability with missing owner data.
- **test_create_availability_invalid_mail**: Tests creating availability with an invalid email format.
- **test_search_available_slots**: Tests searching for available time slots.
- **test_search_partial_available_slots**: Tests searching for partially available slots.
- **test_search_past_date_availability**: Tests searching for available slots on a past date, ensuring that the API returns a 400 Bad Request response with an appropriate error message.
- **test_search_available_slots_no_availability**: Tests searching for available slots when no availability exists.
- **test_doublebook_appointment_fail**: Tests booking an overlapping appointment.
- **test_unavailable_slot_appointment_fail**: Tests booking an appointment in an unavailable time slot.
- **test_book_exactly_at_availability_boundary_fail**: Tests booking an appointment at the exact end of an availability window.
- **test_invalid_slot_at_availability_fail**: Tests booking an appointment that partially overlaps with availability.
- **test_valid_slot_appointment_success**: Tests booking an appointment successfully in a valid available slot.
- **test_double_appointment_fail**: Tests booking multiple appointments, only allowing the first to succeed.
- **test_list_appointments**: Tests listing appointments for a calendar owner.
- **test_list_appointments_no_appointments**: Tests listing when no appointments exist.


---

## Run Tests

To run the tests for this project, use the following command:

```bash
python manage.py test appointments
```
