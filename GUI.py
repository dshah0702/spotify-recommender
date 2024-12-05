import os

os.environ['TCL_LIBRARY'] = 'C:/Users/User/AppData/Local/Programs/Python/Python313/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'C:/Users/User/AppData/Local/Programs/Python/Python313/tcl/tk8.6'

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
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope))

class SpotifyGUI(tk.Tk):
    def __init__(self, recommender):
        super().__init__()
        self.title("Spotify Song Recommender")

        self.recommender = recommender
        self.all_artists = list(set([s.getArtist() for s in recommender._songs if isinstance(s.getArtist(), str)]))

        self.artist_label = tk.Label(self, text="Artist:")
        self.artist_label.grid(row=1, column=0, padx=10, pady=5)

        self.artist_dropdown = ttk.Combobox(self, values=self.all_artists)
        self.artist_dropdown.grid(row=1, column=1, padx=10, pady=5)
        self.artist_dropdown.bind("<<ComboboxSelected>>", self.display_discography)
        self.artist_dropdown.bind("<KeyRelease>", self.filter_artists)

        self.genre_label = tk.Label(self, text="Genre:")
        self.genre_label.grid(row=2, column=0, padx=10, pady=5)
        self.genre_dropdown = ttk.Combobox(self, values=list(set([s.getGenre() for s in recommender._songs])))
        self.genre_dropdown.grid(row=2, column=1, padx=10, pady=5)

        self.rating_label = tk.Label(self, text="Rating:")
        self.rating_label.grid(row=3, column=0, padx=10, pady=5)
        self.rating_stars = ttk.Combobox(self, values=[1, 2, 3, 4, 5])
        self.rating_stars.grid(row=3, column=1, padx=10, pady=5)

        self.recommendation_label = tk.Label(self, text="Recommendation Type:")
        self.recommendation_label.grid(row=4, column=0, padx=10, pady=5)
        self.recommendation_dropdown = ttk.Combobox(self, values=["Genre", "Popularity"])
        self.recommendation_dropdown.grid(row=4, column=1, padx=10, pady=5)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.recommendations_text = tk.Text(self, height=10, width=70)
        self.recommendations_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def filter_artists(self, event):
        typed = self.artist_dropdown.get()
        if typed == "":
            self.artist_dropdown['values'] = self.all_artists
        else:
            filtered_artists = [artist for artist in self.all_artists if isinstance(artist, str) and typed.lower() in artist.lower()]
            self.artist_dropdown['values'] = filtered_artists

        self.artist_dropdown.event_generate("<Down>")

    def submit(self):
        artist_name = self.artist_dropdown.get()
        genre = self.genre_dropdown.get()
        rating = self.rating_stars.get()
        recommendation_type = self.recommendation_dropdown.get()

        print(f"Artist: {artist_name}, Genre: {genre}, Rating: {rating}, Recommendation Type: {recommendation_type}")

        song = next((s for s in self.recommender._songs if s.getArtist() == artist_name), None)

        if song:
            print(f"Song found: {song}")
            self.recommendations_text.delete("1.0", tk.END)
            if recommendation_type == "Genre":
                recommendations = self.recommender.popularity_genre_recommendation(song)
                print(f"Recommendations: {recommendations}")
                self.recommendations_text.insert(tk.END, self.recommender.print_genre_recommendation(song, recommendations))
        else:
            print("No matching song found.")

    def display_discography(self, event):
        artist_name = self.artist_dropdown.get()
        discography = [s for s in self.recommender._songs if s.getArtist() == artist_name]
        self.recommendations_text.delete("1.0", tk.END)
        self.recommendations_text.insert(tk.END, f"{artist_name} Discography:\n" + "\n".join(str(s) for s in discography))

def artist_discography(song_object):
    artist = input("What artist discography would you like to see: ")
    discography = []

    for i in range(len(song_object)):
        if artist == song_object[i].getArtist():
            discography.append(song_object[i])

    return artist, discography

def create_playlist(user_id, playlist_name):
    playlists = sp.user_playlists(user_id)

    for playlist in playlists['items']:
        if playlist['name'].lower() == playlist_name.lower():
            return playlist['id']

    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    return playlist['id']

def check_playlist_exists(user_id, playlist_name):
    playlists = sp.user_playlists(user_id)

    for playlist in playlists['items']:
        if playlist['name'].lower() == playlist_name.lower():
            return True

    return False

def add_tracks(user_id, playlist_name, playlist_id, track_id):
    if check_playlist_exists(user_id, playlist_name):
        print("Playlist exists. Clearing existing tracks and adding new ones.")
        sp.playlist_replace_items(playlist_id, [])

    current_track_id = []

    for track in track_id:
        if track not in current_track_id:
            print("Track not in playlist, adding track.")
            sp.playlist_add_items(playlist_id, [track])
            current_track_id.append(track)

if __name__ == "__main__":
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

            song = Song(identity, name, artist, popularity, genre, subgenre, danceability, energy, acousticness,
                        liveness, tempo)
            # song.setTempo(min_tempo, max_tempo)
            song_object.append(song)

        outFile = open("myData.dat", "wb")
        pickle.dump(song_object, outFile)
        outFile.close()

    inFile = open("myData.dat", "rb")
    song_object = pickle.load(inFile)
    inFile.close()

    recommender = Recommender(song_object)
    app = SpotifyGUI(recommender)
    app.mainloop()

    sample_song = recommender.input_song()
    track_id = []

    print("Recommendation Systems")
    print("1. Popularity & Genre")
    print("2. Sonics")
    print("3. Hybrid between Popularity and Sonics")
    choice = int(input("Which type of recommendation system do you choose: "))

    if recommender.check_song(sample_song):
        num = recommender.get_song_num(sample_song)

        if choice == 1:
            # Recommender for popularity & genre recommendation
            popularity = recommender.popularity_genre_recommendation(song_object[num])
            recommender.print_genre_recommendation(song_object[num], popularity)

            for s in popularity:
                track_id.append(s.getId())

        elif choice == 2:
            # Recommender for sonics recommendation
            sonics = recommender.sonics_recommendation(song_object[num])
            recommender.print_sonics_recommendation(song_object[num], sonics)

            for s in sonics:
                track_id.append(s.getId())

        elif choice == 3:
            # Recommender for hybrid recommendation
            pop_score = float(
                input("How much of the recommendation do you want to be based on popularity of the song (0.0-1.0): "))
            sonics_score = 1 - pop_score
            hybrid = recommender.hybrid_recommendation(song_object[num], pop_score, sonics_score)
            recommender.print_hybrid_recommendation(song_object[num], hybrid, pop_score, sonics_score)

            for s in hybrid:
                track_id.append(s.getId())
    else:
        print(f"{sample_song} does not exist.")

    # Creation of spotify playlist
    user_id = sp.current_user()["id"]
    playlist_name = "My Recommended Songs Playlist"
    playlist_id = create_playlist(user_id, playlist_name)
    add_tracks(user_id, playlist_name, playlist_id, track_id)
    print(f"Playlist created successfully: https://open.spotify.com/playlist/{playlist_id}")

    # Display of artist discography (artist name input)
    artist, discography = artist_discography(song_object)
    print(f"{artist}:")
    for song in discography:
        print(song)
