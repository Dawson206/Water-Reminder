Water Reminder App

The Water Reminder App is a simple desktop application built with Python using Tkinter, pygame, and pystray to help users remember to drink water at regular intervals. The app allows users to:

Set a reminder interval (in minutes) for the reminders.
Select a sound file to play as the reminder.
Preview and adjust the volume of the sound.
Minimize the app to the system tray for easy access while not in use.
Receive reminder notifications with a sound alert at the set intervals.
Features:

Sound Reminder: Plays a sound at the specified interval to remind users to drink water.
System Tray Icon: Allows users to minimize the app to the system tray, freeing up screen space.
Custom Sound and Volume: Users can select a custom sound file (WAV format) and adjust the volume.
Countdown Timer: Displays the time until the next reminder.
Start/Stop Functionality: Users can start and stop reminders easily through the interface.

Instructions:
1. Set Sound and Volume:
Click the Select Sound button to choose a WAV file (such as a sound for the reminder).
Click Preview Sound to play the selected sound and verify it.
Use the Volume Slider to adjust the sound's volume (0% to 100%).
2. Set Reminder Interval:
In the Set Reminder Interval (minutes) field, enter the number of minutes between each reminder. The default is 30 minutes.
3. Start Reminders:
Click Start Reminders to start receiving reminders at the set interval. A countdown will appear, showing the time remaining until the next reminder.
The interface will update to show the countdown and disable the start options.
4. Stop Reminders:
Click Stop Reminders to halt the reminders at any time. The countdown will reset, and the interface will return to its original state.
5. Minimize to Tray:
Click Minimize to Tray to hide the app window and move it to the system tray. Right-click the tray icon to restore or quit the app.
6. Preview and Stop Sound:
Click Preview Sound to hear the selected sound. If you're listening to a preview and want to stop it, click Stop Preview Sound.

Additional Details:
Tray Icon: The app uses the pystray library to create an icon in the system tray. It can be restored or quit by right-clicking the tray icon.
Threading: The reminder loop runs on a separate thread, ensuring that the main window remains responsive.
This application is ideal for people who need to be reminded to drink water regularly or take breaks at work. You can customize the reminder interval and sound according to your preferences.
