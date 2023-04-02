import os
import subprocess
import yt_dlp
import re
import json
import shutil

from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW
from tkinter import messagebox

keys = None
try:
    with open("keys.txt", "r") as file:
        keys = json.load(file)
    api_key = keys["API_KEY"]
except:
    pass

def local_whisper(audio_file, model, language, prompt):
    audio_path = audio_file
    model = model
    output_format = "srt"
    temperature = 0.0 #at zero, basically turns off best_of
    best_of = 5

    if language:
        cmd = ['whisper', 
                audio_path, 
                '--model', model, 
                '--output_dir', ".", 
                '--output_format', output_format,
                '--initial_prompt', prompt,
                '--language', language,
                '--temperature', f'{temperature}',
                '--best_of',  f'{best_of}']
    else:
        cmd = ['whisper', 
                audio_path, 
                '--model', model, 
                '--output_dir', ".", 
                '--output_format', output_format,
                '--initial_prompt', prompt,
                '--temperature', f'{temperature}',
                '--best_of', f'{best_of}']

    subprocess.run(cmd)


def whisperapi_audio(audio_file, language, prompt):
    # This is needed because some video titles aren't parsed correctly by openAI.  Yields a "1"
    new_name = "transcribe.mp3"
    shutil.copy(audio_file, new_name)
    if language:
        cmd = [
            "curl",
            "https://api.openai.com/v1/audio/transcriptions",
            "-X","POST",
            "-H",f"Authorization: Bearer {api_key}",
            "-H","Content-Type: multipart/form-data",
            "-F",f"file=@{new_name}",
            "-F","model=whisper-1",
            "-F",f"prompt={prompt}",
            "-F","response_format=srt",
            "-F",f"language={language}"
        ]
    else:
        cmd = [
            "curl",
            "https://api.openai.com/v1/audio/transcriptions",
            "-X","POST",
            "-H",f"Authorization: Bearer {api_key}",
            "-H","Content-Type: multipart/form-data",
            "-F",f"file=@{new_name}",
            "-F","model=whisper-1",
            "-F",f"prompt={prompt}",
            "-F","response_format=srt"
        ]
    
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW

    # Run the cURL command as a subprocess with the console window hidden
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', startupinfo=startupinfo) 

    # extract the SRT portion from the response
    stdout_lines = result.stdout.splitlines()
    srt_lines = ['1'] + stdout_lines[1:] # add the first line with "1" and start extracting from the second line
    srt_text = "\n".join(srt_lines)
    os.remove("transcribe.mp3")

    return srt_text

# function to download YouTube video and extract audio using yt-dlp and ffmpeg
def download_youtube_video(youtube_link, quality = "64"):
    codec = "mp3"
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

    audio_file = f"{info_dict['id']}.{codec}"

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

    if language:
        # Save the transcription as an Srt file with the same name as the video and language suffix
        with open(f"{video_title}_{language}.srt", "w", encoding='utf-8') as f:
            f.write(transcription)
    else:
        with open(f"{video_title}.srt", "w", encoding='utf-8') as f:
            f.write(transcription)

def rename_files(youtube_link, language, save):
    # Create the "youtube_videos" directory if it doesn't exist
    output_directory = "youtube_files"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
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

    if language:
        srt_filename = f"{video_id}_{language}.srt"
    else:
        srt_filename = f"{video_id}.srt"
    
    # Move and rename srt file, overwriting if it exists
    if language:
        new_srt_filename = os.path.join(output_directory, f"{title}_{language}.srt")
    else:
        new_srt_filename = os.path.join(output_directory, f"{title}.srt")

    # Move and rename video file
    if save == "yes":
        new_video_filename = os.path.join(output_directory, f"{title}.mp4")
        if not os.path.exists(new_video_filename):
            os.rename(video_filename, new_video_filename)
            video_filename = new_video_filename
    else:
        os.remove(video_filename)

    # Move and rename audio file
    if save == "yes":
        new_audio_filename = os.path.join(output_directory, f"{title}.mp3")
        if not os.path.exists(new_audio_filename):
            os.rename(audio_filename, new_audio_filename)
            audio_filename = new_audio_filename
    else:
        os.remove(audio_filename)
        
    if os.path.exists(srt_filename):
        os.rename(srt_filename, new_srt_filename)  # rename, overwriting if it exists
        srt_filename = new_srt_filename
    else:
        print(f"File {srt_filename} not found at path {os.getcwd()}/{srt_filename}")

def update_progress(progress_bar, value):
    progress_bar["value"] = value
    progress_bar.update()

def convert_to_mp3(input_file, quality):
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
            "-b:a",
            f"{quality}k",
            output_file,
        ],
        check=True,
    )

    return output_file