import os
import tkinter as tk  # handles window/gui creation
import time
import threading
from tkinter import filedialog
from tkinter import ttk  # ttk is a theme tool; allows custom theme imports
import librosa  # an audio processing library
from pytube import YouTube  # pulls mp3 from youtube links
from keyfinder import (
    Tonal_Fragment,
)  # an audio analysis and key detection program; uses
from pydub import (
    AudioSegment,
)  # handles non '.mp3' files, and converts them as such; keyfinder only accepts '.mp3'
from PIL import Image, ImageTk  # handles image imports (for light/dark theme button)

# main function
def main():
    window()


def window():
    # create gui element, assign it to variable 'gui'
    gui = tk.Tk()

    # set window dimensions, locks it from being fullscreened or changed, and set window title
    gui.geometry("300x350")
    gui.resizable(False, False)
    gui.title("TuneScan")

    # defining theme path to a variable; was causing problem not doing it this way...
    script_directory = os.path.dirname(os.path.abspath(__file__))
    azure_theme_path = os.path.join(script_directory, "azure.tcl")

    # calls the theme
    gui.tk.call("source", azure_theme_path)
    gui.tk.call("set_theme", "light")

    # open and scale theme toggle image icons
    sun_image = Image.open("media/sun.png")
    sun_image = sun_image.resize((30, 30), Image.Resampling.LANCZOS)
    sun_icon = ImageTk.PhotoImage(sun_image)

    moon_image = Image.open("media/moon.png")
    moon_image = moon_image.resize((30, 30), Image.Resampling.LANCZOS)
    moon_icon = ImageTk.PhotoImage(moon_image)

    # used lots of online resources for this. not sure whats going on but it allows for a smooth transition between themes; opposed to a harsh transition
    def fade_background(start_color, end_color, steps=15, speed=0.01):
        for i in range(steps):
            # Calculate the next color
            new_red = int(
                start_color[0] + ((end_color[0] - start_color[0]) * i / steps)
            )
            new_green = int(
                start_color[1] + ((end_color[1] - start_color[1]) * i / steps)
            )
            new_blue = int(
                start_color[2] + ((end_color[2] - start_color[2]) * i / steps)
            )
            next_color = f"#{new_red:02x}{new_green:02x}{new_blue:02x}"

            # Update the GUI's background
            gui.config(bg=next_color)
            gui.update()  # Update the GUI
            time.sleep(speed)  # Short delay between color updates

    # handles theme toggling and button icon changing with if loop
    def toggle_theme():
        current_theme = gui.tk.call("ttk::style", "theme", "use")
        if current_theme == "azure-dark":
            start_color = (31, 31, 31)
            end_color = (240, 241, 242)
            next_theme = "light"
            next_icon = sun_icon
            label_color = "#000000"
        else:
            start_color = (239, 240, 241)
            end_color = (31, 31, 31)
            next_theme = "dark"
            next_icon = moon_icon
            label_color = "#ffffff"

        # Start a thread to fade the background
        threading.Thread(
            target=fade_background, args=(start_color, end_color), daemon=True
        ).start()

        theme_button.config(image=next_icon)
        theme_button.image = next_icon

        gui.tk.call("set_theme", next_theme)

        style.configure("Key.Label", foreground=label_color)
        detected_key_label.config(style="Key.Label")
        theme_button.config(image=next_icon)
        theme_button.image = next_icon

    # force updates gui tasks; would cause un-transitioned elements within the gui without this
    gui.update_idletasks()

    # creates and sets button element in place;
    theme_button = ttk.Button(gui, image=sun_icon, command=toggle_theme)
    theme_button.image = sun_icon
    x_offset = -10
    y_offset = 10
    theme_button.place(
        relx=1.0, rely=0.0, x=x_offset, y=y_offset, anchor="ne", bordermode="outside"
    )

    # was dealing with some annoying style issues when changing the detected key label text; creates a rectangle to display the key inside of
    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius,
            y1,
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    # styling setup for detected key label text
    style = ttk.Style(gui)
    style = ttk.Style()
    style.configure("TButton", padding=6)
    style.configure(
        "Key.TLabel", font=("Helvetica", 20), background="#d9d9d9", relief="flat"
    )

    # sets up rectangle for canvas
    corner_radius = 30
    key_display_canvas = tk.Canvas(
        gui, width=160, height=30, bg="#d9d9d9", highlightthickness=0
    )
    key_display_canvas.pack(pady=(20, 0))
    rounded_rect = create_rounded_rectangle(
        key_display_canvas, 0, 0, 160, 30, corner_radius, fill="#d9d9d9"
    )

    # sets up label inside of rectangle
    detected_key_label = ttk.Label(key_display_canvas, text="", style="Key.TLabel")
    detected_key_label.place(x=80, y=15, anchor="center")

    # sets application icon
    icon_path = "media/TuneScan.png"
    icon = tk.PhotoImage(file=icon_path)
    gui.tk.call("wm", "iconphoto", gui._w, icon)

    def upload_file():
        # defines allowed audio file types and make a file dialog prompt to get users audio file
        try:
            filetypes = [
                ("WAV Files", "*.wav"),
                ("AIFF Files", "*.aiff"),
                ("MP3 Files", "*.mp3"),
                ("M4A Files", "*.m4a"),
                ("FLAC Files", "*.flac"),
                ("M4A Files", "*.m4a"),
                ("OGG Files", "*.ogg"),
                ("AAC Files", "*.aac"),
            ]
            filepath = filedialog.askopenfilename(filetypes=filetypes)
            print("Selected File:", filepath)

            # our analyze key function will only accept 'mp3' inputs. due to this we must check the file type of the users input, if it isnt mp3, converts it to mp3 then analyzes it.
            file_extension = os.path.splitext(filepath)[1]
            if file_extension != ".mp3":
                mp3_filepath = convert_to_mp3(filepath)
                key = analyze_key(mp3_filepath)
                os.remove(
                    mp3_filepath
                )  # temporary converted file is removed, selected file must stay
            else:
                key = analyze_key(
                    filepath
                )  # file is already mp3, passes it to analyze_key|

            # changes label text to detected key
            detected_key_label.config(text=f"Detected Key: {key}")

        # error handling; ie. user inputs invalid, unsupported or no file at all
        except Exception as e:
            print("An error occurred:", e)
            detected_key_label.config(text="Error in detecting key.")

    def upload_from_youtube():
        # does the analysis for youtube links
        url = youtube_url_entry.get()
        if url and url != "Enter Youtube URL":
            try:
                audio_path = download_youtube_audio(
                    url
                )  # stores mp3 of youtube audio in autio_path
                key = analyze_key(audio_path)  # analyzes and sets label
                detected_key_label.config(text=f"Detected Key: {key}")
                os.remove(audio_path)  # removes temporary youtube mp3; not needed
            # error handling
            except Exception as e:
                print("An error occurred:", e)
                os.remove(audio_path)
                detected_key_label.config(text="Error in detecting key.")
        else:
            detected_key_label.config(text="Please enter a valid YouTube URL.")

    # sets up upload button
    upload_btn = ttk.Button(gui, text="Select File", command=upload_file)
    upload_btn.pack(expand=True)

    # sets up youtube url entry box
    youtube_url_entry = tk.Entry(gui, fg="grey")
    youtube_url_entry.insert(0, "Enter YouTube URL")
    youtube_url_entry.pack(expand=True)

    # sets up submit youtube url button
    youtube_btn = ttk.Button(
        gui, text="Submit YouTube URL", command=upload_from_youtube
    )
    youtube_btn.pack(expand=True)

    # clears placeholder text when entry box is clicked
    def on_entry_click(event):
        if youtube_url_entry.get() == "Enter YouTube URL":
            youtube_url_entry.delete(0, tk.END)
            youtube_url_entry.insert(0, "")
            youtube_url_entry.config(fg="white")

    # inserts placeholder text IF entry is empty on focus out
    def on_focusout(event):
        if youtube_url_entry.get() == "":
            youtube_url_entry.insert(0, "Enter YouTube URL")
            youtube_url_entry.config(fg="grey")

    # executes above functions...
    youtube_url_entry.bind("<FocusIn>", on_entry_click)
    youtube_url_entry.bind("<FocusOut>", on_focusout)

    gui.mainloop()


# handles .x to .mp3 conversion (x for any unsupported file format)
def convert_to_mp3(filepath):
    audio = AudioSegment.from_file(filepath)

    mp3_path = "converted_file.mp3"

    audio.export(mp3_path, format="mp3")

    return mp3_path


# handles yt2mp3 temp file download; stores locally as mp3
def download_youtube_audio(url):
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    destination = "yt_audio.mp3"
    audio.download(filename=destination)
    return destination


# uses algorithmn i found on github to handle scale analysis. i set up the file loading process to handle it easier within the main function
def analyze_key(filepath):
    y, sr = librosa.load(filepath, sr=None)

    fragment = Tonal_Fragment(y, sr)
    fragment.print_key()

    detected_key = fragment.key
    return detected_key


# done!
if __name__ == "__main__":
    main()
