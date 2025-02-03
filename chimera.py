#!/usr/bin/env python3

import os
import tkinter as tk
from tkinter import filedialog
import zipfile

def create_unencrypted_zip(file_paths, folder_paths, zip_path):
    """
    Creates a plain ZIP with no compression (ZIP_STORED), allowing large sizes (allowZip64=True).
    Third-party tools like 7-Zip or WinRAR can open it reliably.
    """
    with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        # Attach individual files
        for f in file_paths:
            arcname = os.path.basename(f)
            zf.write(f, arcname=arcname)

        # Attach entire folders (recursively)
        for d in folder_paths:
            for root, _, filenames in os.walk(d):
                for fname in filenames:
                    full_path = os.path.join(root, fname)
                    # Rel path from the folder itself
                    rel_path = os.path.relpath(full_path, d)
                    # Put that folder as a top-level entry in the zip
                    arcname = os.path.join(os.path.basename(d), rel_path)
                    zf.write(full_path, arcname=arcname)

def create_chimera_file(original_file, zip_path, output_file):
    """
    Appends the ZIP data to the original media file (PNG/GIF/MP4).
    Opening normally => media; rename to .zip => can see hidden files in 7-Zip/WinRAR.
    """
    CHUNK_SIZE = 65536

    with open(original_file, 'rb') as f_in, \
         open(zip_path, 'rb') as f_zip, \
         open(output_file, 'wb') as f_out:

        # Write original file in chunks
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            f_out.write(chunk)

        # Append zip data in chunks
        while True:
            chunk = f_zip.read(CHUNK_SIZE)
            if not chunk:
                break
            f_out.write(chunk)

class ChimeraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chimera Creator")
        self.geometry("530x390")
        self.resizable(False, False)

        # Flag to know if instructions are still displayed
        self.instructions_active = True

        # ---- Title Label ----
        title_label = tk.Label(self, text="Chimera Creator", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 5))

        # ---- Main Frame (Grid) for Fields ----
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ROW 0: Original
        tk.Label(frame, text="Original (.png/.gif/.mp4):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.input_file_var = tk.StringVar()
        self.input_file_entry = tk.Entry(frame, textvariable=self.input_file_var, width=40)
        self.input_file_entry.grid(row=0, column=1, pady=2)

        self.input_file_browse = tk.Button(frame, text="Browse...", width=8, command=self.handle_browse_original)
        self.input_file_browse.grid(row=0, column=2, padx=5, pady=2)

        self.input_file_clear = tk.Button(frame, text="X", width=2, command=self.handle_clear_original)
        self.input_file_clear.grid(row=0, column=3, padx=2, pady=2)

        # ROW 1: File
        tk.Label(frame, text="File to Attach:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.attach_file_var = tk.StringVar()
        self.attach_file_entry = tk.Entry(frame, textvariable=self.attach_file_var, width=40)
        self.attach_file_entry.grid(row=1, column=1, pady=2)

        self.attach_file_browse = tk.Button(frame, text="Browse...", width=8, command=self.handle_browse_file)
        self.attach_file_browse.grid(row=1, column=2, padx=5, pady=2)

        self.attach_file_clear = tk.Button(frame, text="X", width=2, command=self.handle_clear_file)
        self.attach_file_clear.grid(row=1, column=3, padx=2, pady=2)

        # ROW 2: Folder
        tk.Label(frame, text="Folder to Attach:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.attach_folder_var = tk.StringVar()
        self.attach_folder_entry = tk.Entry(frame, textvariable=self.attach_folder_var, width=40)
        self.attach_folder_entry.grid(row=2, column=1, pady=2)

        self.attach_folder_browse = tk.Button(frame, text="Browse...", width=8, command=self.handle_browse_folder)
        self.attach_folder_browse.grid(row=2, column=2, padx=5, pady=2)

        self.attach_folder_clear = tk.Button(frame, text="X", width=2, command=self.handle_clear_folder)
        self.attach_folder_clear.grid(row=2, column=3, padx=2, pady=2)

        # ROW 3: Feedback
        self.feedback_label = tk.Label(
            frame,
            text="",
            fg="green",
            height=10,
            wraplength=500,
            justify="left",
            anchor="nw"
        )
        self.feedback_label.grid(row=3, column=0, columnspan=4, padx=5, pady=(10, 0))

        # ---- Bottom Buttons
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(pady=(10, 10))

        self.create_button = tk.Button(bottom_frame, text="Create Chimera", command=self.handle_create_chimera)
        self.create_button.pack(side="left", padx=10)

        self.instructions_button = tk.Button(bottom_frame, text="Instructions", command=self.handle_instructions)
        self.instructions_button.pack(side="left", padx=10)

        self.amadon_label = tk.Label(self, text="by Amadon", font=("Arial", 10, "italic"))
        self.amadon_label.pack(side="bottom", pady=(5, 10))

        # watchers for mutual exclusivity
        self.attach_file_var.trace_add("write", self.on_file_changed)
        self.attach_folder_var.trace_add("write", self.on_folder_changed)

        # Show instructions by default
        self.show_instructions_in_feedback()

    def remove_instructions_if_active(self):
        if self.instructions_active:
            self.feedback_label.config(text="", fg="green")
            self.instructions_active = False

    def handle_clear_original(self):
        self.remove_instructions_if_active()
        self.input_file_var.set("")

    def handle_clear_file(self):
        self.remove_instructions_if_active()
        self.attach_file_var.set("")

    def handle_clear_folder(self):
        self.remove_instructions_if_active()
        self.attach_folder_var.set("")

    def handle_browse_original(self):
        self.remove_instructions_if_active()
        fp = filedialog.askopenfilename(
            title="Select original (PNG, GIF, or MP4)",
            filetypes=[("PNG/GIF/MP4", "*.png *.gif *.mp4"), ("All Files", "*.*")]
        )
        if fp:
            self.input_file_var.set(fp)

    def handle_browse_file(self):
        self.remove_instructions_if_active()
        fp = filedialog.askopenfilename(title="Select file to attach")
        if fp:
            self.attach_file_var.set(fp)

    def handle_browse_folder(self):
        self.remove_instructions_if_active()
        dp = filedialog.askdirectory(title="Select folder to attach")
        if dp:
            self.attach_folder_var.set(dp)

    def on_file_changed(self, *args):
        file_val = self.attach_file_var.get().strip()
        if file_val:
            self.attach_folder_entry.config(state="disabled")
            self.attach_folder_browse.config(state="disabled")
        else:
            self.attach_folder_entry.config(state="normal")
            self.attach_folder_browse.config(state="normal")

    def on_folder_changed(self, *args):
        folder_val = self.attach_folder_var.get().strip()
        if folder_val:
            self.attach_file_entry.config(state="disabled")
            self.attach_file_browse.config(state="disabled")
        else:
            self.attach_file_entry.config(state="normal")
            self.attach_file_browse.config(state="normal")

    def validate_inputs(self):
        original = self.input_file_var.get().strip()
        if not original or not os.path.exists(original):
            return False, "Original file does not exist."
        ext = os.path.splitext(original)[1].lower()
        if ext not in (".png", ".gif", ".mp4"):
            return False, "Original file must be a .png, .gif, or .mp4."

        f_val = self.attach_file_var.get().strip()
        d_val = self.attach_folder_var.get().strip()

        if bool(f_val) == bool(d_val):
            return False, "Attach exactly one: a single file OR a single folder."

        if f_val and not os.path.exists(f_val):
            return False, "The file to attach does not exist."
        if d_val and not os.path.exists(d_val):
            return False, "The folder to attach does not exist."

        return True, ""

    def handle_create_chimera(self):
        self.remove_instructions_if_active()

        ok, msg = self.validate_inputs()
        if not ok:
            self.feedback_label.config(text=msg, fg="red")
            return
        self.feedback_label.config(fg="green")

        original = self.input_file_var.get().strip()
        file_val = self.attach_file_var.get().strip()
        folder_val = self.attach_folder_var.get().strip()

        directory = os.path.dirname(original)
        base_name = os.path.splitext(os.path.basename(original))[0]
        ext = os.path.splitext(original)[1]
        out_file_name = f"chimera_{base_name}{ext}"
        out_file_path = os.path.join(directory, out_file_name)
        temp_zip = os.path.join(directory, "temp_chimera.zip")

        try:
            files, dirs = [], []
            if file_val:
                files.append(file_val)
            if folder_val:
                dirs.append(folder_val)

            create_unencrypted_zip(files, dirs, temp_zip)
            create_chimera_file(original, temp_zip, out_file_path)

            if os.path.exists(temp_zip):
                os.remove(temp_zip)

            success_message = (
                f"Chimera created:\n{out_file_path}\n\n"
                "To see hidden contents:\n"
                "1. Rename the file to .zip\n"
                "2. Open with 7-Zip, WinRAR, etc.\n"
            )
            self.feedback_label.config(text=success_message, fg="green")

        except Exception as e:
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
            self.feedback_label.config(text=f"Error: {e}", fg="red")

    def handle_instructions(self):
        self.feedback_label.config(
            text=self.get_instructions_text(),
            fg="green"
        )
        self.instructions_active = True

    def show_instructions_in_feedback(self):
        self.feedback_label.config(
            text=self.get_instructions_text(),
            fg="green"
        )
        self.instructions_active = True

    def get_instructions_text(self):
        return (
            "Instructions:\n\n"
            "1. Choose an Original File (.png, .gif, or .mp4).\n"
            "2. Attach ONE file or ONE folder (the other is disabled).\n"
            "3. Click 'Create Chimera' => 'chimera_<basename>.<ext>'.\n\n"
            "How to Open:\n"
            "- Normal usage: open as an image/video.\n"
            "- Hidden data: rename to '.zip' and open with 7-Zip or WinRAR.\n"
        )

def main():
    app = ChimeraApp()
    app.mainloop()

if __name__ == "__main__":
    main()
