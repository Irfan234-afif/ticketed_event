### Ticketed Event App

A simple yet powerful event registration system built on **Frappe Framework**. This application allows users to register for multi-day events, select specific time slots, and manage up to 3 participants per registration. Each participant receives a unique QR code for seamless event day check-ins.

#### 🚀 Key Features

- **Multi-Day Event Support**: Organize events over multiple dates (e.g., 3-day events).
- **Time Slots & Capacity**: Manage per-day schedules with specific time slots and maximum participant limits.
- **Participant Management**: Each registration supports up to 3 participants with individual details (Name, Email, Phone, IG).
- **Unique QR Codes**: Automatically generates unique UUIDs for each participant to be used for QR code generation.
- **Check-in System**: A dedicated API for administrators to validate and mark participant attendance.
- **Modern Frontend**: Built with **Vue 3**, **Vite**, **Tailwind CSS**, and **Frappe UI** for a premium user experience.

#### 🛠 Technical Flow

1.  **Selection**: User selects an Event Date and a specific Time Schedule.
2.  **Validation**: Backend checks for available slots and ensures the user hasn't exceeded the 3-participant limit.
3.  **Submission**: On submission, unique `qr_code_id`s are generated, and `enrolled_count` is updated for the schedule.
4.  **Check-in**: Admins use the `check_in_participant` whitelist method to scan and verify QR codes.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app ticketed_event
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/ticketed_event
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
