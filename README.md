# Chimera Creator
Chimera creator 

Chimera Creator is a Python Tkinter GUI that appends a ZIP archive to an existing .png, .gif, or .mp4 file. The resulting "chimera" file still behaves like the original image or video when opened normally, yet can also be renamed to .zip and opened with a third-party ZIP tool (7-Zip, WinRAR, etc.) to reveal hidden files or folders.

Important Note:

Windows Explorer typically rejects appended ZIP data (calling it "invalid zip"). You should use 7-Zip, WinRAR, or another ZIP tool to open the file after renaming.

Features
GUI with fields for:
Original File: must be .png, .gif, or .mp4
Either a single File to Attach or a single Folder to Attach (mutually exclusive)
"X" buttons to clear each entry
Instructions displayed in the feedback area by default
Output file name is "chimera_<original_basename>.<ext>"
No additional Python libraries required (only tkinter, zipfile, etc. from the standard library)

License
This project is released under the MIT License (or whichever license you choose). See a LICENSE file for details.

Author
by Amadon 
