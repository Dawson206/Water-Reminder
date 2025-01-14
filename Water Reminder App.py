import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import time
import threading
import os
import queue
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Initialize pygame mixer for sound
pygame.mixer.init()

# Global variables
reminder_sound = None
reminders_running = False
ui_queue = queue.Queue()

# Function to load the sound
def load_sound(file_path):
    global reminder_sound
    try:
        if os.path.exists(file_path):
            reminder_sound = pygame.mixer.Sound(file_path)
            reminder_sound.set_volume(volume.get() / 100)  # Set initial volume
            messagebox.showinfo("Sound Selected", f"Sound file loaded: {os.path.basename(file_path)}")
        else:
            raise FileNotFoundError("File not found.")
    except Exception as e:
        reminder_sound = None
        messagebox.showerror("Error", f"Could not load sound: {str(e)}")

# Function to show the reminder notification
def show_reminder():
    if reminder_sound:
        reminder_sound.play()
    else:
        messagebox.showwarning("Reminder", "It's time to drink water!")

# Function to preview the currently loaded sound
def preview_sound():
    if reminder_sound:
        reminder_sound.play()
        stop_preview_button.config(state="normal")  # Enable the stop button
    else:
        messagebox.showerror("Error", "No sound file loaded!")

# Function to stop preview sound
def stop_preview_sound():
    if reminder_sound:
        reminder_sound.stop()
    stop_preview_button.config(state="disabled")  # Disable stop button

# Function to update the countdown label
def update_countdown(seconds):
    if seconds < 0 or not reminders_running:
        countdown_label.config(text="Next reminder in: --:--")
        return

    mins, secs = divmod(seconds, 60)
    countdown_label.config(text=f"Next reminder in: {mins:02d}:{secs:02d}")
    root.after(1000, update_countdown, seconds - 1)

# Function to process the UI queue
def process_ui_queue():
    while not ui_queue.empty():
        event, data = ui_queue.get()
        if event == "update_countdown":
            update_countdown(data)
        elif event == "show_reminder":
            show_reminder()
        elif event == "restore":
            root.deiconify()
    root.after(100, process_ui_queue)  # Check the queue every 100ms

# Function to run the reminder loop
def reminder_loop(interval):
    global reminders_running
    while reminders_running:
        ui_queue.put(("update_countdown", interval))
        for remaining in range(interval, 0, -1):
            if not reminders_running:
                return
            time.sleep(1)
        ui_queue.put(("show_reminder", None))

# Function to start the reminders
def start_reminders():
    global reminders_running
    reminders_running = True
    interval_seconds = interval_minutes.get() * 60
    threading.Thread(target=reminder_loop, args=(interval_seconds,), daemon=True).start()
    start_button.config(state="disabled")
    interval_entry.config(state="disabled")
    sound_button.config(state="disabled")
    volume_slider.config(state="disabled")
    preview_button.config(state="disabled")
    stop_preview_button.config(state="disabled")
    stop_button.config(state="normal")
    messagebox.showinfo("Water Reminder", f"Reminders set for every {interval_minutes.get()} minutes.")

# Function to stop the reminders
def stop_reminders():
    global reminders_running
    reminders_running = False
    start_button.config(state="normal")
    interval_entry.config(state="normal")
    sound_button.config(state="normal")
    volume_slider.config(state="normal")
    preview_button.config(state="normal")
    stop_preview_button.config(state="disabled")
    stop_button.config(state="disabled")
    countdown_label.config(text="Next reminder in: --:--")
    messagebox.showinfo("Water Reminder", "Reminders have been stopped.")

# Function to minimize the app to the system tray
def minimize_to_tray():
    root.withdraw()
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

# Function to restore the main window
def restore_window(icon, item):
    ui_queue.put(("restore", None))
    icon.stop()

# Function to quit the app
def quit_app(icon, item):
    global reminders_running
    reminders_running = False
    root.quit()
    icon.stop()

# Function to create the tray icon
def create_tray_icon():
    image = Image.new("RGB", (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 128, 255))

    menu = Menu(
        MenuItem("Restore", restore_window),
        MenuItem("Quit", quit_app)
    )

    icon = Icon("water_reminder", image, menu=menu)
    icon.run()

# Function to select a sound file
def select_sound_file():
    file_path = filedialog.askopenfilename(
        title="Select Sound File",
        filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")]
    )
    if file_path:
        load_sound(file_path)

# Function to update the volume
def update_volume(value):
    if reminder_sound:
        reminder_sound.set_volume(int(value) / 100)

# Create the main application window
root = tk.Tk()
root.title("Dawson's Water Reminder")
root.geometry("400x550")
root.resizable(True, True)

# Set the background color to light blue
root.configure(bg="#26a4d3")

# Interval between reminders (in minutes)
interval_minutes = tk.IntVar(value=30)  # Default 30 minutes

# Create UI elements
volume_label = tk.Label(root, text="Select & Preview Sound", font=("Arial", 12), bg="#ADD8E6")
volume_label.pack(pady=5)

sound_button = tk.Button(root, text="Select Sound", font=("Arial", 12), command=select_sound_file)
sound_button.pack(pady=10)

preview_button = tk.Button(root, text="Preview Sound", font=("Arial", 12), command=preview_sound)
preview_button.pack(pady=10)

stop_preview_button = tk.Button(root, text="Stop Preview Sound", font=("Arial", 12), command=stop_preview_sound, state="disabled")
stop_preview_button.pack(pady=10)

volume_label = tk.Label(root, text="Set Volume:", font=("Arial", 12), bg="#ADD8E6")
volume_label.pack(pady=5)

volume = tk.IntVar(value=75)  # Default volume level (75%)
volume_slider = tk.Scale(
    root,
    from_=0,
    to=100,
    orient="horizontal",
    variable=volume,
    command=update_volume,
    font=("Arial", 10),
    length=200,
    bg="#ADD8E6"
)
volume_slider.pack()

label = tk.Label(root, text="Set Reminder Interval (minutes):", font=("Arial", 12), bg="#ADD8E6")
label.pack(pady=10)

interval_entry = tk.Entry(root, textvariable=interval_minutes, font=("Arial", 12), width=5)
interval_entry.pack()

start_button = tk.Button(root, text="Start Reminders", font=("Arial", 12), command=start_reminders)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Reminders", font=("Arial", 12), command=stop_reminders, state="disabled")
stop_button.pack(pady=10)

countdown_label = tk.Label(root, text="Next reminder in: --:--", font=("Arial", 12), bg="#ADD8E6")
countdown_label.pack(pady=10)

minimize_button = tk.Button(root, text="Minimize to Tray", font=("Arial", 12), command=minimize_to_tray)
minimize_button.pack(pady=10)

# Start the queue processing loop
process_ui_queue()

# Start the Tkinter event loop
root.mainloop()
