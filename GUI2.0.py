import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from Recommender import Recommender
from Song import Song
import pickle
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "b3d002f4b4a64da197edd649c1054aa6"
CLIENT_SECRET = "0cdffccbbd5543a6a8531a26c8470d7f"
REDIRECT_URI = "http://localhost:8080/callback"

scope = "playlist-modify-public"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope))


class SpotifyGUI(tk.Tk):
    def __init__(self, recommender):
        super().__init__()
        self.title("Recommender System")
        self.geometry("800x850")  # Set the initial size of the window to 800x850

        self.recommender = recommender
        self.all_songs = list(set([s.getName() for s in recommender._songs if isinstance(s.getName(), str)]))
        self.all_artists = list(set([s.getArtist() for s in recommender._songs if isinstance(s.getArtist(), str)]))

        self.create_widgets()

    def create_widgets(self):
        # Instruction Label
        tk.Label(self, text="Hello! Please select a song and recommendation type, then click Submit to get "
                            "recommendations.\nFor hybrid recommendation, adjust the sliders to set "
                            "weights.").grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Song Selection
        tk.Label(self, text="Song:").grid(row=1, column=0, padx=10, pady=10)
        self.song_var = tk.StringVar()
        self.song_menu = ttk.Combobox(self, textvariable=self.song_var, values=self.all_songs)
        self.song_menu.grid(row=1, column=1, padx=10, pady=10)
        self.song_menu.bind("<KeyRelease>", self.filter_songs)

        # Recommendation Choice
        tk.Label(self, text="Recommendation Choice:").grid(row=2, column=0, padx=10, pady=10)
        self.rec_choice_var = tk.StringVar()
        self.rec_choice_menu = ttk.Combobox(self, textvariable=self.rec_choice_var, values=["Popularity & Genre", "Sonics", "Hybrid"])
        self.rec_choice_menu.grid(row=2, column=1, padx=10, pady=10)
        self.rec_choice_menu.bind("<<ComboboxSelected>>", self.update_widgets)

        # Submit Button
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Recommendation Output with Scroll Bars
        self.output_frame = tk.Frame(self)
        self.output_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.output_text = tk.Text(self.output_frame, height=10, width=70, wrap="none")
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_scroll_y = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_scroll_y.grid(row=0, column=1, sticky="ns")
        self.output_scroll_x = tk.Scrollbar(self.output_frame, orient="horizontal", command=self.output_text.xview)
        self.output_scroll_x.grid(row=1, column=0, sticky="ew")
        self.output_text.configure(yscrollcommand=self.output_scroll_y.set, xscrollcommand=self.output_scroll_x.set)

        # Artist Selection
        tk.Label(self, text="Artist:").grid(row=5, column=0, padx=10, pady=10)
        self.artist_var = tk.StringVar()
        self.artist_menu = ttk.Combobox(self, textvariable=self.artist_var, values=self.all_artists)
        self.artist_menu.grid(row=5, column=1, padx=10, pady=10)
        self.artist_menu.bind("<KeyRelease>", self.filter_artists)

        # New Submit Button for artist information
        self.artist_submit_button = tk.Button(self, text="Submit", command=self.display_discography)
        self.artist_submit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # New Output Box for artist information with Scroll Bars
        self.artist_output_frame = tk.Frame(self)
        self.artist_output_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.artist_output_text = tk.Text(self.artist_output_frame, height=10, width=70, wrap="none")
        self.artist_output_text.grid(row=0, column=0, sticky="nsew")
        self.artist_output_scroll_y = tk.Scrollbar(self.artist_output_frame, orient="vertical", command=self.artist_output_text.yview)
        self.artist_output_scroll_y.grid(row=0, column=1, sticky="ns")
        self.artist_output_scroll_x = tk.Scrollbar(self.artist_output_frame, orient="horizontal", command=self.artist_output_text.xview)
        self.artist_output_scroll_x.grid(row=1, column=0, sticky="ew")
        self.artist_output_text.configure(yscrollcommand=self.artist_output_scroll_y.set, xscrollcommand=self.artist_output_scroll_x.set)

        # Hybrid Sliders
        self.weighted_popularity_label = tk.Label(self, text="Weighted Popularity (%):")
        self.weighted_popularity_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, resolution=1)
        self.weighted_sonics_label = tk.Label(self, text="Weighted Sonics (%):")
        self.weighted_sonics_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, resolution=1)

    def filter_songs(self, event):
        typed = self.song_var.get()
        if typed == "":
            self.song_menu['values'] = self.all_songs
        else:
            filtered_songs = [song for song in self.all_songs if isinstance(song, str) and typed.lower() in song.lower()]
            self.song_menu['values'] = filtered_songs
        self.song_menu.event_generate("<Dropdown>")

    def filter_artists(self, event):
        typed = self.artist_var.get()
        if typed == "":
            self.artist_menu['values'] = self.all_artists
        else:
            filtered_artists = [artist for artist in self.all_artists if isinstance(artist, str) and typed.lower() in artist.lower()]
            self.artist_menu['values'] = filtered_artists
        self.artist_menu.event_generate("<Dropdown>")

    def update_widgets(self, event):
        choice = self.rec_choice_var.get()
        if choice == "Hybrid":
            self.weighted_popularity_label.grid(row=8, column=0, padx=10, pady=10)
            self.weighted_popularity_slider.grid(row=8, column=1, padx=10, pady=10)
            self.weighted_sonics_label.grid(row=9, column=0, padx=10, pady=10)
            self.weighted_sonics_slider.grid(row=9, column=1, padx=10, pady=10)
        else:
            self.weighted_popularity_label.grid_forget()
            self.weighted_popularity_slider.grid_forget()
            self.weighted_sonics_label.grid_forget()
            self.weighted_sonics_slider.grid_forget()

    def submit(self):
        song_name = self.song_menu.get()
        recommendation_type = self.rec_choice_menu.get()

        song = next((s for s in self.recommender._songs if s.getName() == song_name), None)

        if song:
            self.output_text.delete("1.0", tk.END)
            if recommendation_type == "Popularity & Genre":
                recommendations = self.recommender.popularity_genre_recommendation(song)
                self.output_text.insert(tk.END, self.format_recommendations(song, recommendations))
                self.create_playlist(recommendations)
            elif recommendation_type == "Sonics":
                recommendations = self.recommender.sonics_recommendation(song)
                self.output_text.insert(tk.END, self.format_recommendations(song, recommendations))
                self.create_playlist(recommendations)
            elif recommendation_type == "Hybrid":
                weighted_popularity = self.weighted_popularity_slider.get() / 100
                weighted_sonics = 1 - weighted_popularity
                recommendations = self.recommender.hybrid_recommendation(song, weighted_popularity, weighted_sonics)
                self.output_text.insert(tk.END, self.format_recommendations(song, recommendations))
                self.create_playlist(recommendations)
        else:
            self.output_text.insert(tk.END, "No matching song found.")

    def create_playlist(self, recommendations):
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user=user_id, name="Recommended Songs Playlist", public=True)
        track_ids = [s.getId() for s in recommendations]
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_ids)

    def format_recommendations(self, song, recommendations):
        formatted_recs = f"Here are recommendations based on {song.getName()} by {song.getArtist()}:\n"
        for i, s in enumerate(recommendations, 1):
            formatted_recs += f"{i}. {s.getName()} by {s.getArtist()} | Popularity: {s.getPopularity()} | Genre: {s.getGenre()} | Link: http://open.spotify.com/track/{s.getId()}\n"
        return formatted_recs

    def display_discography(self):
        artist_name = self.artist_menu.get()
        if artist_name:
            discography = [s for s in self.recommender._songs if s.getArtist() == artist_name]
            self.artist_output_text.delete("1.0", tk.END)
            self.artist_output_text.insert(tk.END, f"{artist_name} Discography:\n" + "\n".join(str(s) for s in discography))
        else:
            self.artist_output_text.insert(tk.END, "No artist selected.")


