import tkinter as tk
import threading

from tkinter import font
from tkinter import ttk
from tkinter import StringVar



def create_button_style(root):
    style = ttk.Style(root)
    style.configure(
        "Fancy.TButton",
        background="#2E2E2E",
        foreground="#000000",
        font=("Helvetica", 12),
        borderwidth=1,
        relief="raised",
    )
    style.map(
        "Fancy.TButton",
        background=[("active", "#E5E5E5")],
        foreground=[("active", "#000000")],
        relief=[("active", "raised")],
    )
    
    return style

import tkinter as tk

def create_context_menu(entry):
    def copy():
        entry.clipboard_clear()
        entry.clipboard_append(entry.selection_get())

    def paste():
        entry.delete("sel.first", "sel.last")
        entry.insert(tk.INSERT, entry.clipboard_get())

    def cut():
        copy()
        entry.delete("sel.first", "sel.last")

    context_menu = tk.Menu(entry, tearoff=0)
    context_menu.add_command(label="Cut", command=cut)
    context_menu.add_command(label="Copy", command=copy)
    context_menu.add_command(label="Paste", command=paste)

    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    entry.bind("<Button-2>", show_context_menu)
    entry.bind("<Button-3>", show_context_menu)




def create_app(youtube_transcription, select_local_file):
     # create the main window
    root = tk.Tk()
    root.title("YouTube Transcription")
    root.geometry("500x500")
    root.configure(bg="#2b2b2b")
    create_button_style(root)  # Call the create_button_style function


    # create custom fonts
    label_font = font.Font(family="Helvetica", size=14, weight="bold")
    entry_font = font.Font(family="Helvetica", size=12)
    button_font = font.Font(family="Helvetica", size=12, weight="bold")

    # create a frame to hold the widgets
    main_frame = tk.Frame(root, bg="#2b2b2b")
    main_frame.pack(pady=20)

    # create the link entry
    link_label = tk.Label(main_frame, text="Enter the YouTube link:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    link_label.pack(anchor="w", padx=(10, 0), pady=(0, 5))
    link_entry = tk.Entry(main_frame, bg="#4b4b4b", fg="#ffffff", insertbackground="#ffffff", font=entry_font, width=50)
    link_entry.pack(anchor="w", padx=(10, 0), pady=(0, 10))
    create_context_menu(link_entry)  # Add this line

    # create the prompt entry
    prompt_label = tk.Label(main_frame, text="Enter Transcription Advice:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    prompt_label.pack(anchor="w", padx=(10, 0), pady=(0, 5))
    prompt_entry = tk.Entry(main_frame, bg="#4b4b4b", fg="#ffffff", insertbackground="#ffffff", font=entry_font, width=50)
    prompt_entry.pack(anchor="w", padx=(10, 0), pady=(0, 20))
    create_context_menu(prompt_entry)

    # create the local file transcription button
    local_file_button = ttk.Button(main_frame, text="Transcribe Local File", style="Fancy.TButton", command=lambda: threading.Thread(target=select_local_file, args=(prompt_entry, progress_bar, language_combobox, audio_quality_combobox)).start())
    local_file_button.pack(anchor="center", pady=(0, 20), expand=True)

    # create the start button
    youtube_button = ttk.Button(main_frame, text="Transcribe Youtube Video", style="Fancy.TButton", command=lambda: threading.Thread(target=youtube_transcription, args=(link_entry, progress_bar, prompt_entry, language_combobox, audio_quality_combobox, save)).start())
    youtube_button.pack(anchor="center", pady=(0, 20), expand=True)

    # create the progress bar
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate", maximum=100)
    progress_bar.pack(anchor="center", pady=(0, 10))

    # create the audio quality drop-down menu
    audio_quality_label = tk.Label(main_frame, text="Select audio quality:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    audio_quality_label.pack(anchor="w", padx=(10, 0), pady=(0, 5))
    audio_quality_combobox = ttk.Combobox(main_frame, values=["16", "32", "64", "128", "192", "256", "320"], state="readonly", font=entry_font)
    audio_quality_combobox.pack(anchor="w", padx=(140, 0), pady=(0, 20))
    audio_quality_combobox.current(3)  # Set the default value to 128

    # create the language drop-down menu
    language_label = tk.Label(main_frame, text="Select language:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    language_label.pack(anchor="w", padx=(10, 0), pady=(0, 5))
    language_combobox = ttk.Combobox(main_frame, values=["Auto", "English", "Japanese"], state="readonly", font=entry_font)
    language_combobox.pack(anchor="w", padx=(140, 0), pady=(0, 20))
    language_combobox.current(0)  # Set the default value to Auto

    # create the checkbox
    save = StringVar(value="yes")  # Default value is "yes"
    checkbox = tk.Checkbutton(main_frame, text="Save Yt After Download", variable=save, onvalue="yes", offvalue="no", bg="#2b2b2b", fg="#ffffff", selectcolor="#2b2b2b", font=label_font, activebackground="#2b2b2b", activeforeground="#ffffff")
    checkbox.pack(anchor="w", padx=(10, 0), pady=(0, 20))


    root.mainloop()
