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
import winreg
import sys


config = configparser.ConfigParser()

base_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(base_dir, "config.ini")

os.chdir(base_dir)

pygame.mixer.init()

reminder_sound = None
reminders_running = False
ui_queue = queue.Queue()


#Windows Core Audio API
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


def enable_autostart():
    try:
        app_name = "DawsonWaterReminder"
        executable_path = os.path.abspath(__file__)  #Path to your script
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
        winreg.CloseKey(key)
        messagebox.showinfo("Autostart Enabled", "The application will now start with Windows.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not enable autostart: {e}")


def disable_autostart():
    try:
        app_name = "DawsonWaterReminder"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        messagebox.showinfo("Autostart Disabled", "The application will no longer start with Windows.")
    except FileNotFoundError:
        messagebox.showinfo("Autostart Not Found", "Autostart is already disabled.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not disable autostart: {e}")


def toggle_autostart():
    """
    Enable or disable autostart based on the state of autostart_enabled.
    """
    app_name = "DawsonsWaterReminder"

    if getattr(sys, 'frozen', False):  #Check if running as a PyInstaller package
        exe_path = sys.executable
    else:  #Running as a script
        exe_path = os.path.abspath(__file__)

    registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_SET_VALUE) as key:
            if autostart_enabled.get() == 1:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                save_settings()
            else:  # Disable autostart
                winreg.DeleteValue(key, app_name)
                save_settings()
    except FileNotFoundError:
        if autostart_enabled.get() == 0:
            messagebox.showinfo("Autostart Already Disabled", "Autostart was not enabled.")
    except Exception as e:
        messagebox.showerror("Autostart Error", f"Failed to update autostart settings: {str(e)}")


def get_config_file_path():
    if getattr(sys, 'frozen', False):  #If running as a PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    #Use AppData folder for the config file in case of packaged app
    appdata_dir = os.getenv('APPDATA', os.path.expanduser("~"))
    config_file_path = os.path.join(appdata_dir, "DawsonsWaterReminder", "config.ini")

    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

    return config_file_path

config_file_path = get_config_file_path()


def load_settings():
    global reminder_sound
    try:
        if os.path.exists(config_file_path):
            config.read(config_file_path)
            if "Settings" in config:
                sound_path = config["Settings"].get("sound_file", "")
                volume_level = config["Settings"].getint("volume", 75)
                reminder_interval = config["Settings"].getint("interval_minutes", 30)
                volume.set(volume_level)
                interval_minutes.set(reminder_interval)
                interval_slider.set(reminder_interval)
                update_slider_label(reminder_interval)
                autostart_state = config["Settings"].getint("autostart", 0)
                autostart_enabled.set(autostart_state)

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
        else:
            save_settings()

    except Exception as e:
        messagebox.showerror("Error", f"Could not load settings: {str(e)}")


def save_settings(sound_file_path=None):
    if "Settings" not in config:
        config["Settings"] = {}

    if sound_file_path:
        config["Settings"]["sound_file"] = sound_file_path

    config["Settings"]["volume"] = str(volume.get())
    config["Settings"]["interval_minutes"] = str(interval_minutes.get())
    config["Settings"]["interval_slider"] =str(interval_slider.get())
    config["Settings"]["autostart"] = str(autostart_enabled.get())

    try:
        with open(config_file_path, "w") as config_file:
            config.write(config_file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")


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
    interval_slider.configure(state="disabled")
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
    interval_slider.configure(state="normal")
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
            MenuItem("Start", start_reminders),
            MenuItem("Stop", stop_reminders),
            MenuItem("Restore", restore_window),
            MenuItem("Quit", quit_app)
        )
        icon = Icon(icon_image_path, icon_image, menu=menu)
        icon.run()
    except Exception as e:
        print(f"Error loading tray icon: {e}")
    

def update_slider_label(value):
    reminder_label.configure(text=f"Reminder Time: {int(value)} (Minutes)")


def save_on_exit():
    save_settings()
    root.destroy()


#Global Variables:
root = ctk.CTk()

autostart_enabled = ctk.IntVar(value=0)
if not os.path.exists(config_file_path):
    autostart_enabled.set(0)

