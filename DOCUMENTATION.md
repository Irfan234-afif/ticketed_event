# Ticketed Event Technical Documentation

This document provides a detailed technical overview of the **Ticketed Event** application, covering the data model, backend logic, and frontend architecture.

---

## 🏗 Data Model

The application is built around four primary DocTypes:

### 1. Event User (New)

Handles guest information for passwordless authentication.

- **Fields**: `email` (Data, Unique), `full_name`, `phone`.
- **Naming**: By field `email`.

### 2. Ticketed Event

The header object that defines the event details.

- **Fields**: `title`, `description`, `start_date`, `end_date`, `status` (Draft, Published, Completed), `image`.

### 3. Event Schedule

Defines specific time slots for an event day.

- **Fields**:
  - `event` (Link to Ticketed Event)
  - `date` (Specific date of the slot)
  - `start_time`, `end_time`
  - `max_capacity` (Total slots available)
  - `enrolled_count` (Read-only, calculated on submission of Registration)
- **Naming**: Standard Series `SCH-.YYYY.-.MM.-.####` (e.g., `SCH-2024-05-0001`).

### 4. Event Registration (Submittable)

The core registration document connecting a user to a schedule.

- **Fields**:
  - `user` (Link to **Event User**),
  - `event` (Link to Ticketed Event),
  - `schedule` (Link to Event Schedule),
  - `status` (Draft, Submitted, Cancelled).
- **Naming**: Standard Series `REG-.YYYY.-.MM.-.####` (e.g., `REG-2024-05-0001`).
- **Submittable**: Uses DocStatus (0=Draft, 1=Submitted, 2=Cancelled).
- **Constraints**:
  - A user can only have **one** submitted registration for a specific schedule.
  - A registration can have a maximum of **3** associated participants.

### 5. Event Participant (Standalone)

Stores details for individual attendees. Linked directly to a registration.

- **Fields**:
  - `registration` (Link to **Event Registration**),
  - `full_name`, `email`, `phone`, `instagram`,
  - `qr_code_id` (Unique UUID),
  - `checked_in` (Check), `check_in_time` (Datetime).
- **Naming**: Standard Series `PART-.YYYY.-.MM.-.####` (e.g., `PART-2024-05-0001`).
- **Logic**: `qr_code_id` is generated automatically on the first save (`before_insert`).

---

## 🧠 Backend Logic

Implemented in `event_registration.py`:

- **Participant Limit**: Validates that the number of `Event Participant` docs linked to the registration does not exceed 3.
- **Capacity Validation**: On save/submit, checks if `Event Schedule` has remaining capacity (`max_capacity` vs `enrolled_count`).
- **Uniqueness**: Ensures an `Event User` cannot register twice for the same `Event Schedule`.
- **Count Management**:
  - `on_submit`: Increments `Event Schedule.enrolled_count`.
  - `on_cancel`: Decrements `Event Schedule.enrolled_count`.

---

## 🔌 API Reference

### Check-in API

**Method**: `ticketed_event.ticketed_event.doctype.event_registration.event_registration.check_in_participant`

- **Whitelisted**: Yes (accessible via API)
- **Parameters**: `qr_code_id` (string)
- **Logic**:
  1. Finds the `Event Participant` using the unique `qr_code_id`.
  2. Verifies the linked `Event Registration` is in _Submitted_ status.
  3. Validates that the participant hasn't already checked in.
  4. Updates `checked_in` to `1` and sets `check_in_time`.
  5. Returns success status with participant and event details.

---

## 🎨 Frontend Architecture

The frontend is located in the `frontend/` directory of the app and uses a modern stack:

- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Frappe UI
- **Integration**:
  - Proxies API calls to the Frappe backend.
  - Uses `window.csrf_token` for authenticated requests.
  - Build output is served via Frappe's `public/assets` and a custom WWW page (`_ticketed_event.html`).

---

## 🧪 Testing

Unit tests are provided to ensure core logic reliability:

- **Location**: `.../doctype/event_registration/test_event_registration.py`
- **Test Cases**:
  - `test_participant_limit`: Ensures the 3-participant rule (counting linked docs).
  - `test_capacity_limit`: Ensures no overbooking.
  - `test_unique_schedule_per_user`: Ensures single registration per schedule constraint.
  - `test_check_in_flow`: Verifies the end-to-end check-in API with the new standalone structure.
