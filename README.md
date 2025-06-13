# Personal-Task-Reminder-System
A full-featured Python desktop application to schedule and manage personal tasks with automated email reminders, a sleek Tkinter GUI, and persistent local storage. Built to boost productivity and never miss a deadline.

📌 Key Features
✅ Task Scheduling — Add tasks with custom title, description, date & time, email, and phone number.
📧 Automated Email Notifications — Sends reminders via email using Gmail SMTP (customizable).
🖥️ Desktop Popup Alerts — On-screen popups notify you when a task is due.
💾 Data Persistence — Tasks and email settings are saved using JSON.
🔁 Multithreaded Scheduler — Reminders are processed in the background using schedule + threading.
🧩 Custom Email Config — Configure SMTP credentials via settings panel.
📱 SMS Placeholder — SMS functionality scaffolded for integration with services like Twilio.
📊 Live Task Tracker — View and manage tasks in a sortable table with completion status.

🛠️ Tech Stack
Component	Tool/Library
GUI	tkinter, ttk, scrolledtext
Scheduling	schedule, threading
Notifications	smtplib, email.mime, tkinter.messagebox
Persistence	json, local storage
Data Structures	Python dataclass for Task objects
Other	datetime, os, typing
