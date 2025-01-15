import customtkinter as ctk
from tkinter import messagebox, filedialog
import pygame
import time
import threading
import os
import queue
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import configparser

config = configparser.ConfigParser()

config_file_path = "config.ini"

pygame.mixer.init()

reminder_sound = None
reminders_running = False
ui_queue = queue.Queue()


def load_settings():
    global reminder_sound
    if os.path.exists(config_file_path):
        config.read(config_file_path)
        if "Settings" in config:
            sound_path = config["Settings"].get("sound_file", "")
            volume_level = config["Settings"].getint("volume", 75)
            if sound_path and os.path.exists(sound_path):
                load_sound(sound_path)
                volume.set(volume_level)
                reminder_sound.set_volume(volume_level / 100)


def save_settings(sound_file_path=None):
    if "Settings" not in config:
        config["Settings"] = {}
    if sound_file_path:
        config["Settings"]["sound_file"] = sound_file_path
    config["Settings"]["volume"] = str(volume.get())
    with open(config_file_path, "w") as config_file:
        config.write(config_file)


def select_sound_file():
    file_path = filedialog.askopenfilename(
        title="Select Sound File",
        filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")]
    )
    if file_path:
        load_sound(file_path)


def update_volume(value):
    if reminder_sound:
        reminder_sound.set_volume(int(value) / 100)


def load_sound(file_path):
    global reminder_sound
    try:
        if os.path.exists(file_path):
            reminder_sound = pygame.mixer.Sound(file_path)
            reminder_sound.set_volume(volume.get() / 100)
            save_settings(file_path)
            messagebox.showinfo("Sound Selected", f"Sound file loaded: {os.path.basename(file_path)}")
    except Exception as e:
        reminder_sound = None
        messagebox.showerror("Error", f"Could not load sound: {str(e)}")


def preview_sound():
    if reminder_sound:
        reminder_sound.play()
        stop_preview_button.configure(state="normal")


def stop_preview_sound():
    if reminder_sound:
        reminder_sound.stop()
    stop_preview_button.configure(state="disabled")


def update_countdown(seconds):
    if seconds < 0 or not reminders_running:
        countdown_label.configure(text="Next reminder in: --:--")
        return

    mins, secs = divmod(seconds, 60)
    countdown_label.configure(text=f"Next reminder in: {mins:02d}:{secs:02d}")
    root.after(1000, update_countdown, seconds - 1)


def process_ui_queue():
    while not ui_queue.empty():
        event, data = ui_queue.get()
        if event == "update_countdown":
            update_countdown(data)
        elif event == "show_reminder":
            show_reminder()
        elif event == "restore":
            root.deiconify()
    root.after(100, process_ui_queue)


def show_reminder():
    if reminder_sound:
        reminder_sound.play()
    else:
        messagebox.showwarning("Reminder", "It's time to drink water!")


def reminder_loop(interval):
    global reminders_running
    while reminders_running:
        ui_queue.put(("update_countdown", interval))
        for remaining in range(interval, 0, -1):
            if not reminders_running:
                return
            time.sleep(1)
        ui_queue.put(("show_reminder", None))


def start_reminders():
    global reminders_running
    if reminders_running:
        return
    if not reminder_sound:
        response = messagebox.askyesno("No Sound Selected", "No sound file has been selected. Would you like to select one now?")
        if response:
            select_sound_file()
            return
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


def stop_reminders():
    global reminders_running
    reminders_running = False
    if reminder_sound:
        reminder_sound.stop()
    pygame.mixer.stop()
    countdown_label.configure(text="Next reminder in: --:--")
    start_button.configure(state="normal")
    interval_entry.configure(state="normal")
    sound_button.configure(state="normal")
    volume_slider.configure(state="normal")
    preview_button.configure(state="normal")
    stop_preview_button.configure(state="disabled")
    stop_button.configure(state="disabled")


def minimize_to_tray():
    root.withdraw()
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()


def restore_window(icon, item):
    ui_queue.put(("restore", None))
    icon.stop()


def quit_app(icon, item):
    global reminders_running
    reminders_running = False
    if reminder_sound:
        reminder_sound.stop()
    pygame.mixer.quit()
    root.quit()
    icon.stop()
    os._exit(0)


def create_tray_icon():
    image = Image.new("RGB", (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 128, 255))
    menu = Menu(MenuItem("Restore", restore_window), MenuItem("Quit", quit_app))
    icon = Icon("water_reminder", image, menu=menu)
    icon.run()


def update_entry_width(*args):
    current_text = str(interval_minutes.get())
    min_width = 35
    additional_width = len(current_text) * 2
    new_width = min_width + additional_width
    interval_entry.configure(width=new_width)

root = ctk.CTk()
root.title("Dawson's Water Reminder")
root.geometry("400x550")
root.resizable(True, True)
root.configure(bg="#A8E6A1")
custom_font = ctk.CTkFont(family="Arial", size=12)
interval_minutes = ctk.IntVar(value=30)
volume_label = ctk.CTkLabel(root, text="Select & Preview Sound", font=custom_font)
volume_label.pack(pady=5)
sound_button = ctk.CTkButton(root, text="Select Sound", font=custom_font, command=select_sound_file)
sound_button.pack(pady=10)
volume_label = ctk.CTkLabel(root, text="Set Volume:", font=custom_font)
volume_label.pack(pady=5)
volume = ctk.IntVar(value=75)
volume_slider = ctk.CTkSlider(root, from_=0, to=100, variable=volume, command=update_volume, width=200)
volume_slider.pack()
preview_button = ctk.CTkButton(root, text="Preview Sound", font=custom_font, command=preview_sound)
preview_button.pack(pady=10)
stop_preview_button = ctk.CTkButton(root, text="Stop Preview Sound", font=custom_font, command=stop_preview_sound, state="disabled")
stop_preview_button.pack(pady=10)
label = ctk.CTkLabel(root, text="Set Reminder Interval (minutes):", font=custom_font)
label.pack(pady=10)
interval_entry = ctk.CTkEntry(root, textvariable=interval_minutes, font=custom_font, width=35, justify="center")
interval_entry.pack()
interval_minutes.trace("w", update_entry_width)
start_button = ctk.CTkButton(root, text="Start Reminders", font=custom_font, command=start_reminders)
start_button.pack(pady=10)
stop_button = ctk.CTkButton(root, text="Stop Reminders", font=custom_font, command=stop_reminders, state="disabled")
stop_button.pack(pady=10)
countdown_label = ctk.CTkLabel(root, text="Next reminder in: --:--", font=custom_font)
countdown_label.pack(pady=10)
minimize_button = ctk.CTkButton(root, text="Minimize to Tray", font=custom_font, command=minimize_to_tray)
minimize_button.pack(pady=10)
load_settings()
process_ui_queue()
root.mainloop()
