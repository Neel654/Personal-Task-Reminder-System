# ⏰ Personal Task Reminder System - Desktop Productivity & Notification Platform

A full-featured Python desktop productivity application for scheduling, tracking, and managing personal tasks with automated email reminders, popup notifications, multithreaded scheduling, and persistent local storage.

[![Python](https://img.shields.io/badge/Python-Desktop%20Application-blue?style=for-the-badge&logo=python)](https://www.python.org/) [![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)]() [![Notifications](https://img.shields.io/badge/System-Email%20Reminders-orange?style=for-the-badge)]() [![Storage](https://img.shields.io/badge/Persistence-JSON-red?style=for-the-badge)]()

---

## 🎯 Project Overview

Personal Task Reminder System is a Python-based desktop application designed to help users manage tasks, deadlines, and reminders through an interactive GUI and automated notification workflows.

The system combines:
- Task scheduling
- Email notifications
- Popup alerts
- Persistent local storage
- Background scheduling processes
- Configurable reminder settings

The application is built with a modular architecture using Python, Tkinter, JSON persistence, and multithreaded scheduling to create a lightweight productivity management platform.

---

## ✨ Key Capabilities

- ✅ **Task scheduling system** with title, description, date, and reminder configuration
- ✅ **Automated email reminders** using Gmail SMTP integration
- ✅ **Desktop popup notifications** for real-time task alerts
- ✅ **Persistent task storage** using JSON-based local persistence
- ✅ **Multithreaded background scheduler** for continuous reminder processing
- ✅ **Custom email configuration panel** for SMTP credentials
- ✅ **Live task management interface** with tracking and completion status
- ✅ **Extensible notification architecture** with SMS integration scaffolding

---

## 🏗️ Architecture

```text
┌────────────────────────┐
│      Desktop User      │
│   Tkinter GUI System   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│    GUI Application     │
│------------------------│
│ • Main Window          │
│ • Task Forms           │
│ • Settings Panel       │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│   Task Management      │
│ & Scheduling Engine    │
└────────────┬───────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌──────────────┐ ┌────────────────┐
│ Notifications│ │ JSON Storage   │
│--------------│ │ Persistence    │
│ • Email SMTP │ │ Tasks & Config │
│ • Popup UI   │ └────────────────┘
└──────────────┘
```

The application separates the GUI, scheduling engine, notifications, and persistence layers into modular components for maintainability and scalability.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Language** | Python |
| **GUI Framework** | Tkinter |
| **Scheduling** | schedule + threading |
| **Notifications** | smtplib + email.mime |
| **Persistence** | JSON local storage |
| **Data Modeling** | Python dataclasses |
| **Utilities** | datetime, typing, os |

---

## 📁 Project Structure

```text
Personal-Task-Reminder-System/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config.json                # Configuration settings
├── tasks.json                 # Persistent task storage
├── src/
│   ├── gui/
│   │   ├── main_window.py     # Main desktop interface
│   │   ├── task_form.py       # Task creation and editing
│   │   └── settings_panel.py  # Settings configuration UI
│   ├── scheduler/
│   │   └── reminder.py        # Reminder scheduling engine
│   ├── notifications/
│   │   ├── email.py           # Email notification system
│   │   └── popup.py           # Desktop popup alerts
│   └── utils/
│       ├── task.py            # Task dataclass model
│       └── storage.py         # JSON persistence layer
└── README.md                  # Project documentation
```

### Core System Areas

- **GUI Layer** — Desktop interface and user interaction
- **Scheduler Engine** — Background task reminder processing
- **Notification Layer** — Email and popup alerts
- **Persistence Layer** — JSON-based storage management
- **Task Models** — Structured task representation using dataclasses

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/Neel654/Personal-Task-Reminder-System.git
cd Personal-Task-Reminder-System
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the environment**

#### Windows
```bash
venv\Scripts\activate
```

#### macOS/Linux
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python main.py
```

---

## ⚙️ Configuration

### Gmail SMTP Setup

1. Enable 2-Factor Authentication for your Gmail account
2. Generate a Gmail App Password
3. Configure credentials inside the application settings panel

### Adjustable Settings

The application supports configurable:
- Reminder intervals
- Email settings
- Popup timing
- Task refresh intervals
- Notification preferences

---

## 🔄 System Workflow

### Task Lifecycle

1. User creates a task through the Tkinter GUI
2. Task data is saved to JSON persistence storage
3. Background scheduler continuously monitors due times
4. Email reminders and popup alerts are triggered automatically
5. Task status updates are reflected in the live task tracker

---

## 💡 Example Usage

### Create a Task Programmatically

```python
from src.utils.task import Task
from datetime import datetime

task = Task(
    title="Complete Assignment",
    description="Finish backend systems project",
    due_date=datetime.now(),
    email="example@gmail.com"
)
```

### Send an Email Reminder

```python
from src.notifications.email import EmailNotifier

notifier.send_reminder(task)
```

---

## 📌 Project Highlights

### Productivity Features
- Interactive task management
- Reminder automation
- Real-time desktop alerts
- Persistent storage workflows

### Software Engineering Focus
- Modular Python architecture
- Background scheduling systems
- GUI application development
- Structured notification pipelines

### Scalability & Extensibility
- Modular notification layer
- JSON-based configurable persistence
- SMS integration scaffolding
- Expandable scheduler workflows

---

## 💡 Why This Project Stands Out

Unlike a simple to-do list application, this project combines:
- Desktop GUI engineering
- Background scheduling systems
- Notification automation
- Persistent data management
- Modular software architecture

The repository demonstrates practical experience building a real multi-component desktop productivity application rather than a basic script-based utility.

---

## 🧠 Learning Outcomes

This project demonstrates practical experience with:
- Python desktop application development
- Tkinter GUI engineering
- Background threading and scheduling
- Email automation with SMTP
- JSON persistence workflows
- Modular software architecture
- Notification system design

---

## 🚀 Future Improvements

Potential future enhancements:
- Cloud synchronization support
- SQLite or PostgreSQL persistence
- Push/mobile notifications
- Calendar integrations
- Recurring task automation
- User authentication system
- Dark mode UI themes

---

## 📄 Resume-Ready Description

- Built a Python desktop productivity platform with Tkinter GUI, multithreaded scheduling, automated email reminders, popup notifications, and JSON-based persistent task management.

---

## 👤 Author

**Neel Prajapati**  
Computer Science Student @ Toronto Metropolitan University

---

⭐ Feel free to explore the repository, contribute improvements, or fork the project!
