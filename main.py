import pandas as pd
from Song import Song

def main():
    spotify_songs = pd.read_csv("spotify_songs.csv")
    song_object = []

    for i in range(len(spotify_songs)):
        identity = spotify_songs.iloc[i, 0]
        name = spotify_songs.iloc[i, 1]
        artist = spotify_songs.iloc[i, 2]
        popularity = spotify_songs.iloc[i, 3]
        genre = spotify_songs.iloc[i, 9]
        subgenre = spotify_songs.iloc[i, 10]

        song_object.append(Song(identity, name, artist, popularity, genre, subgenre))

    for song in song_object:
        print(song)


if __name__ == "__main__":
    main()