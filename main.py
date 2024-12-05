import os
import pickle
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from Song import Song
from Recommender import Recommender

CLIENT_ID = "b3d002f4b4a64da197edd649c1054aa6"
CLIENT_SECRET = "0cdffccbbd5543a6a8531a26c8470d7f"
REDIRECT_URI = "http://localhost:8080/callback"

scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope))

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
    sample_song = recommender.input_song()
    track_id = []

    if recommender.check_song(sample_song):
        num = recommender.get_song_num(sample_song)

        popularity = recommender.popularity_genre_recommendation(song_object[num])
        recommender.print_genre_recommendation(song_object[num], popularity)

        for s in popularity:
            track_id.append(s.getId())

        sonics = recommender.sonics_recommendation(song_object[num])
        recommender.print_sonics_recommendation(song_object[num], sonics)

        for s in sonics:
            track_id.append(s.getId())

        pop_score = float(input("How much of the recommendation do you want to be based on popularity of the song (0.0-1.0): "))
        sonics_score = 1 - pop_score
        hybrid = recommender.hybrid_recommendation(song_object[num], pop_score, sonics_score)
        recommender.print_hybrid_recommendation(song_object[num], hybrid, pop_score, sonics_score)

        for s in hybrid:
            track_id.append(s.getId())

    else:
        print(f"{sample_song} does not exist.")

    user_id = sp.current_user()["id"]
    playlist_name = "My Recommended Songs Playlist"
    playlist_id = create_playlist(user_id, playlist_name)
    add_tracks(user_id, playlist_name, playlist_id, track_id)
    print(f"Playlist created successfully: https://open.spotify.com/playlist/{playlist_id}")

    artist, discography = artist_discography(song_object)
    print(f"{artist}:")
    for song in discography:
        print(song)

if __name__ == "__main__":
    main()