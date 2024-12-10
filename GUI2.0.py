import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from Recommender import Recommender
from Song import Song
import pickle
import spotipy
import webbrowser
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "b3d002f4b4a64da197edd649c1054aa6"
CLIENT_SECRET = "0cdffccbbd5543a6a8531a26c8470d7f"
REDIRECT_URI = "http://localhost:8080/callback"

scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope))

class SpotifyGUI(tk.Tk):
    def __init__(self, recommender):
        super().__init__()
        self.title("Audio Alchemy")
        self.geometry("600x800")  # Set the initial size of the window to 600x800
        self.recommender = recommender
        self.all_songs = list(set([s.getName() for s in recommender._songs if isinstance(s.getName(), str)]))
        self.all_artists = list(set([s.getArtist() for s in recommender._songs if isinstance(s.getArtist(), str)]))

        self.create_widgets()

    def create_widgets(self):
        # Instruction Label
        tk.Label(self, text="Audio Alchemy").grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        tk.Label(self, text="Hello! Please select a song and recommendation type, then click Submit to get "
                            "recommendations.\nFor hybrid recommendation, adjust the sliders to set "
                            "weights.").grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Song Selection
        tk.Label(self, text="Song:").grid(row=2, column=0, padx=10, pady=10)
        self.song_var = tk.StringVar()
        self.song_menu = ttk.Combobox(self, textvariable=self.song_var, values=self.all_songs)
        self.song_menu.grid(row=2, column=1, padx=10, pady=10)
        self.song_menu.bind("<KeyRelease>", self.filter_songs)
        self.song_menu.bind("<<ComboboxSelected>>", self.clear_output)

        # Recommendation Choice
        tk.Label(self, text="Recommendation Choice:").grid(row=3, column=0, padx=10, pady=10)
        self.rec_choice_var = tk.StringVar()
        self.rec_choice_menu = ttk.Combobox(self, textvariable=self.rec_choice_var, values=["Popularity & Genre", "Sonics", "Hybrid"])
        self.rec_choice_menu.grid(row=3, column=1, padx=10, pady=10)
        self.rec_choice_menu.bind("<<ComboboxSelected>>", self.update_widgets)
        self.rec_choice_menu.bind("<<ComboboxSelected>>", self.clear_output)

        # Hybrid Sliders
        self.weighted_popularity_label = tk.Label(self, text="Weighted Popularity (%):")
        self.weighted_popularity_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, resolution=1)
        self.weighted_sonics_label = tk.Label(self, text="Weighted Sonics (%):")
        self.weighted_sonics_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, resolution=1)

        self.weighted_popularity_slider.config(command=self.update_sonics_slider)
        self.weighted_popularity_slider.config(command=self.update_popularity_slider)

        # Submit Button
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Recommendation Output with Scroll Bars
        self.output_frame = tk.Frame(self)
        self.output_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.output_text = tk.Text(self.output_frame, height=6, width=70, wrap="none")
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_scroll_y = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_scroll_y.grid(row=0, column=1, sticky="ns")
        self.output_scroll_x = tk.Scrollbar(self.output_frame, orient="horizontal", command=self.output_text.xview)
        self.output_scroll_x.grid(row=1, column=0, sticky="ew")
        self.output_text.configure(yscrollcommand=self.output_scroll_y.set, xscrollcommand=self.output_scroll_x.set)

        # Artist Selection
        tk.Label(self, text="Artist:").grid(row=9, column=0, padx=10, pady=10)
        self.artist_var = tk.StringVar()
        self.artist_menu = ttk.Combobox(self, textvariable=self.artist_var, values=self.all_artists)
        self.artist_menu.grid(row=9, column=1, padx=10, pady=10)
        self.artist_menu.bind("<KeyRelease>", self.filter_artists)
        self.artist_menu.bind("<<ComboboxSelected>>", self.clear_artist_output)

        # New Submit Button for artist information
        self.artist_submit_button = tk.Button(self, text="Submit", command=self.display_discography)
        self.artist_submit_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        # New Output Box for artist information with Scroll Bars
        self.artist_output_frame = tk.Frame(self)
        self.artist_output_frame.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.artist_output_text = tk.Text(self.artist_output_frame, height=6, width=70, wrap="none")
        self.artist_output_text.grid(row=0, column=0, sticky="nsew")
        self.artist_output_scroll_y = tk.Scrollbar(self.artist_output_frame, orient="vertical",
                                                   command=self.artist_output_text.yview)
        self.artist_output_scroll_y.grid(row=0, column=1, sticky="ns")
        self.artist_output_scroll_x = tk.Scrollbar(self.artist_output_frame, orient="horizontal",
                                                   command=self.artist_output_text.xview)
        self.artist_output_scroll_x.grid(row=1, column=0, sticky="ew")
        self.artist_output_text.configure(yscrollcommand=self.artist_output_scroll_y.set,
                                          xscrollcommand=self.artist_output_scroll_x.set)

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

    def clear_output(self, event=None):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_artist_output(self, event=None):
        self.artist_output_text.config(state=tk.NORMAL)
        self.artist_output_text.delete("1.0", tk.END)
        self.artist_output_text.config(state=tk.DISABLED)

    def update_widgets(self, event):
        choice = self.rec_choice_var.get()
        if choice == "Hybrid":
            self.weighted_popularity_label.grid(row=6, column=0, padx=10, pady=10)
            self.weighted_popularity_slider.grid(row=6, column=1, padx=10, pady=10)
            self.weighted_sonics_label.grid(row=7, column=0, padx=10, pady=10)
            self.weighted_sonics_slider.grid(row=7, column=1, padx=10, pady=10)
        else:
            self.weighted_popularity_label.grid_forget()
            self.weighted_popularity_slider.grid_forget()
            self.weighted_sonics_label.grid_forget()
            self.weighted_sonics_slider.grid_forget()

    def update_sonics_slider(self, val):
        popularity_val = int(val)
        sonics_val = 100 - popularity_val
        self.weighted_sonics_slider.set(sonics_val)

    def update_popularity_slider(self, val):
        sonics_val = int(val)
        popularity_val = 100 - sonics_val
        self.weighted_sonics_slider.set(popularity_val)

    def print_playlist(self, recommendations):
        user_id = sp.current_user()["id"]
        playlist_name = "My Recommended Songs Playlist"
        playlist_id = create_playlist(user_id, playlist_name)

        track_id = []
        for recommendation in recommendations:
            track_id.append(recommendation.getId())
        add_tracks(user_id, playlist_name, playlist_id, track_id)

        playlist = f"Playlist created successfully: https://open.spotify.com/playlist/{playlist_id}"
        return playlist

    def submit(self):
        song_name = self.song_menu.get()
        recommendation_type = self.rec_choice_menu.get()

        song = next((s for s in self.recommender._songs if s.getName() == song_name), None)

        if song:
            self.output_text.delete("1.0", tk.END)
            recommendations = []

            if recommendation_type == "Popularity & Genre":
                recommendations = self.recommender.popularity_genre_recommendation(song)
            elif recommendation_type == "Sonics":
                recommendations = self.recommender.sonics_recommendation(song)
            elif recommendation_type == "Hybrid":
                weighted_popularity = self.weighted_popularity_slider.get() / 100
                weighted_sonics = 1 - weighted_popularity
                recommendations = self.recommender.hybrid_recommendation(song, weighted_popularity, weighted_sonics)

            self.output_text.insert(tk.END, self.format_recommendations(song, recommendations))
            playlist = self.print_playlist(recommendations)
            self.output_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
            self.output_text.insert(tk.END, playlist, "bold")
            self.output_text.config(state=tk.DISABLED)
        else:
            self.output_text.insert(tk.END, "No matching song found.")

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
            self.artist_output_text.insert(tk.END,
                                           f"{artist_name} Discography:\n" + "\n".join(str(s) for s in discography))
        else:
            self.artist_output_text.insert(tk.END, "No artist selected.")

