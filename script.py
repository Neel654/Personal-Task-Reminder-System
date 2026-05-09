import flet as ft
from datetime import datetime, timedelta
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import subprocess
from dataclasses import dataclass
import schedule
try:
    from plyer import notification
except ImportError:
    notification = None

@dataclass
class Task:
    id: str
    title: str
    description: str
    reminder_time: datetime
    email: str
    phone: str
    is_completed: bool = False
    is_active: bool = True

class TaskReminderApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Personal Task Reminder System"
        self.page.window.width = 1050
        self.page.window.height = 750
        self.page.theme_mode = ft.ThemeMode.DARK
        
        # Premium Styling
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.TEAL,
            font_family="Roboto",
            use_material3=True
        )
        self.page.padding = 0
        self.page.update()

        # Data
        self.tasks = []
        self.task_counter = 0
        self.data_file = "tasks.json"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_username = ""
        self.email_password = ""

        self.load_email_settings()
        self.load_tasks()

        self.build_ui()

        # Threads
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
        schedule.every(1).minutes.do(self.process_reminders)

    def show_snack(self, message, is_error=False):
        color = ft.colors.ERROR if is_error else ft.colors.TEAL_600
        self.page.snack_bar = ft.SnackBar(ft.Text(message, color=ft.colors.WHITE), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def build_ui(self):
        # Settings Dialog
        self.smtp_server_input = ft.TextField(label="SMTP Server", value=self.smtp_server, expand=True)
        self.smtp_port_input = ft.TextField(label="SMTP Port", value=str(self.smtp_port), expand=True)
        self.email_user_input = ft.TextField(label="Email Username", value=self.email_username)
        self.email_pass_input = ft.TextField(label="App Password", value=self.email_password, password=True, can_reveal_password=True)

        self.settings_status = ft.Text("", size=12)

        def test_email_connection(e):
            self.settings_status.value = "Testing connection..."
            self.settings_status.color = ft.colors.GREY_400
            self.page.update()
            try:
                server = smtplib.SMTP(self.smtp_server_input.value.strip(), int(self.smtp_port_input.value.strip()))
                server.starttls()
                server.login(self.email_user_input.value.strip(), self.email_pass_input.value.strip())
                server.quit()
                self.settings_status.value = "✅ Connection successful!"
                self.settings_status.color = ft.colors.GREEN_400
            except Exception as ex:
                self.settings_status.value = f"❌ Failed: {ex}"
                self.settings_status.color = ft.colors.ERROR
            self.page.update()

        self.settings_dlg = ft.AlertDialog(
            title=ft.Text("⚙️ Email & Notification Settings"),
            content=ft.Column([
                ft.Text("SMTP Configuration", weight=ft.FontWeight.BOLD),
                ft.Row([self.smtp_server_input, self.smtp_port_input]),
                self.email_user_input,
                self.email_pass_input,
                ft.Container(
                    content=ft.Text(
                        "💡 For Gmail: Enable 2FA, then create an App Password at\n"
                        "   myaccount.google.com → Security → App Passwords.\n"
                        "   Use that App Password here, NOT your regular password.",
                        color=ft.colors.BLUE_200, size=12
                    ),
                    padding=ft.padding.symmetric(vertical=8)
                ),
                ft.Divider(),
                ft.Text("📱 SMS / Phone Notifications", weight=ft.FontWeight.BOLD),
                ft.Text(
                    "SMS requires a Twilio account (twilio.com).\n"
                    "Currently, phone number is saved with the task but SMS is not sent automatically.\n"
                    "You can add your Twilio credentials here in the future.",
                    color=ft.colors.ORANGE_300, size=12
                ),
                ft.Divider(),
                self.settings_status,
                ft.ElevatedButton("🔌 Test Email Connection", on_click=test_email_connection,
                                  style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)),
            ], tight=True, width=450, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_settings()),
                ft.ElevatedButton("Save", on_click=self.save_settings_click,
                                  style=ft.ButtonStyle(bgcolor=ft.colors.TEAL_600, color=ft.colors.WHITE)),
            ]
        )

        # Input fields for new task
        now = datetime.now()
        self.title_input = ft.TextField(label="Task Title", prefix_icon=ft.icons.TITLE)
        self.desc_input = ft.TextField(label="Description", multiline=True, min_lines=2, max_lines=4)
        self.date_input = ft.TextField(label="Date", hint_text="YYYY-MM-DD", value=now.strftime("%Y-%m-%d"), expand=1, prefix_icon=ft.icons.CALENDAR_MONTH)
        self.time_input = ft.TextField(label="Time", hint_text="HH:MM", value=(now + timedelta(hours=1)).strftime("%H:%M"), expand=1, prefix_icon=ft.icons.ACCESS_TIME)
        self.email_input = ft.TextField(label="Email", hint_text="user@example.com", expand=1, prefix_icon=ft.icons.EMAIL)
        self.phone_input = ft.TextField(label="Phone", hint_text="Optional", expand=1, prefix_icon=ft.icons.PHONE)

        input_container = ft.Container(
            content=ft.Column([
                ft.Text("Create New Task", size=22, weight=ft.FontWeight.W_600),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                self.title_input,
                self.desc_input,
                ft.Row([self.date_input, self.time_input], spacing=15),
                ft.Row([self.email_input, self.phone_input], spacing=15),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Row([
                    ft.ElevatedButton("Add Task", icon=ft.icons.ADD_TASK, on_click=self.add_task, 
                                      style=ft.ButtonStyle(bgcolor=ft.colors.TEAL_700, color=ft.colors.WHITE)),
                ], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=25,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=16,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.with_opacity(0.1, ft.colors.BLACK)),
        )

        # Tasks list container
        self.tasks_view = ft.ListView(expand=True, spacing=15)

        # Main Layout Structure
        left_pane = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, size=35, color=ft.colors.TEAL_400),
                        ft.Text("Task Master", size=26, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.IconButton(ft.icons.SETTINGS, tooltip="Settings", on_click=self.open_settings)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=30, color=ft.colors.TRANSPARENT),
                input_container
            ]),
            width=400,
            padding=30,
            bgcolor=ft.colors.SURFACE,
        )

        right_pane = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Your Tasks", size=26, weight=ft.FontWeight.W_600),
                    ft.IconButton(ft.icons.REFRESH, tooltip="Refresh", on_click=lambda e: self.refresh_tasks())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.tasks_view
            ]),
            expand=True,
            padding=30,
            bgcolor=ft.colors.BACKGROUND
        )

        self.page.add(
            ft.Row([
                left_pane,
                ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                right_pane
            ], expand=True, spacing=0)
        )
        self.refresh_tasks()

    def open_settings(self, e):
        if self.settings_dlg not in self.page.overlay:
            self.page.overlay.append(self.settings_dlg)
        self.settings_dlg.open = True
        self.page.update()

    def close_settings(self):
        self.settings_dlg.open = False
        self.page.update()

    def save_settings_click(self, e):
        self.smtp_server = self.smtp_server_input.value.strip()
        port_text = self.smtp_port_input.value.strip()
        self.smtp_port = int(port_text) if port_text.isdigit() else 587
        self.email_username = self.email_user_input.value.strip()
        self.email_password = self.email_pass_input.value.strip()
        self.save_email_settings()
        self.close_settings()
        self.show_snack("Email settings saved!")

    def add_task(self, e):
        title = self.title_input.value.strip()
        desc = self.desc_input.value.strip()
        date_str = self.date_input.value.strip()
        time_str = self.time_input.value.strip()
        email = self.email_input.value.strip()
        phone = self.phone_input.value.strip()

        if not title:
            self.show_snack("Task title is required", is_error=True)
            return
        if not date_str or not time_str:
            self.show_snack("Date and time are required", is_error=True)
            return

        try:
            reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if reminder_datetime <= datetime.now():
                self.show_snack("Reminder time must be in the future", is_error=True)
                return

            task = Task(
                id=str(self.task_counter),
                title=title,
                description=desc,
                reminder_time=reminder_datetime,
                email=email,
                phone=phone
            )
            self.tasks.append(task)
            self.task_counter += 1

            self.title_input.value = ""
            self.desc_input.value = ""
            self.page.update()

            self.save_tasks()
            self.refresh_tasks()
            self.show_snack("Task added successfully!")

        except ValueError:
            self.show_snack("Invalid date/time format. Use YYYY-MM-DD and HH:MM", is_error=True)

    def complete_task(self, task):
        task.is_completed = True
        task.is_active = False
        self.save_tasks()
        self.refresh_tasks()
        self.show_snack(f"Task '{task.title}' completed!")

    def delete_task(self, task):
        self.tasks = [t for t in self.tasks if t.id != task.id]
        self.save_tasks()
        self.refresh_tasks()
        self.show_snack(f"Task '{task.title}' deleted!")

    def refresh_tasks(self):
        self.tasks_view.controls.clear()
        active_tasks = sorted([t for t in self.tasks if t.is_active], key=lambda x: x.reminder_time)
        
        if not active_tasks:
            self.tasks_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CELEBRATION, size=50, color=ft.colors.TEAL_200),
                        ft.Text("No active tasks. You're all caught up!", size=18, color=ft.colors.GREY_400)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=100
                )
            )

        for task in active_tasks:
            time_left = task.reminder_time - datetime.now()
            is_overdue = time_left.total_seconds() < 0
            
            if is_overdue:
                time_str = "Overdue!"
                color_time = ft.colors.ERROR
            else:
                days, seconds = time_left.days, time_left.seconds
                hours = seconds // 3600
                mins = (seconds % 3600) // 60
                if days > 0:
                    time_str = f"Due in {days}d {hours}h"
                elif hours > 0:
                    time_str = f"Due in {hours}h {mins}m"
                else:
                    time_str = f"Due in {mins}m"
                color_time = ft.colors.TEAL_300

            card = ft.Card(
                elevation=2,
                surface_tint_color=ft.colors.SURFACE_VARIANT,
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(task.title, size=20, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Container(
                                content=ft.Text(time_str, color=ft.colors.WHITE, weight=ft.FontWeight.W_600, size=13),
                                bgcolor=ft.colors.with_opacity(0.8, color_time),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=20
                            )
                        ]),
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        ft.Text(task.description, color=ft.colors.ON_SURFACE_VARIANT, size=15),
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        ft.Row([
                            ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color=ft.colors.GREY_500),
                            ft.Text(task.reminder_time.strftime("%Y-%m-%d %H:%M"), size=14, color=ft.colors.GREY_500),
                            ft.Container(expand=True),
                            ft.IconButton(ft.icons.CHECK_CIRCLE_OUTLINE, icon_color=ft.colors.GREEN_400, tooltip="Complete", on_click=lambda e, t=task: self.complete_task(t)),
                            ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.ERROR, tooltip="Delete", on_click=lambda e, t=task: self.delete_task(t))
                        ], alignment=ft.MainAxisAlignment.START)
                    ])
                )
            )
            self.tasks_view.controls.append(card)
        self.page.update()

    def check_reminders(self):
        while True:
            schedule.run_pending()
            time.sleep(10) # check more frequently than 60s

    def process_reminders(self):
        current_time = datetime.now()
        updated = False
        for task in self.tasks:
            if task.is_active and not task.is_completed and task.reminder_time <= current_time:
                self.send_notification(task)
                task.is_completed = True
                task.is_active = False
                updated = True
        
        if updated:
            self.save_tasks()
            try:
                self.page.window.to_front()
            except:
                pass
            self.refresh_tasks()

    def send_notification(self, task):
        # Play macOS system sound (no extra library needed)
        try:
            subprocess.Popen(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Could not play sound: {e}")

        # Native OS Notification
        if notification:
            try:
                notification.notify(
                    title=f"⏰ Task Reminder: {task.title}",
                    message=task.description or "Your task is due!",
                    app_name="Task Master",
                    timeout=10
                )
            except Exception as e:
                print(f"Failed to send OS notification: {e}")

        # In-App dialog notification
        def close_alert(e):
            alert.open = False
            self.page.update()

        alert = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=ft.colors.TEAL), ft.Text(" Reminder!")]),
            content=ft.Column([
                ft.Text(task.title, weight=ft.FontWeight.BOLD, size=20),
                ft.Text(task.description)
            ], tight=True),
            actions=[ft.ElevatedButton("Got it", on_click=close_alert)]
        )
        self.page.overlay.append(alert)
        alert.open = True
        self.page.update()

        if task.email and self.email_username and self.email_password:
            threading.Thread(target=self.send_email, args=(task,)).start()

    def send_email(self, task):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = task.email
            msg['Subject'] = f"⏰ Task Reminder: {task.title}"
            body = (
                f"Hello!\n\n"
                f"This is a reminder for your task:\n\n"
                f"📌 Title: {task.title}\n"
                f"📝 Description: {task.description}\n"
                f"🕐 Scheduled Time: {task.reminder_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Best regards,\nTask Master — Personal Reminder System"
            )
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.sendmail(self.email_username, task.email, msg.as_string())
            server.quit()
            print(f"✅ Email sent successfully to {task.email}")
            # Show success snack on main thread
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"📧 Email sent to {task.email}!", color=ft.colors.WHITE),
                bgcolor=ft.colors.TEAL_700
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            err = str(e)
            print(f"❌ Failed to send email: {err}")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Email failed: {err}", color=ft.colors.WHITE),
                bgcolor=ft.colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()

    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump([
                    {
                        'id': t.id, 'title': t.title, 'description': t.description,
                        'reminder_time': t.reminder_time.isoformat(),
                        'email': t.email, 'phone': t.phone,
                        'is_completed': t.is_completed, 'is_active': t.is_active
                    } for t in self.tasks
                ], f, indent=2)
        except Exception:
            pass

    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                for d in data:
                    t = Task(
                        id=d['id'], title=d['title'], description=d['description'],
                        reminder_time=datetime.fromisoformat(d['reminder_time']),
                        email=d.get('email', ''), phone=d.get('phone', ''),
                        is_completed=d.get('is_completed', False), is_active=d.get('is_active', True)
                    )
                    self.tasks.append(t)
                if self.tasks:
                    self.task_counter = max(int(t.id) for t in self.tasks) + 1
        except Exception:
            pass

    def save_email_settings(self):
        try:
            with open('email_settings.json', 'w') as f:
                json.dump({
                    'smtp_server': self.smtp_server, 'smtp_port': self.smtp_port,
                    'email_username': self.email_username, 'email_password': self.email_password
                }, f, indent=2)
        except Exception:
            pass

    def load_email_settings(self):
        try:
            if os.path.exists('email_settings.json'):
                with open('email_settings.json', 'r') as f:
                    data = json.load(f)
                self.smtp_server = data.get('smtp_server', 'smtp.gmail.com')
                self.smtp_port = data.get('smtp_port', 587)
                self.email_username = data.get('email_username', '')
                self.email_password = data.get('email_password', '')
        except Exception:
            pass

def main(page: ft.Page):
    TaskReminderApp(page)

if __name__ == "__main__":
    ft.app(target=main)
