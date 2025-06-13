import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from dataclasses import dataclass
from typing import List, Optional
import schedule

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

class TaskReminderSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Task Reminder System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Task storage
        self.tasks = []
        self.task_counter = 0
        self.data_file = "tasks.json"
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_username = ""
        self.email_password = ""
        
        # Load existing data
        self.load_email_settings()
        self.load_tasks()
        
        # Create GUI
        self.create_widgets()
        
        # Start reminder checker thread
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
        
        # Schedule periodic checks
        schedule.every(1).minutes.do(self.process_reminders)
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Personal Task Reminder System", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Task input section
        input_frame = ttk.LabelFrame(main_frame, text="Add New Task", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Task title
        ttk.Label(input_frame, text="Task Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Task description
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.desc_entry = scrolledtext.ScrolledText(input_frame, width=30, height=3)
        self.desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Date and time
        ttk.Label(input_frame, text="Reminder Date:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        date_frame = ttk.Frame(input_frame)
        date_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.date_entry = ttk.Entry(date_frame, width=12)
        self.date_entry.grid(row=0, column=0, padx=(0, 5))
        ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(input_frame, text="Reminder Time:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        time_frame = ttk.Frame(input_frame)
        time_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.time_entry = ttk.Entry(time_frame, width=12)
        self.time_entry.grid(row=0, column=0, padx=(0, 5))
        ttk.Label(time_frame, text="(HH:MM)").grid(row=0, column=1, sticky=tk.W)
        
        # Contact information
        ttk.Label(input_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.email_entry = ttk.Entry(input_frame, width=30)
        self.email_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        ttk.Label(input_frame, text="Phone:").grid(row=5, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.phone_entry = ttk.Entry(input_frame, width=30)
        self.phone_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Add task button
        add_button = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_button.grid(row=6, column=1, sticky=tk.E, pady=(10, 0))
        
        # Tasks list section
        list_frame = ttk.LabelFrame(main_frame, text="Your Tasks", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Treeview for tasks
        columns = ("Title", "Description", "Reminder Time", "Status")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Complete Task", command=self.complete_task).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_tasks).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Settings", command=self.open_settings).grid(row=0, column=3, padx=(5, 0))
        
        # Set default values
        now = datetime.now()
        self.date_entry.insert(0, now.strftime("%Y-%m-%d"))
        self.time_entry.insert(0, (now + timedelta(hours=1)).strftime("%H:%M"))
        
        # Load and display tasks
        self.refresh_tasks()
        
    def add_task(self):
        try:
            title = self.title_entry.get().strip()
            description = self.desc_entry.get("1.0", tk.END).strip()
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            email = self.email_entry.get().strip()
            phone = self.phone_entry.get().strip()
            
            if not title:
                messagebox.showerror("Error", "Please enter a task title")
                return
                
            if not date_str or not time_str:
                messagebox.showerror("Error", "Please enter both date and time")
                return
            
            # Parse datetime
            reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            if reminder_datetime <= datetime.now():
                messagebox.showerror("Error", "Reminder time must be in the future")
                return
            
            # Create task
            task = Task(
                id=str(self.task_counter),
                title=title,
                description=description,
                reminder_time=reminder_datetime,
                email=email,
                phone=phone
            )
            
            self.tasks.append(task)
            self.task_counter += 1
            
            # Clear entries
            self.title_entry.delete(0, tk.END)
            self.desc_entry.delete("1.0", tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            
            # Save and refresh
            self.save_tasks()
            self.refresh_tasks()
            
            messagebox.showinfo("Success", f"Task '{title}' added successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid date (YYYY-MM-DD) and time (HH:MM)")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def complete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to complete")
            return
        
        item = self.task_tree.item(selected[0])
        task_title = item['values'][0]
        
        for task in self.tasks:
            if task.title == task_title and task.is_active:
                task.is_completed = True
                task.is_active = False
                break
        
        self.save_tasks()
        self.refresh_tasks()
        messagebox.showinfo("Success", f"Task '{task_title}' marked as completed!")
    
    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        item = self.task_tree.item(selected[0])
        task_title = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{task_title}'?"):
            self.tasks = [task for task in self.tasks if not (task.title == task_title and task.is_active)]
            self.save_tasks()
            self.refresh_tasks()
            messagebox.showinfo("Success", f"Task '{task_title}' deleted!")
    
    def refresh_tasks(self):
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add active tasks
        for task in self.tasks:
            if task.is_active:
                status = "Completed" if task.is_completed else "Pending"
                self.task_tree.insert("", tk.END, values=(
                    task.title,
                    task.description[:50] + "..." if len(task.description) > 50 else task.description,
                    task.reminder_time.strftime("%Y-%m-%d %H:%M"),
                    status
                ))
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Email Settings")
        settings_window.geometry("450x400")
        settings_window.configure(bg="#f0f0f0")
        
        # Make window modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Email Configuration", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # SMTP Server
        ttk.Label(frame, text="SMTP Server:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        smtp_entry = ttk.Entry(frame, width=40, font=("Arial", 10))
        smtp_entry.pack(fill=tk.X, pady=(0, 10))
        smtp_entry.insert(0, self.smtp_server)
        
        # SMTP Port
        ttk.Label(frame, text="SMTP Port:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        port_entry = ttk.Entry(frame, width=40, font=("Arial", 10))
        port_entry.pack(fill=tk.X, pady=(0, 10))
        port_entry.insert(0, str(self.smtp_port))
        
        # Email Username
        ttk.Label(frame, text="Email Username:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        username_entry = ttk.Entry(frame, width=40, font=("Arial", 10))
        username_entry.pack(fill=tk.X, pady=(0, 10))
        username_entry.insert(0, self.email_username)
        
        # Email Password
        ttk.Label(frame, text="Email Password (App Password):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        password_entry = ttk.Entry(frame, width=40, show="*", font=("Arial", 10))
        password_entry.pack(fill=tk.X, pady=(0, 15))
        password_entry.insert(0, self.email_password)
        
        # Instructions
        instructions = ttk.Label(frame, text="For Gmail: Use App Password (not regular password)\nSMTP: smtp.gmail.com, Port: 587", 
                               font=("Arial", 9), foreground="blue")
        instructions.pack(pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_settings():
            try:
                self.smtp_server = smtp_entry.get().strip()
                port_text = port_entry.get().strip()
                self.smtp_port = int(port_text) if port_text.isdigit() else 587
                self.email_username = username_entry.get().strip()
                self.email_password = password_entry.get().strip()
                
                # Save to file for persistence
                self.save_email_settings()
                
                messagebox.showinfo("Success", "Email settings saved successfully!")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        
        def test_connection():
            try:
                server = smtplib.SMTP(smtp_entry.get().strip(), int(port_entry.get().strip()))
                server.starttls()
                server.login(username_entry.get().strip(), password_entry.get().strip())
                server.quit()
                messagebox.showinfo("Success", "Email connection test successful!")
            except Exception as e:
                messagebox.showerror("Error", f"Connection test failed: {str(e)}")
        
        # Buttons
        ttk.Button(button_frame, text="Test Connection", command=test_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save Settings", command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT)
    
    def check_reminders(self):
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def process_reminders(self):
        current_time = datetime.now()
        
        for task in self.tasks:
            if (task.is_active and not task.is_completed and 
                task.reminder_time <= current_time):
                
                self.send_notification(task)
                # Mark as completed to avoid repeated notifications
                task.is_completed = True
                self.save_tasks()
    
    def send_notification(self, task):
        # Desktop notification
        messagebox.showinfo("Task Reminder", 
                          f"Reminder: {task.title}\n\n{task.description}")
        
        # Email notification
        if task.email and self.email_username and self.email_password:
            self.send_email(task)
        
        # SMS would require additional services like Twilio
        # For now, we'll just show the phone number in console
        if task.phone:
            print(f"SMS Reminder to {task.phone}: {task.title}")
    
    def send_email(self, task):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = task.email
            msg['Subject'] = f"Task Reminder: {task.title}"
            
            body = f"""
            Hello!
            
            This is a reminder for your task:
            
            Title: {task.title}
            Description: {task.description}
            Scheduled Time: {task.reminder_time.strftime('%Y-%m-%d %H:%M')}
            
            Best regards,
            Personal Task Reminder System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_username, task.email, text)
            server.quit()
            
            print(f"Email sent successfully to {task.email}")
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
    
    def save_tasks(self):
        try:
            tasks_data = []
            for task in self.tasks:
                tasks_data.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'reminder_time': task.reminder_time.isoformat(),
                    'email': task.email,
                    'phone': task.phone,
                    'is_completed': task.is_completed,
                    'is_active': task.is_active
                })
            
            with open(self.data_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving tasks: {str(e)}")
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data:
                    task = Task(
                        id=task_data['id'],
                        title=task_data['title'],
                        description=task_data['description'],
                        reminder_time=datetime.fromisoformat(task_data['reminder_time']),
                        email=task_data['email'],
                        phone=task_data['phone'],
                        is_completed=task_data.get('is_completed', False),
                        is_active=task_data.get('is_active', True)
                    )
                    self.tasks.append(task)
                
                if self.tasks:
                    self.task_counter = max(int(task.id) for task in self.tasks) + 1
                    
        except Exception as e:
            print(f"Error loading tasks: {str(e)}")
    
    def save_email_settings(self):
        """Save email settings to file for persistence"""
        try:
            settings = {
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'email_username': self.email_username,
                'email_password': self.email_password
            }
            
            with open('email_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving email settings: {str(e)}")
    
    def load_email_settings(self):
        """Load email settings from file"""
        try:
            if os.path.exists('email_settings.json'):
                with open('email_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.smtp_server = settings.get('smtp_server', 'smtp.gmail.com')
                self.smtp_port = settings.get('smtp_port', 587)
                self.email_username = settings.get('email_username', '')
                self.email_password = settings.get('email_password', '')
                    
        except Exception as e:
            print(f"Error loading email settings: {str(e)}")
    
    def run(self):
        self.root.mainloop()

def main():
    """
    Personal Task Reminder System
    
    Features:
    - Add tasks with title, description, and reminder time
    - Email notifications (requires email configuration)
    - SMS notifications (placeholder - requires external service)
    - Desktop popup reminders
    - Task completion tracking
    - Data persistence
    
    Setup Instructions:
    1. Run the application
    2. Go to Settings to configure your email SMTP settings
    3. For Gmail, use: smtp.gmail.com, port 587, and an app password
    4. Add tasks with future reminder times
    5. The system will automatically check for due reminders
    
    Note: For SMS functionality, you would need to integrate with services
    like Twilio, which requires API keys and additional setup.
    """
    
    app = TaskReminderSystem()
    app.run()

if __name__ == "__main__":
    main()