def create_playlist(user_id, playlist_name):
    """
    Creates the playlist for the user
    :param user_id: Takes in the user's id
    :param playlist_name: Takes in the name of the playlist
    :return: Returns the playlist id to the user
    """

    # Finds all the playlists of the user
    playlists = sp.user_playlists(user_id)

    # Checks if the playlist name already exists under the user's profile, if it does, it returns the playlist id
    for playlist in playlists['items']:
        if playlist is not None:
            if playlist['name'].lower() == playlist_name.lower():
                return playlist['id']

    # If the playlist does not exist, it will create the playlist under the user's id
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    return playlist['id']

def check_playlist_exists(user_id, playlist_name):
    """
    Checks if the playlist exists
    :param user_id: Takes in the user id
    :param playlist_name: Takes in the playlist name
    :return: Returns true if the playlist exists, otherwise it returns false
    """
    playlists = sp.user_playlists(user_id)

    for playlist in playlists['items']:
        if playlist['name'].lower() == playlist_name.lower():
            return True

    return False

def add_tracks(user_id, playlist_name, playlist_id, track_id):
    """
    Adds track to the playlist
    :param user_id: Takes in user id
    :param playlist_name: Takes in playlist name
    :param playlist_id: Takes in playlist id
    :param track_id: Takes in track id
    :return: Void function, returns nothing
    """

    # Checks if the playlist exists, and if it does, it clears the playlist
    if check_playlist_exists(user_id, playlist_name):
        print("Playlist exists. Clearing existing tracks and adding new ones.")
        sp.playlist_replace_items(playlist_id, [])

    current_track_id = []

    # Checks if the track is the playlist or not. If it isn't, it adds it to the playlist
    for track in track_id:
        if track not in current_track_id:
            print("Track not in playlist, adding track.")
            sp.playlist_add_items(playlist_id, [track])
            current_track_id.append(track)

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
