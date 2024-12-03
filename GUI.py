import tkinter as tk
from tkinter import ttk
import pandas as pd
from Recommender import Recommender
from Song import Song


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

        self.danceability_label = tk.Label(self, text="Danceability:")
        self.danceability_label.grid(row=3, column=0, padx=10, pady=5)
        self.danceability_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL)
        self.danceability_slider.grid(row=3, column=1, padx=10, pady=5)

        self.energy_label = tk.Label(self, text="Energy:")
        self.energy_label.grid(row=4, column=0, padx=10, pady=5)
        self.energy_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL)
        self.energy_slider.grid(row=4, column=1, padx=10, pady=5)

        self.rating_label = tk.Label(self, text="Rating:")
        self.rating_label.grid(row=5, column=0, padx=10, pady=5)
        self.rating_stars = ttk.Combobox(self, values=[1, 2, 3, 4, 5])
        self.rating_stars.grid(row=5, column=1, padx=10, pady=5)

        self.recommendation_label = tk.Label(self, text="Recommendation Type:")
        self.recommendation_label.grid(row=6, column=0, padx=10, pady=5)
        self.recommendation_dropdown = ttk.Combobox(self, values=["Genre", "Popularity", "Danceability"])
        self.recommendation_dropdown.grid(row=6, column=1, padx=10, pady=5)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.recommendations_text = tk.Text(self, height=10, width=70)
        self.recommendations_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

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
        danceability = self.danceability_slider.get()
        energy = self.energy_slider.get()
        rating = self.rating_stars.get()
        recommendation_type = self.recommendation_dropdown.get()

        print(f"Artist: {artist_name}, Genre: {genre}, Danceability: {danceability}, Energy: {energy}, Rating: {rating}, Recommendation Type: {recommendation_type}")

        song = next((s for s in self.recommender._songs if s.getArtist() == artist_name), None)

        if song:
            print(f"Song found: {song}")
            self.recommendations_text.delete("1.0", tk.END)
            if recommendation_type == "Genre":
                recommendations = self.recommender.popularity_genre_recommendation(song)
                print(f"Recommendations: {recommendations}")
                self.recommendations_text.insert(tk.END, self.recommender.print_genre_recommendation(song, recommendations))
            elif recommendation_type == "Danceability":
                recommendations = self.recommender.sonics_recommendation(song)
                print(f"Recommendations: {recommendations}")
                self.recommendations_text.insert(tk.END, self.recommender.print_sonics_recommendation(song, recommendations))
        else:
            print("No matching song found.")

    def display_discography(self, event):
        artist_name = self.artist_dropdown.get()
        discography = [s for s in self.recommender._songs if s.getArtist() == artist_name]
        self.recommendations_text.delete("1.0", tk.END)
        self.recommendations_text.insert(tk.END, f"{artist_name} Discography:\n" + "\n".join(str(s) for s in discography))


if __name__ == "__main__":
    spotify_songs = pd.read_csv("spotify_songs.csv")
    spotify_songs = spotify_songs.drop_duplicates("track_id")
    song_object = []

    min_tempo = spotify_songs["tempo"].min()
    max_tempo = spotify_songs["tempo"].max()

    for i in range(len(spotify_songs)):
        identity = spotify_songs.iloc[i, 0]
        name = spotify_songs.iloc[i, 1]
        artist = spotify_songs.iloc[i, 2]
        popularity = spotify_songs.iloc[i, 3]
        genre = spotify_songs.iloc[i, 4]
        subgenre = spotify_songs.iloc[i, 5]
        danceability = spotify_songs.iloc[i, 6]
        energy = spotify_songs.iloc[i, 7]
        acousticness = spotify_songs.iloc[i, 8]
        liveness = spotify_songs.iloc[i, 9]
        tempo = spotify_songs.iloc[i, 10]

        song = Song(identity, name, artist, popularity, genre, subgenre, danceability, energy, acousticness, liveness, tempo)
        song.setTempo(min_tempo, max_tempo)
        song_object.append(song)

    recommender = Recommender(song_object)
    app = SpotifyGUI(recommender)
    app.mainloop()
