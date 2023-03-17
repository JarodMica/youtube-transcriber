import os
import subprocess
import yt_dlp
import re
import tkinter as tk
import threading
import json
import sys
import tempfile

from contextlib import contextmanager
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from tkinter import filedialog  # import filedialog module
from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW



keys = None

with open("keys.txt", "r") as file:
    keys = json.load(file)

api_key = keys["API_KEY"]


def transcribe_audio(audio_file, language, prompt="focus on nautral speech"):
    cmd = [
        "curl",
        "https://api.openai.com/v1/audio/transcriptions",
        "-X",
        "POST",
        "-H",
        f"Authorization: Bearer {api_key}",
        "-H",
        "Content-Type: multipart/form-data",
        "-F",
        f"file=@{audio_file}",
        "-F",
        "model=whisper-1",
        "-F",
        f"prompt={prompt}",
        "-F",
        "response_format=srt",
        "-F",
        f"language={language}",
        "-F",
        "temperature=0.2"
    ]
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW

    # Run the cURL command as a subprocess with the console window hidden
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', startupinfo=startupinfo) 

    # extract the SRT portion from the response
    stdout_lines = result.stdout.splitlines()
    srt_lines = ['1'] + stdout_lines[1:] # add the first line with "1" and start extracting from the second line
    srt_text = "\n".join(srt_lines)

    return srt_text


# function to download YouTube video and extract audio using yt-dlp and ffmpeg
def download_youtube_video(youtube_link, debug=False):
    codec = "mp3"
    quality = "64"
    ydl_opts = {
        'format': '22',
        'outtmpl': '%(id)s.%(ext)s',
        'keepvideo': True,
        'progress_hooks': [lambda d: None],
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': quality, #192 max
            }
        ],
        'preferredformat': f'{codec}',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_link, download=True)

    video_file = f"{info_dict['id']}.mp4"
    audio_file = f"{info_dict['id']}.{codec}"


    if debug:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_file,
                "-ss",
                "00:00:00",
                "-t",
                "00:60:00",
                "-vn",
                "-acodec",
                "libmp3lame",
                "-qscale:a",
                "2",
                f"{audio_file}_debug.{codec}",
            ],
            check=True,
        )
        audio_file = f"{audio_file}_debug.{codec}"

    # if the audio file is greater than 25 MB, split it into chunks
    if os.path.getsize(audio_file) > 25 * 1024 * 1024:
        print("Audio size file is over 25mb! Stick to content under 1 hour!")
        raise SystemExit
        # split_audio_file(audio_file)
        # was supposed to be a chunking function, but didn't implement

    return audio_file


# function to save transcription as Srt file
def save_transcription_as_srt(transcription, source, language, is_youtube=True):
    if is_youtube:
        # Extract the video title from the YouTube link
        video_title = yt_dlp.YoutubeDL({}).extract_info(source, download=False)["id"]
    else:
        # Use the local file name without the extension
        video_title = os.path.splitext(os.path.basename(source))[0]

    # Save the transcription as an Srt file with the same name as the video and language suffix
    with open(f"{video_title}_{language}.srt", "w", encoding='utf-8') as f:
        f.write(transcription)


def rename_files(youtube_link, language):
    ydl_opts = {'quiet': True,
                'progress_hooks': [lambda d: None],
                'no_warnings': True,}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_link, download=False)

    title = re.sub(r'[^\w\s-]', '', info_dict['title'])  # remove non-alphanumeric characters
    title = re.sub(r'^\d+\s*', '', title)  # remove leading numbers
    title = title.strip().replace(' ', '_')  # replace spaces with underscores

    video_id = info_dict['id']
    video_filename = f"{video_id}.mp4"
    audio_filename = f"{video_id}.mp3"
    srt_filename = f"{video_id}_{language}.srt"
    
    # Create the "youtube_videos" directory if it doesn't exist
    output_directory = "youtube_videos"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Move and rename video file
    new_video_filename = os.path.join(output_directory, f"{title}.mp4")
    if not os.path.exists(new_video_filename):
        os.rename(video_filename, new_video_filename)
        video_filename = new_video_filename

    # Move and rename audio file
    new_audio_filename = os.path.join(output_directory, f"{title}.mp3")
    if not os.path.exists(new_audio_filename):
        os.rename(audio_filename, new_audio_filename)
        audio_filename = new_audio_filename

    # Move and rename srt file, overwriting if it exists
    new_srt_filename = os.path.join(output_directory, f"{title}_{language}.srt")
    if os.path.exists(srt_filename):
        os.rename(srt_filename, new_srt_filename)  # rename, overwriting if it exists
        srt_filename = new_srt_filename
    else:
        print(f"File {srt_filename} not found at path {os.getcwd()}/{srt_filename}")

    return (video_filename, audio_filename, srt_filename)

def update_progress(progress_bar, value):
    progress_bar["value"] = value
    progress_bar.update()

