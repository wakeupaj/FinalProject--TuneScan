import os 
import tkinter as tk
from tkinter import filedialog
import librosa
from pytube import YouTube
from keyfinder import Tonal_Fragment
from pydub import AudioSegment

def main():
      window()

def window():
        gui = tk.Tk()

        gui.geometry("650x450")
        gui.title("TuneScan")
        icon_path = '/Users/aj/Developer/Projects/FinalProject/media/TuneScan.png'
        icon = tk.PhotoImage(file=icon_path)
        gui.tk.call('wm', 'iconphoto', gui._w, icon)

        detected_key_label = tk.Label(gui, text="")
        detected_key_label.pack()


        def upload_file():
            try:
                filetypes = [
                    ('WAV Files', '*.wav'), 
                    ('AIFF Files', '*.aiff'), 
                    ('MP3 Files', '*.mp3'),
                    ('M4A Files', '*.m4a'),
                    ('FLAC Files', '*.flac'), 
                    ('M4A Files', '*.m4a'),
                    ('OGG Files', '*.ogg'),
                    ('AAC Files', '*.aac')
                    ]  
                filepath = filedialog.askopenfilename(filetypes=filetypes)
                print("Selected File:", filepath)

                file_extension = os.path.splitext(filepath)[1]

                if file_extension != '.mp3':
                    mp3_filepath  = convert_to_mp3(filepath)
                    key = analyze_key(mp3_filepath)
                    os.remove(mp3_filepath)
                else:
                    key = analyze_key(filepath)
                detected_key_label.config(text=f"Detected Key: {key}")

            except Exception as e:
                    print("An error occurred:", e)
                    detected_key_label.config(text="Error in detecting key.")

       

        youtube_url_entry = tk.Entry(gui, fg='grey')
        youtube_url_entry.insert(0, "Enter YouTube URL")
        youtube_url_entry.pack(expand=True)

        def on_entry_click(event):
            if youtube_url_entry.get() == "Enter YouTube URL":
                youtube_url_entry.delete(0, tk.END)  
                youtube_url_entry.insert(0, '')  
                youtube_url_entry.config(fg='black')


        def on_focusout(event):
            if youtube_url_entry.get() == '':
                youtube_url_entry.insert(0, "Enter YouTube URL")
                youtube_url_entry.config(fg='grey')


        def upload_from_youtube():
                    url = youtube_url_entry.get()
                    if url and url != "Enter Youtube URL":
                        try:
                            audio_path = download_youtube_audio(url)
                            key = analyze_key(audio_path)
                            detected_key_label.config(text=f"Detected Key: {key}")
                            os.remove(audio_path)
                        except Exception as e:
                            print("An error occurred:", e)
                            os.remove(audio_path)
                            detected_key_label.config(text="Error in detecting key.")
                    else:
                        detected_key_label.config(text="Please enter a valid YouTube URL.")
                    

        upload_btn = tk.Button(gui, text="Select File", command=upload_file)
        upload_btn.pack(expand=True)

        youtube_btn = tk.Button(gui, text="Enter YouTube URL", command=upload_from_youtube)
        youtube_btn.pack(expand=True)

        gui.mainloop()

def convert_to_mp3(filepath):
    audio = AudioSegment.from_file(filepath)

    mp3_path = "converted_file.mp3"

    audio.export(mp3_path, format="mp3")

    return mp3_path

def download_youtube_audio(url):
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    destination = "yt_audio.mp3"
    audio.download(filename=destination)
    return destination

def analyze_key(filepath):
    y, sr = librosa.load(filepath, sr=None)

    fragment = Tonal_Fragment(y, sr)
    fragment.print_key()

    detected_key = fragment.key
    return detected_key

if __name__ == "__main__":
    main()