import customtkinter as ctk
from tkinter import Label, messagebox, filedialog
import pygame
import time
import threading
import os
import queue
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageTk
import configparser
import io
import base64
import ctypes
from ctypes import wintypes, POINTER
from comtypes import CLSCTX_ALL
from comtypes.client import CreateObject

config = configparser.ConfigParser()

base_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(base_dir, "config.ini")
config_file_path = "config.ini"

pygame.mixer.init()

reminder_sound = None
reminders_running = False
ui_queue = queue.Queue()

# Windows Core Audio API
MMDeviceEnumerator = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"
IMMNotificationClient = "{7991EEC9-7E89-4D85-8390-6C703CEC60C0}"

class AudioDeviceChangeHandler(ctypes.Structure):
    _fields_ = [
        ("lpVtbl", ctypes.POINTER(ctypes.c_void_p))
    ]

def on_device_change():
    global reminder_sound
    try:
        pygame.mixer.quit()
        pygame.mixer.init()
        if reminder_sound:
            reminder_sound.set_volume(volume.get() / 100)
    except Exception as e:
        print(f"Error reinitializing audio: {e}")

def monitor_audio_device_changes():
    device_enumerator = CreateObject(
        MMDeviceEnumerator,
        interface=POINTER(ctypes.c_void_p),
        clsctx=CLSCTX_ALL
    )
    client = AudioDeviceChangeHandler()
    device_enumerator.RegisterEndpointNotificationCallback(ctypes.byref(client))

def start_audio_monitor():
    def monitor_thread():
        monitor_audio_device_changes()
    threading.Thread(target=monitor_thread, daemon=True).start()

start_audio_monitor()


def hide_file(file_path):
    try:
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 2)  # 2 is the attribute for hidden
    except Exception as e:
        print(f"Error hiding file {file_path}: {e}")

def unhide_file(file_path):
    try:
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 0)  # 0 removes the hidden attribute
    except Exception as e:
        print(f"Error unhiding file {file_path}: {e}")


def load_settings():
    global reminder_sound
    if os.path.exists(config_file_path):
        unhide_file(config_file_path)
        config.read(config_file_path)
        if "Settings" in config:
            sound_path = config["Settings"].get("sound_file", "")
            volume_level = config["Settings"].getint("volume", 75)
            reminder_interval = config["Settings"].getint("interval_minutes", 30)
            volume.set(volume_level)
            interval_minutes.set(reminder_interval)
            if sound_path:
                if os.path.exists(sound_path):
                    load_sound(sound_path)
                    reminder_sound.set_volume(volume_level / 100)
                    volume.set(volume_level)
                else:
                    messagebox.showwarning("Broken Sound File", "The previously selected sound file is missing. Please select a new one.")
                    select_sound_file()
            else:
                messagebox.showwarning("No Sound File", "No sound file selected. Please select a sound file.")
                select_sound_file()


def save_settings(sound_file_path=None):
    unhide_file(config_file_path)
    if "Settings" not in config:
        config["Settings"] = {}
    if sound_file_path:
        config["Settings"]["sound_file"] = sound_file_path
    config["Settings"]["volume"] = str(volume.get())
    config["Settings"]["interval_minutes"] = str(interval_minutes.get())
    with open(config_file_path, "w") as config_file:
        config.write(config_file)
    hide_file(config_file_path)


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
        else:
            messagebox.showwarning("Broken Sound File", "The selected sound file is missing. Please select a new one.")
            select_sound_file()
    except Exception as e:
        reminder_sound = None
        messagebox.showerror("Error", f"Could not load sound: {str(e)}")


def preview_sound():
    if reminder_sound:
        reminder_sound.play()
        stop_preview_button.configure(state="normal")
    else: 
        messagebox.showerror("Error", "No sound file loaded to preview. Please select a sound file.")


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
    save_settings()
    reminders_running = True
    interval_seconds = interval_minutes.get() * 60
    reminder_thread = threading.Thread(target=reminder_loop, args=(interval_seconds,), daemon=True)
    reminder_thread.start()
    start_button.configure(state="disabled")
    interval_entry.configure(state="disabled")
    sound_button.configure(state="disabled")
    volume_slider.configure(state="normal")
    preview_button.configure(state="disabled")
    stop_preview_button.configure(state="disabled")
    stop_button.configure(state="normal")


def stop_reminders():
    global reminders_running
    reminders_running = False
    if reminder_sound:
        reminder_sound.stop()
    pygame.mixer.stop()
    save_settings()
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
    save_settings()
    if reminder_sound:
        reminder_sound.stop()
    pygame.mixer.quit()
    root.quit()
    icon.stop()
    os._exit(0)


def create_tray_icon():
    try:
        icon_image_path = os.path.join(base_dir, "water_timer_3.ico")
        icon_image = Image.open(icon_image_path).resize((64, 64))
        menu = Menu(
            MenuItem("Restore", restore_window),
            MenuItem("Quit", quit_app)
        )
        icon = Icon(icon_image_path, icon_image, menu=menu)
        icon.run()
    except Exception as e:
        print(f"Error loading tray icon: {e}")


def update_entry_width(*args):
    current_text = str(interval_minutes.get())
    min_width = 35
    additional_width = len(current_text) * 2
    new_width = min_width + additional_width
    interval_entry.configure(width=new_width)


def save_on_exit():
    save_settings()
    root.destroy()


root = ctk.CTk()
build_number = "v12.5.6"
root.title(f"Dawson's Water Reminder")
root.geometry("400x550")
root.resizable(True, True)
root.configure(bg="#A8E6A1")
root.protocol("WM_DELETE_WINDOW", save_on_exit)
icon_path = os.path.join(base_dir, "water_timer_3.ico")
root.iconbitmap(icon_path)
custom_font = ctk.CTkFont(family="Arial", size=12)
interval_minutes = ctk.IntVar(value=30)
volume_label = ctk.CTkLabel(root, text="Select & Preview Sound", font=custom_font)
volume_label.pack(pady=5)
sound_button = ctk.CTkButton(root, text="Select Sound", font=custom_font, command=select_sound_file)
sound_button.pack(pady=10)
volume_label = ctk.CTkLabel(root, text="Volume:", font=custom_font)
volume_label.pack(pady=5)
volume = ctk.IntVar(value=75)
volume_slider = ctk.CTkSlider(root, from_=0, to=100, variable=volume, command=update_volume, width=200)
volume_slider.pack()
preview_button = ctk.CTkButton(root, text="Preview Sound", font=custom_font, command=preview_sound)
preview_button.pack(pady=10)
stop_preview_button = ctk.CTkButton(root, text="Stop Preview Sound", font=custom_font, command=stop_preview_sound, state="disabled")
stop_preview_button.pack(pady=10)
label = ctk.CTkLabel(root, text="Reminder Time (Minutes):", font=custom_font)
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
build_number_color = "#ffffff"
build_number_label = ctk.CTkLabel(root, text=f"Build {build_number}", font=custom_font, text_color=build_number_color)
build_number_label.pack(pady=5)
build_number_label.place(x=200, y=560, anchor="center")
label_name = ctk.CTkLabel(root, text="Connor Dawson Carlson", font=custom_font)
label_name_color = "#ffffff"
label_name.pack(pady=5)
label_name.place(x=200, y=580, anchor="center")

load_settings()
process_ui_queue()
root.mainloop()