def main():
    if not os.path.exists("myData.dat"):
        spotify_songs = pd.read_csv("spotify_songs.csv")
        spotify_songs = spotify_songs.drop_duplicates("track_id")
        spotify_songs = spotify_songs.drop_duplicates("track_name")
        song_object = []

        for i in range(len(spotify_songs)):
            identity = spotify_songs.iloc[i, 0]
            name = spotify_songs.iloc[i, 1]
            artist = spotify_songs.iloc[i, 2]
            popularity = spotify_songs.iloc[i, 3]
            genre = spotify_songs.iloc[i, 9]
            subgenre = spotify_songs.iloc[i, 10]
            danceability = spotify_songs.iloc[i, 11]
            energy = spotify_songs.iloc[i, 12]
            acousticness = spotify_songs.iloc[i, 17]
            liveness = spotify_songs.iloc[i, 19]
            tempo = spotify_songs.iloc[i, 21]
            song = Song(identity, name, artist, popularity, genre, subgenre, danceability, energy, acousticness, liveness, tempo)
            song_object.append(song)

        with open("myData.dat", "wb") as outFile:
            pickle.dump(song_object, outFile)

    with open("myData.dat", "rb") as inFile:
        song_object = pickle.load(inFile)

    recommender = Recommender(song_object)
    app = SpotifyGUI(recommender)
    app.mainloop()

if __name__ == "__main__":
    main()