root.title(f"Dawson's Water Reminder")
build_number = "v12.7.0 - Jan 26th, 2025"
root.geometry("400x775")
root.resizable(True, True)
root.configure(bg="#A8E6A1")
root.protocol("WM_DELETE_WINDOW", save_on_exit)
icon_path = os.path.join(base_dir, "water_timer_3.ico")
root.iconbitmap(icon_path)
custom_font = ctk.CTkFont(family="Arial", size=12)
interval_minutes = ctk.IntVar(value=30)


#Select Audio & Volume Slider Frame
sound_frame = ctk.CTkFrame(root)
sound_frame.pack(pady=20, padx=20, fill="x")

volume_label = ctk.CTkLabel(sound_frame, text="Select An Audio File (.WAV)", font=custom_font)
volume_label.pack(pady=5)
sound_button = ctk.CTkButton(sound_frame, text="Select Sound", font=custom_font, command=select_sound_file)
sound_button.pack(pady=10)
volume_label = ctk.CTkLabel(sound_frame, text="Volume:", font=custom_font)
volume_label.pack(pady=5)
volume = ctk.IntVar(value=75)
volume_slider = ctk.CTkSlider(sound_frame, from_=0, to=100, variable=volume, command=update_volume, width=200)
volume_slider.pack(pady=(0, 20))

#Preview Audio Frame
preview_frame = ctk.CTkFrame(root)
preview_frame.pack(pady=20, padx=20, fill="x")

preview_label = ctk.CTkLabel(preview_frame, text="Preview Audio", font=custom_font)
preview_label.pack(pady=5)
preview_button = ctk.CTkButton(preview_frame, text="Preview Sound", font=custom_font, command=preview_sound)
preview_button.pack(pady=10)
stop_preview_button = ctk.CTkButton(preview_frame, text="Stop Preview Sound", font=custom_font, command=stop_preview_sound, state="disabled")
stop_preview_button.pack(pady=(10, 20))

#Reminder Time Slider Frame
remindertime_frame = ctk.CTkFrame(root)
remindertime_frame.pack(pady=20, padx=20, fill="x")

reminder_label = ctk.CTkLabel(
    remindertime_frame, 
    text=f"Reminder Time: {interval_minutes.get()} (Minutes)", 
    font=custom_font
)
reminder_label.pack(pady=10)

interval_slider = ctk.CTkSlider(
    remindertime_frame,
    from_=1,
    to=60,
    variable=interval_minutes,
    command=lambda value: (interval_minutes.set(int(value)), update_slider_label(int(value))),
    number_of_steps=59,
    width=200
)
interval_slider.pack()

start_button = ctk.CTkButton(remindertime_frame, text="Start Reminders", font=custom_font, command=start_reminders)
start_button.pack(pady=(20, 10))
stop_button = ctk.CTkButton(remindertime_frame, text="Stop Reminders", font=custom_font, command=stop_reminders, state="disabled")
stop_button.pack(pady=10)
countdown_label = ctk.CTkLabel(remindertime_frame, text="Next reminder in: --:--", font=custom_font)
countdown_label.pack(pady=10)

#Minimize To Tray
minimize_button = ctk.CTkButton(root, text="Minimize to Tray", font=custom_font, command=minimize_to_tray)
minimize_button.pack(pady=10)

#Start on boot
autostart_frame = ctk.CTkFrame(root)
autostart_frame.pack(pady=20, padx=20, fill="x")
autostart_checkbox = ctk.CTkCheckBox(
    autostart_frame,
    text="Start with Windows",
    variable=autostart_enabled,
    command=toggle_autostart,
    font=custom_font,
    height=20,
    width=20,
)
autostart_checkbox.pack(pady=10)

#Information Frame
info_frame = ctk.CTkFrame(root,)
info_frame.pack(pady=20, padx=20, fill="x")
build_number_color = "#ffffff"
label_name_color = "#ffffff"
combined_text = f"Build {build_number}\nConnor Dawson Carlson"
combined_label = ctk.CTkLabel(info_frame, text=combined_text, font=custom_font, text_color=build_number_color)
combined_label.pack(pady=5)

load_settings()
process_ui_queue()
root.mainloop()
