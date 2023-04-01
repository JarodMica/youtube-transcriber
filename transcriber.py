import os

from tkinter import filedialog
from tkinter import messagebox
from utilities import transcribe_audio, download_youtube_video, save_transcription_as_srt, rename_files, update_progress, convert_to_mp3
from gui import create_app, redirect_output_to_tempfile



def start_transcription(link_entry, progress_bar, prompt_entry, language_combobox, quality, save):
    youtube_link = link_entry.get()
    quality = quality.get()
    save = save.get()
    if language_combobox.get() == "English":
        language = "en"
    elif language_combobox.get() == "Japanese":
        language = "ja"
    else:
        language = False
    

    prompt = prompt_entry.get()


    if not youtube_link.strip():
        messagebox.showerror("Error", "Please enter a YouTube link.")
        return

    if not prompt.strip():
        messagebox.showinfo("No Prompt", "Using default prompt.")
        prompt = "focus on nautral speech"
    else:
        pass

    try:
        update_progress(progress_bar, 10)
        audio_file = download_youtube_video(youtube_link, quality)
        update_progress(progress_bar, 30)
        transcription = transcribe_audio(audio_file, language, prompt)
        update_progress(progress_bar, 60)
        save_transcription_as_srt(transcription, youtube_link, language)
        update_progress(progress_bar, 80)
        rename_files(youtube_link, language, save)
        update_progress(progress_bar, 100)

        messagebox.showinfo("Success", "Transcription complete. Srt file saved.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during transcription: {e}")
    finally:
        update_progress(progress_bar, 0)  # Reset the progress bar

def select_local_file(prompt_entry, progress_bar, language_combobox, quality):
    quality = quality.get()
    
    if language_combobox.get() == "English":
        language = "en"
    elif language_combobox.get() == "Japanese":
        language = "ja"
    else:
        language = False
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav;*.m4a;*.mp4"), ("All files", "*.*")])
    if not file_path:
        return

    if file_path.lower().endswith(".mp4"):
        update_progress(progress_bar, 10)
        file_path = convert_to_mp3(file_path, quality)
        update_progress(progress_bar, 20)

    prompt = prompt_entry.get()
    if not prompt.strip():
        messagebox.showinfo("No Prompt", "Using default prompt.")
        prompt = "focus on nautral speech"
    else:
        pass
        
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



def main():
    app = create_app(start_transcription, select_local_file)
    if app is not None:
        app.mainloop()


if __name__ == "__main__":
    with redirect_output_to_tempfile() as temp_filename:
        main()
        with open(temp_filename, 'r') as temp_file:
            content = temp_file.read()
            print(f'Temporary file content:\n{content}')
    os.unlink(temp_filename)  # Remove the temporary file