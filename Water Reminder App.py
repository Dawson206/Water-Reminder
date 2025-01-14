import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import time
import threading
import os
import queue
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Initialize pygame mixer for soundimport customtkinter as ctk
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
        stop_preview_button.configure(state="normal")  # Enable the stop button
    else:
        messagebox.showerror("Error", "No sound file loaded!")

# Function to stop preview sound
def stop_preview_sound():
    if reminder_sound:
        reminder_sound.stop()
    stop_preview_button.configure(state="disabled")  # Disable stop button

# Function to update the countdown label
def update_countdown(seconds):
    if seconds < 0 or not reminders_running:
        countdown_label.configure(text="Next reminder in: --:--")
        return

    mins, secs = divmod(seconds, 60)
    countdown_label.configure(text=f"Next reminder in: {mins:02d}:{secs:02d}")
    root.after(1000, update_countdown, seconds - 1)

# Function to process the UI queue
def process_ui_queue():
    while not ui_queue.empty():  # Process events from the queue
        event, data = ui_queue.get()  # Get the event from the queue
        if event == "update_countdown":
            update_countdown(data)  # Update the countdown on the UI
        elif event == "show_reminder":
            show_reminder()  # Show the reminder notification
        elif event == "restore":
            root.deiconify()  # Restore the window if minimized
    root.after(100, process_ui_queue)  # Check the queue every 100ms


# Function to run the reminder loop
def reminder_loop(interval):
    global reminders_running
    while reminders_running:  # Loop until reminders_running is set to False
        ui_queue.put(("update_countdown", interval))  # Update countdown on the UI
        for remaining in range(interval, 0, -1):
            if not reminders_running:  # If reminders_running is False, exit the loop
                return
            time.sleep(1)  # Wait for 1 second
        ui_queue.put(("show_reminder", None))  # Show reminder


# Function to start the reminders
# Function to start the reminders
def start_reminders():
    global reminders_running
    if reminders_running:
        return  # Prevent starting multiple reminder loops
    
    if not reminder_sound:
        response = messagebox.askyesno("No Sound Selected", 
                                       "No sound file has been selected. Would you like to select one now?")
        if response:
            select_sound_file()
            return  # Exit the function if the user wants to select a sound first
    
    reminders_running = True
    interval_seconds = interval_minutes.get() * 60
    reminder_thread = threading.Thread(target=reminder_loop, args=(interval_seconds,), daemon=True)
    reminder_thread.start()
    
    start_button.configure(state="disabled")
    interval_entry.configure(state="disabled")
    sound_button.configure(state="disabled")
    volume_slider.configure(state="disabled")
    preview_button.configure(state="disabled")
    stop_preview_button.configure(state="disabled")
    stop_button.configure(state="normal")

# Function to stop the reminders
def stop_reminders():
    global reminders_running
    reminders_running = False
    
    # Stop the audio if it's playing
    if reminder_sound:
        reminder_sound.stop()

    # Stop any queued audio (if any)
    pygame.mixer.stop()

    # Reset the countdown display
    countdown_label.configure(text="Next reminder in: --:--")

    # Re-enable the controls
    start_button.configure(state="normal")
    interval_entry.configure(state="normal")
    sound_button.configure(state="normal")
    volume_slider.configure(state="normal")
    preview_button.configure(state="normal")
    stop_preview_button.configure(state="disabled")
    stop_button.configure(state="disabled")

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

# Function to dynamically update the width of the entry box
def update_entry_width(*args):
    current_text = str(interval_minutes.get())
    min_width = 35  # Set a base width
    additional_width = len(current_text) * 2  # Add width based on the number of characters entered
    new_width = min_width + additional_width
    interval_entry.configure(width=new_width)

# Create the main application window with CustomTkinter
root = ctk.CTk()
root.title("Dawson's Water Reminder")
root.geometry("400x550")
root.resizable(True, True)

# Set the background color to light blue
root.configure(bg="#A8E6A1")

# Create the custom font using CTkFont
custom_font = ctk.CTkFont(family="Arial", size=12)

# Interval between reminders (in minutes)
interval_minutes = ctk.IntVar(value=30)  # Default 30 minutes

# Create UI elements with CustomTkinter
volume_label = ctk.CTkLabel(root, text="Select & Preview Sound", font=custom_font)
volume_label.pack(pady=5)

sound_button = ctk.CTkButton(root, text="Select Sound", font=custom_font, command=select_sound_file)
sound_button.pack(pady=10)

volume_label = ctk.CTkLabel(root, text="Set Volume:", font=custom_font)
volume_label.pack(pady=5)

volume = ctk.IntVar(value=75)  # Default volume level (75%)
volume_slider = ctk.CTkSlider(
    root,
    from_=0,
    to=100,
    variable=volume,
    command=update_volume,
    width=200
)
volume_slider.pack()

preview_button = ctk.CTkButton(root, text="Preview Sound", font=custom_font, command=preview_sound)
preview_button.pack(pady=10)

stop_preview_button = ctk.CTkButton(root, text="Stop Preview Sound", font=custom_font, command=stop_preview_sound, state="disabled")
stop_preview_button.pack(pady=10)

label = ctk.CTkLabel(root, text="Set Reminder Interval (minutes):", font=custom_font)
label.pack(pady=10)

interval_entry = ctk.CTkEntry(
    root,
    textvariable=interval_minutes,
    font=custom_font,
    width=35,
    justify="center"  # Center the text
)
interval_entry.pack()

# Bind the function to update the width of the entry as text is entered
interval_minutes.trace("w", update_entry_width)

start_button = ctk.CTkButton(root, text="Start Reminders", font=custom_font, command=start_reminders)
start_button.pack(pady=10)

stop_button = ctk.CTkButton(root, text="Stop Reminders", font=custom_font, command=stop_reminders, state="disabled")
stop_button.pack(pady=10)

countdown_label = ctk.CTkLabel(root, text="Next reminder in: --:--", font=custom_font)
countdown_label.pack(pady=10)

minimize_button = ctk.CTkButton(root, text="Minimize to Tray", font=custom_font, command=minimize_to_tray)
minimize_button.pack(pady=10)

# Start the queue processing loop
process_ui_queue()

# Start the CustomTkinter event loop
root.mainloop()

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
