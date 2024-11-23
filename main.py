import pandas as pd
from Song import Song
from Recommender import Recommender

def artist_discography(song_object):
    artist = input("What artist discography would you like to see: ")
    discography = []

    for i in range(len(song_object)):
        if artist == song_object[i].getArtist():
            discography.append(song_object[i])

    return artist, discography

def main():
    spotify_songs = pd.read_csv("spotify_songs.csv")
    spotify_songs = spotify_songs.drop_duplicates("track_id")
    song_object = []

    min_tempo = spotify_songs["tempo"].max()
    max_tempo = spotify_songs["tempo"].min()

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
        song.setTempo(min_tempo, max_tempo)
        song_object.append(song)

    """
    recommender = Recommender(song_object)
    sample_song = recommender.input_song()

    if recommender.check_song(sample_song):
        num = recommender.get_song_num(sample_song)
        popularity = recommender.popularity_genre_recommendation(song_object[num])
        recommender.print_genre_recommendation(song_object[num], popularity)

        sonics = recommender.sonics_recommendation(song_object[num])
        recommender.print_sonics_recommendation(song_object[num], sonics)
    else:
        print(f"{sample_song} does not exist.")
    """

    """
    artist, discography = artist_discography(song_object)
    print(f"{artist}:")
    for song in discography:
        print(song)

    """

if __name__ == "__main__":
    main()