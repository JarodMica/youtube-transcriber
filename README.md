# auto-transcriber
This is an auto-transcriber based on openAi's Whisper model.  This repo utilizes the API version of it so it requires an API key, however, it is very affordable in my honest opinion at $0.06 per 10 minutes of transcription.  Now supports all languages that are supported by openAI's whisper, but please note the accuracy is based on the language.  If you want to see your language's accuracy rating (lower is better), check out this graph here: https://github.com/openai/whisper/blob/main/language-breakdown.svg

## Features
- Download videos from youtube and transcribe them with an option to delete the videos afterwards
- Supports multiple languages, including English, Japanese, Spanish, Korean, German, etc.
- Transcribe local videos
- A "Transcription Advice" section which allows you to specify more details about the video you are transcribing (what language, theme, topic, etc).  This can result in a more accurate subtitle file
- Ability to change the audio quality of the mp3 file.  This is only imporant for file size as the whisper API can only take a maximum file size of 25mb. This means higher quality may result in (but not always) more accurate subtitles at the cost of file size, whereas lower quality will result in smaller file size.
    - Example: An hour long video at quality of 128 may take up 25 mb, meaning you can only transcribe up to an hour.  In contrast, for the same file size, you may be able to get a 2 hour long video at a quality of 64 due to it resulting in a smaller file size.

## Some future would-be-nices:
- Integrate it with the local version of Whisper, *requires a good GPU depending on which model to be used.*
- Beautify the GUI

Youtube video: https://www.youtube.com/watch?v=ft3A2LijQAo&t=116
