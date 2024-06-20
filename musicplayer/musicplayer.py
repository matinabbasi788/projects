import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter.ttk import Progressbar
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import pygame
from PIL import Image, ImageTk
import io
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x700")
        self.root.config(bg="black")

        pygame.mixer.init()

        self.track = tk.StringVar()
        self.artist = tk.StringVar()
        self.album = tk.StringVar()

        self.track_label = tk.Label(root, textvariable=self.track, font=("Helvetica", 20), bg="black", fg="white")
        self.track_label.grid(pady=10)

        self.artist_label = tk.Label(root, textvariable=self.artist, font=("Helvetica", 15), bg="black", fg="white")
        self.artist_label.grid(pady=10)

        self.album_label = tk.Label(root, textvariable=self.album, font=("Helvetica", 15), bg="black", fg="white")
        self.album_label.grid(pady=10)

        self.cover_label = tk.Label(root, bg="black")
        self.cover_label.grid(pady=10)

        self.load_button = tk.Button(root, text="Load Music", command=self.load_music, font=("Helvetica", 15), bg="gray", fg="white")
        self.load_button.grid(pady=10)

        self.controls_frame = tk.Frame(root, bg="black")
        self.controls_frame.grid(pady=10)

        self.play_icon = ImageTk.PhotoImage(Image.open("icons/play.png").resize((50, 50), Image.LANCZOS))
        self.pause_icon = ImageTk.PhotoImage(Image.open("icons/pause.png").resize((50, 50), Image.LANCZOS))
        self.stop_icon = ImageTk.PhotoImage(Image.open("icons/stop.png").resize((50, 50), Image.LANCZOS))
        self.exit_icon = ImageTk.PhotoImage(Image.open("icons/exit.png").resize((50, 50), Image.LANCZOS))

        self.play_button = tk.Button(self.controls_frame, image=self.play_icon, command=self.play_music, bg="black", bd=0)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(self.controls_frame, image=self.pause_icon, command=self.pause_music, bg="black", bd=0)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(self.controls_frame, image=self.stop_icon, command=self.stop_music, bg="black", bd=0)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.exit_button = tk.Button(self.controls_frame, image=self.exit_icon, command=root.quit, bg="black", bd=0)
        self.exit_button.grid(row=0, column=3, padx=5)

        self.progress = Progressbar(root, orient='horizontal', length=350, mode='determinate')
        self.progress.grid(pady=10)
        self.progress.bind("<ButtonRelease-1>", self.seek_music)

        self.lyrics_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("B Nazanin", 12), bg="black", fg="white", insertbackground="white", undo=True)
        self.lyrics_text.grid(pady=10, sticky='')
        self.lyrics_text.place(x=470, y=300, width=300)

        self.lyrics_text.tag_configure("right_align", justify='right')

        self.music_file = None
        self.is_playing = False
        self.total_time = 0

    def load_music(self):
        self.music_file = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if not self.music_file:
            return

        audio = MP3(self.music_file, ID3=EasyID3)

        self.track.set(audio["title"][0] if "title" in audio else "Unknown")
        self.artist.set(audio["artist"][0] if "artist" in audio else "Unknown")
        self.album.set(audio["album"][0] if "album" in audio else "Unknown")

        try:
            tags = ID3(self.music_file)
            for tag in tags.values():
                if tag.FrameID == 'APIC':
                    cover_data = tag.data
                    cover_image = Image.open(io.BytesIO(cover_data))
                    cover_image = cover_image.resize((150, 150), Image.LANCZOS)
                    cover_photo = ImageTk.PhotoImage(cover_image)
                    self.cover_label.config(image=cover_photo)
                    self.cover_label.image = cover_photo
                    break
        except KeyError:
            self.cover_label.config(image='')

        self.progress['value'] = 0
        self.total_time = audio.info.length

        # Load lyrics
        lyrics_file = os.path.splitext(self.music_file)[0] + ".txt"
        if os.path.exists(lyrics_file):
            with open(lyrics_file, "r", encoding="utf-8") as file:
                lyrics = file.read()
                self.lyrics_text.delete(1.0, tk.END)
                self.lyrics_text.insert(tk.END, lyrics)
                self.lyrics_text.tag_add("right_align", "1.0", "end")
        else:
            self.lyrics_text.delete(1.0, tk.END)
            self.lyrics_text.insert(tk.END, "Lyrics not found.")
            self.lyrics_text.tag_add("right_align", "1.0", "end")

    def play_music(self):
        if not self.music_file:
            return

        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play()
        self.is_playing = True
        self.update_progress()

    def pause_music(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.progress['value'] = 0

    def update_progress(self):
        if self.is_playing:
            current_time = pygame.mixer.music.get_pos() / 1000
            self.progress['value'] = (current_time / self.total_time) * 100
            if current_time < self.total_time:
                self.root.after(1000, self.update_progress)
            else:
                self.is_playing = False

    def seek_music(self, event):
        if self.music_file and self.total_time:
            x = event.x
            rel_x = x / self.progress.winfo_width()
            seek_time = rel_x * self.total_time
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(seek_time)
            self.progress['value'] = rel_x * 100
            self.is_playing = True
            self.update_progress()

if __name__ == "__main__":
    # Function to set up the background
    def set_background(root, image_path):
        # Load the image
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        
        # Create a label to hold the image
        background_label = tk.Label(root, image=photo)
        background_label.image = photo  # Keep a reference to the image to prevent garbage collection
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        
    root = tk.Tk()
    set_background(root, "icons/bg.jpg")
    app = MusicPlayer(root)
    root.mainloop()