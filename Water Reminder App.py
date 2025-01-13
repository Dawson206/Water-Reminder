import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import time
import threading
import os
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Initialize pygame mixer for sound
pygame.mixer.init()

# Initialize global variables
reminder_sound = None
reminders_running = False
countdown_running = False

# Function to load the sound
def load_sound(file_path):
    global reminder_sound
    if os.path.exists(file_path):
        reminder_sound = pygame.mixer.Sound(file_path)
        reminder_sound.set_volume(volume.get() / 100)  # Set initial volume
        messagebox.showinfo("Sound Selected", f"Sound file loaded: {os.path.basename(file_path)}")
    else:
        reminder_sound = None
        messagebox.showerror("Error", "Selected file not found or invalid!")

# Function to show the reminder notification
def show_reminder():
    if reminder_sound:
        reminder_sound.play()

# Function to preview the currently loaded sound
def preview_sound():
    if reminder_sound:
        reminder_sound.play()
        stop_preview_button.config(state="normal")  # Enable stop button
    else:
        messagebox.showerror("Error", "No sound file loaded!")

# Function to stop preview sound
def stop_preview_sound():
    if reminder_sound:
        reminder_sound.stop()
    stop_preview_button.config(state="disabled")  # Disable stop button

# Function to run the reminder loop
def reminder_loop(interval):
    global countdown_running

    while reminders_running:
        countdown_running = True  # Start the countdown
        update_countdown(interval)  # Start countdown
        time.sleep(interval)  # Wait for the specified interval
        if not reminders_running:  # Check if reminders were stopped during sleep
            break
        show_reminder()  # Play sound and show notification

# Start the reminder loop in a separate thread
def start_reminder_thread(interval):
    reminder_thread = threading.Thread(target=reminder_loop, args=(interval,), daemon=True)
    reminder_thread.start()

# Function to restore the main window
def restore_window(icon, item):
    root.deiconify()
    icon.stop()

# Function to quit the app
def quit_app(icon, item):
    root.quit()
    icon.stop()

# Function to create the tray icon
def create_tray_icon():
    # Create an image for the tray icon
    image = Image.new("RGB", (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 128, 255))

    # Create the menu for the tray icon
    menu = Menu(
        MenuItem("Restore", restore_window),
        MenuItem("Quit", quit_app)
    )

    # Create the tray icon
    icon = Icon("water_reminder", image, menu=menu)
    icon.run()

# Function to minimize the app to the system tray
def minimize_to_tray():
    root.withdraw()
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

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

# Function to start the reminders
def start_reminders():
    global reminders_running
    reminders_running = True  # Set reminders to running
    interval_seconds = interval_minutes.get() * 60
    start_reminder_thread(interval_seconds)
    start_button.config(state="disabled")
    interval_entry.config(state="disabled")
    sound_button.config(state="disabled")
    volume_slider.config(state="disabled")
    preview_button.config(state="disabled")
    stop_button.config(state="normal")
    messagebox.showinfo("Water Reminder", f"Reminders set for every {interval_minutes.get()} minutes.")

# Function to stop the reminders
def stop_reminders():
    global reminders_running, countdown_running
    reminders_running = False
    countdown_running = False  # Stop the countdown
    if reminder_sound:  # Stop any currently playing sound
        reminder_sound.stop()
    start_button.config(state="normal")
    interval_entry.config(state="normal")
    sound_button.config(state="normal")
    volume_slider.config(state="normal")
    preview_button.config(state="normal")
    stop_button.config(state="disabled")
    countdown_label.config(text="Next reminder in: --:--")  # Reset countdown
    messagebox.showinfo("Water Reminder", "Reminders have been stopped.")

# Function to update the countdown label
def update_countdown(seconds):
    global countdown_running

    if not countdown_running:  # Stop updating if the countdown is no longer running
        return

    if seconds < 0:  # If countdown ends, reset display
        countdown_label.config(text="Next reminder in: --:--")
        return

    # Calculate minutes and seconds
    mins, secs = divmod(seconds, 60)
    countdown_label.config(text=f"Next reminder in: {mins:02d}:{secs:02d}")
    
    # Schedule the function to run again after 1 second
    root.after(1000, update_countdown, seconds - 1)

# Create the main application window
root = tk.Tk()
root.title("Water Reminder App")
root.geometry("300x550")
root.resizable(True, True)

# Set the background color to light blue
root.configure(bg="#26a4d3")  # Light blue color code

# Interval between reminders (in seconds)
interval_minutes = tk.IntVar(value=30)  # Default 30 minutes

# Create UI elements
volume_label = tk.Label(root, text="Select & Preview Sound", font=("Arial", 12), bg="#ADD8E6")
volume_label.pack(pady=5)

sound_button = tk.Button(root, text="Select Sound", font=("Arial", 12), command=select_sound_file)
sound_button.pack(pady=10)

preview_button = tk.Button(root, text="Preview Sound", font=("Arial", 12), command=preview_sound)
preview_button.pack(pady=10)

stop_preview_button = tk.Button(root, text="Stop Preview Sound", font=("Arial", 12), command=stop_preview_sound)
stop_preview_button.pack(pady=10)
stop_preview_button.config(state="disabled")  # Initially disabled

volume_label = tk.Label(root, text="Set Volume:", font=("Arial", 12), bg="#ADD8E6")
volume_label.pack(pady=5)

volume = tk.IntVar(value=75)  # Default volume level (50%)
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

# Start the Tkinter event loop
root.mainloop()