def start_transcription(link_entry, progress_bar, prompt_entry, language_combobox):
    youtube_link = link_entry.get()
    language = "en" if language_combobox.get() == "English" else "ja"
    prompt = prompt_entry.get()


    if not youtube_link.strip():
        messagebox.showerror("Error", "Please enter a YouTube link.")
        return

    if not prompt.strip():
        messagebox.showerror("No Prompt", "Using default prompt.")
    else:
        prompt = ""

    try:
        update_progress(progress_bar, 10)
        audio_file = download_youtube_video(youtube_link)
        update_progress(progress_bar, 30)
        transcription = transcribe_audio(audio_file, language, prompt)
        update_progress(progress_bar, 60)
        save_transcription_as_srt(transcription, youtube_link, language)
        update_progress(progress_bar, 80)
        rename_files(youtube_link, language)
        update_progress(progress_bar, 100)

        messagebox.showinfo("Success", "Transcription complete. Srt file saved.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during transcription: {e}")
    finally:
        update_progress(progress_bar, 0)  # Reset the progress bar


from tkinter import messagebox

def convert_to_mp3(input_file):
    output_file = os.path.splitext(input_file)[0] + ".mp3"

    # Check if the output file already exists
    if os.path.exists(output_file):
        # Ask the user if they want to overwrite the existing file using a GUI
        response = messagebox.askyesno("Overwrite?", f"File '{output_file}' already exists. Overwrite?")
        if not response:
            # Return the path to the existing file if the user chooses not to overwrite it
            return output_file

    subprocess.run(
        [
            "ffmpeg",
            "-y",  # Add the '-y' option to overwrite the output file without confirmation
            "-i",
            input_file,
            "-vn",
            "-acodec",
            "libmp3lame",
            "-qscale:a",
            "2",
            output_file,
        ],
        check=True,
    )

    return output_file

def select_local_file(prompt_entry, progress_bar, language_combobox):
    language = "en" if language_combobox.get() == "English" else "ja"
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav;*.m4a;*.mp4"), ("All files", "*.*")])
    if not file_path:
        return

    if file_path.lower().endswith(".mp4"):
        update_progress(progress_bar, 10)
        file_path = convert_to_mp3(file_path)
        update_progress(progress_bar, 20)

    prompt = prompt_entry.get()
    if not prompt.strip():
        messagebox.showerror("No Prompt", "Using default prompt.")
    else:
        prompt = ""
        
    local_file_path = os.path.splitext(file_path)[0]

    try:
        update_progress(progress_bar, 30)
        transcription = transcribe_audio(file_path, language, prompt)
        update_progress(progress_bar, 60)
        save_transcription_as_srt(transcription, local_file_path, language, is_youtube=False)
        update_progress(progress_bar, 100)

        messagebox.showinfo("Success", "Transcription complete. Srt file saved.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during transcription: {e}")
    finally:
        update_progress(progress_bar, 0)  # Reset the progress bar

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

@contextmanager
def redirect_output_to_tempfile():
    # Save the original stdout and stderr
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr

    # Create a temporary file and redirect the stdout and stderr
    with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp_output:
        sys.stdout = temp_output
        sys.stderr = temp_output
        try:
            yield temp_output.name
        finally:
            # Restore the original stdout and stderr
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

def main():
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
    link_label.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(0, 5))
    link_entry = tk.Entry(main_frame, bg="#4b4b4b", fg="#ffffff", insertbackground="#ffffff", font=entry_font, width=50)
    link_entry.grid(row=1, column=0, padx=(10, 0), pady=(0, 10))


    # create the prompt entry
    prompt_label = tk.Label(main_frame, text="Enter the prompt:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    prompt_label.grid(row=2, column=0, sticky="w", padx=(10, 0), pady=(0, 5))
    prompt_entry = tk.Entry(main_frame, bg="#4b4b4b", fg="#ffffff", insertbackground="#ffffff", font=entry_font, width=50)
    prompt_entry.grid(row=3, column=0, padx=(10, 0), pady=(0, 20))

    # create the local file transcription button
    local_file_button = ttk.Button(main_frame, text="Select Local File", style="Fancy.TButton", command=lambda: threading.Thread(target=select_local_file, args=(prompt_entry, progress_bar, language_combobox)).start())
    local_file_button.grid(row=6, column=0, pady=(0, 20))
    # create the start button
    start_button = ttk.Button(main_frame, text="Start Transcription", style="Fancy.TButton", command=lambda: threading.Thread(target=start_transcription, args=(link_entry, progress_bar, prompt_entry, language_combobox)).start())
    start_button.grid(row=7, column=0, pady=(0, 20))

    # create the progress bar
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate", maximum=100)
    progress_bar.grid(row=8, column=0, pady=(0, 10))

    # create the language drop-down menu
    language_label = tk.Label(main_frame, text="Select language:", bg="#2b2b2b", fg="#ffffff", font=label_font)
    language_label.grid(row=9, column=0, sticky="w", padx=(10, 0), pady=(0, 5))
    language_combobox = ttk.Combobox(main_frame, values=["English", "Japanese"], state="readonly", font=entry_font)
    language_combobox.grid(row=10, column=0, padx=(140, 0), pady=(0, 20), sticky="w")
    language_combobox.current(0)  # Set the default value to English

    root.mainloop()


if __name__ == "__main__":
    with redirect_output_to_tempfile() as temp_filename:
        main()
        with open(temp_filename, 'r') as temp_file:
            content = temp_file.read()
            print(f'Temporary file content:\n{content}')
    os.unlink(temp_filename)  # Remove the temporary file