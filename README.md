# Personal Task Reminder System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-yellowgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)

A full-featured Python desktop application to schedule and manage personal tasks with automated email reminders, a sleek Tkinter GUI, and persistent local storage. Built to boost productivity and never miss a deadline.

## 📑 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Usage Examples](#-usage-examples)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

✅ **Task Scheduling** — Add tasks with custom title, description, date & time, email, and phone number.
📧 **Automated Email Notifications** — Sends reminders via email using Gmail SMTP (customizable).
🖥️ **Desktop Popup Alerts** — On-screen popups notify you when a task is due.
💾 **Data Persistence** — Tasks and email settings are saved using JSON.
🔁 **Multithreaded Scheduler** — Reminders are processed in the background using schedule + threading.
🧩 **Custom Email Config** — Configure SMTP credentials via settings panel.
📱 **SMS Placeholder** — SMS functionality scaffolded for integration with services like Twilio.
📊 **Live Task Tracker** — View and manage tasks in a sortable table with completion status.

## 🛠️ Tech Stack

| Component | Tool/Library |
|-----------|--------------|
| GUI | tkinter, ttk, scrolledtext |
| Scheduling | schedule, threading |
| Notifications | smtplib, email.mime, tkinter.messagebox |
| Persistence | json, local storage |
| Data Structures | Python dataclass for Task objects |
| Other | datetime, os, typing |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Neel654/Personal-Task-Reminder-System.git
   cd Personal-Task-Reminder-System
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Add a Task:**
   - Click the "Add Task" button
   - Fill in task details (title, description, date, time)
   - Enter email for notifications (optional)
   - Click "Save"

3. **Configure Email Settings:**
   - Go to Settings → Email Configuration
   - Enter your Gmail email and app-specific password
   - Save settings

4. **Monitor Tasks:**
   - View all tasks in the main table
   - Mark tasks as complete
   - Delete tasks as needed

## ⚙️ Configuration

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Visit [Google Account Security](https://myaccount.google.com/security)
   - Generate an app-specific password
3. In the application settings:
   - Email: your-email@gmail.com
   - Password: your-app-specific-password

### Reminder Intervals

Edit `config.json` or use the settings panel to adjust:
- Check interval for due tasks
- Email reminder timing
- Desktop popup duration

## 📁 Project Structure

```
Personal-Task-Reminder-System/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.json               # Configuration settings
├── tasks.json                # Persistent task storage
├── src/
│   ├── gui/
│   │   ├── main_window.py    # Main application window
│   │   ├── task_form.py      # Task creation/edit form
│   │   └── settings_panel.py # Settings configuration
│   ├── scheduler/
│   │   └── reminder.py       # Reminder scheduling logic
│   ├── notifications/
│   │   ├── email.py          # Email notification handler
│   │   └── popup.py          # Desktop popup alerts
│   └── utils/
│       ├── task.py           # Task dataclass definition
│       └── storage.py        # JSON persistence layer
└── README.md                 # This file
```

## 💡 Usage Examples

### Adding a Task Programmatically

```python
from src.utils.task import Task
from src.utils.storage import TaskStorage
from datetime import datetime, timedelta

# Create a new task
new_task = Task(
    title="Project Deadline",
    description="Complete the quarterly report",
    due_date=datetime.now() + timedelta(days=2),
    email="your-email@gmail.com",
    phone="+1234567890"
)

# Save to storage
storage = TaskStorage()
storage.add_task(new_task)
```

### Configuring Email Notifications

```python
from src.notifications.email import EmailNotifier

notifier = EmailNotifier(
    sender_email="your-email@gmail.com",
    sender_password="your-app-password"
)

notifier.send_reminder(task)
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ by [Neel654](https://github.com/Neel654)**