![water_timer_3](https://github.com/user-attachments/assets/2c1bcc3b-415e-4989-b79b-136fe4fa27ee)

**Release Name**: Dawson's Water Reminder v12.8.1  
**Release Date**: October 17th, 2025
**Supported**: Windows 10/11

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

#### To install **Dawson's Water Reminder**, follow these steps:  

1. **Download the Installer:**  
   - Click the **DawsonsWaterReminder.exe** to download the application.  

2. **Download a Sound File (Optional):**  
   - If you do not have a preferred `.wav` sound file for the reminder, download one of the provided `.wav` audio files from below.
   - Save the file to an easily accessible location, such as your Documents, Downloads, Music, or Desktop folder.  

3. **Run the application:**  
   - Locate the downloaded file and double-click it to start the installation.  
   - Follow the on-screen prompts to complete setup.  
   - Windows may show a message saying:  
     *“Microsoft Defender SmartScreen prevented an unrecognized app from starting. Running this app might put your PC at risk.”*  
   - Click **More Info**, then select **Run Anyway** to continue.  

   **Note:**  
   This message appears because the installer isn’t digitally signed yet, not because it’s unsafe. The app has been tested and is safe to run     the prompt simply means Windows doesn’t recognize the publisher.


4. **Launch the Application:**  
   - After installation, find Dawson's Water Reminder in your Start menu or on your Desktop (if the option was selected during installation).  
   - Double-click the icon to open the application.  

5. **Set Up Your Reminder:**  
   - During the initial setup, select your `.wav` file by clicking the "Select Sound" button in the application. You can choose the downloaded default sound file or your own `.wav` file below 100MB.  
   - Configure your reminder intervals and volume preferences to get started.  
 
6. **Auto Start with Windows:**  
   - To allow this application to start automatically when Windows boots, follow these steps:  
   - Right-click the **.exe** file and select **Create shortcut**.  
   - Press **Windows + R** on your keyboard to open the Run dialog.  
   - Type:
     ```
     shell:startup
     ```
   - Press **Enter** to open the Startup folder.  
   - Drag and drop the shortcut you created into this folder.  
   - The application will now launch automatically each time you log in to Windows.  

   **What `shell:startup` Does:**  
   Typing `shell:startup` simply opens a safe Windows system folder that runs any shortcuts placed inside it when you log in.  
   It’s the same method Windows uses for programs like OneDrive or Discord to start automatically.  

### System Requirements:  
- **OS:** Windows 10/11  
- **Python:** Not required; the application comes with all necessary dependencies pre-packaged.  
- **Disk Space:** Approximately 25 MB  

### Troubleshooting:  
- If you encounter any issues with the installation, ensure that your antivirus or firewall settings are not blocking the .exe.  

This project is a great way to stay hydrated while working on your computer, and it's designed to be lightweight and unobtrusive. If you have suggestions or want to contribute, feel free to open an issue or create a pull request! If you discover any issues please report to [Water-Reminder/Issues](https://github.com/Dawson206/Water-Reminder/issues)

### v12.6.0 to v12.8.1 [Changelog](https://github.com/Dawson206/Water-Reminder/blob/main/changelog_v12.7.0.txt)
