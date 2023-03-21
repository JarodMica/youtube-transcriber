# auto-transcriber
Creates and outputs subtitles from either Youtube videos or local files.  Currently only supports Japanese and English, but if you want me to open it up in the future or if you want to modify it for more languages, the script has to modifed so that it passes the correct ISO 639-1 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) when selected in the window.

If you are doing a local video, you will see a screen pop up for the **ffmpeg** conversion, but once that is done, it will not pop up again for the file unless you delete the mp3 file.

Some future would-be-nices:
- Add auto-detect or additional languages (I personally like specifying the language, I feel like it's less error prone but that's just my hunch)
- Integrate it with the ability to be locally ran with Whisper, requires a good GPU depending on which model to be used.
- Option to keep or delete the files as a radio button in the GUI
- Beautify the GUI

