![water_timer_3](https://github.com/user-attachments/assets/2c1bcc3b-415e-4989-b79b-136fe4fa27ee)

**Release Name**: Dawson's Water Reminder v12.7.0  
**Release Date**: January 20th, 2025
**Supported**: Windows 10/11

### Important Notice:  
Due to a false positive detection by Windows Defender Security, most likely from this not having a CA digital signature, it is currently necessary to create an exception in Defender Security to allow the installation and proper functioning of the application. Currently working on getting this fixed.

# Dawson's Water Reminder

**Dawson's Water Reminder** is a simple yet effective desktop application designed to remind users to stay hydrated throughout the day. Built with Python, the app uses `customtkinter` for the user interface, `pygame` for sound management, and offers a system tray integration for minimized operation. It includes features like automatic startup on Windows boot, customizable reminder intervals, and sound selection.

## Key Features:
- **Customizable Reminder Intervals**: Set the frequency of reminders in minutes.
- **Sound Notifications**: Choose a custom sound to play at each reminder.
- **System Tray Integration**: Minimize the app to the system tray for convenient background operation.
- **Autostart with Windows**: Option to enable or disable the app to start automatically when Windows boots.
- **Audio Device Change Handling**: Automatically adjusts when the audio device is changed.
- **Configurable Settings**: Save and load user settings such as volume, reminder interval, and sound file.
- **Cross-platform**: Works on Windows, with future potential for cross-platform compatibility.

## Libraries Used:
- `customtkinter`: A custom version of Tkinter for modern UI elements.
- `pygame`: For sound playback functionality.
- `pystray`: To create a system tray icon with options for app control.
- `ctypes`, `comtypes`: For handling Windows-specific APIs such as detecting audio device changes.
- `winreg`: For managing the Windows registry for autostart functionality.
- `configparser`: For storing and loading user settings from a configuration file.

## How It Works:
- The app runs as a background process, reminding you to drink water at regular intervals.
- It includes an interactive interface for selecting sound files, adjusting the volume, and setting the reminder interval.
- It can be minimized to the system tray and continues to run quietly in the background.
- On detecting an audio device change (such as switching from speakers to headphones), the app automatically reinitializes the sound system to ensure proper playback.
- The app is fully configurable and saves settings such as the reminder interval, sound file, volume, and autostart preference.

Here’s the updated version with optional instructions for downloading a provided `.wav` file:  

---

# Installation Instructions  

### Important Notice:  
Again, due to a false positive detection by Windows Defender Security, it is currently necessary to create an exception in Defender Security to allow the installation and proper functioning of the application. Currently working on getting this fixed.

#### To install **Dawson's Water Reminder v12.7.0**, follow these steps:  

1. **Download the Installer:**  
   - Click the **DawsonsWaterReminderv12.7.0_Setup.exe** to download the installer.  

2. **Download a Sound File (Optional):**  
   - If you do not have a preferred `.wav` sound file for the reminder, download one of the provided `.wav` audio files from below.
   - Save the file to an easily accessible location, such as your Documents, Downloads, Music, or Desktop folder.  

3. **Run the Installer:**  
   - Locate the downloaded installer file and double-click it to start the installation process.  
   - Follow the on-screen prompts to complete the installation.  

4. **Launch the Application:**  
   - After installation, find Dawson's Water Reminder in your Start menu or on your Desktop (if the option was selected during installation).  
   - Double-click the icon to open the application.  

5. **Set Up Your Reminder:**  
   - During the initial setup, select your `.wav` file by clicking the "Select Sound" button in the application. You can choose the downloaded default sound file or your own `.wav` file below 100MB.  
   - Configure your reminder intervals and volume preferences to get started.  

### System Requirements:  
- **OS:** Windows 10/11  
- **Python:** Not required; the application comes with all necessary dependencies pre-packaged.  
- **Disk Space:** Approximately 25 MB  

### Troubleshooting:  
- If you encounter any issues with the installation, ensure that your antivirus or firewall settings are not blocking the installer.  

This project is a great way to stay hydrated while working on your computer, and it's designed to be lightweight and unobtrusive. If you have suggestions or want to contribute, feel free to open an issue or create a pull request! If you discover any issues please report to [Water-Reminder/Issues](https://github.com/Dawson206/Water-Reminder/issues)

### v12.6.0 to v12.7.0 [Changelog](https://github.com/Dawson206/Water-Reminder/blob/main/changelog_v12.7.0.txt)
