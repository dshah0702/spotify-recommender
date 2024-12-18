import pytest
from Song import Song
from Recommender import Recommender

def test_sonics_recommendation():
    test_songs = [
        Song("1", "Song 1", "Artist A", 90, "Pop", "Electro Pop", 0.8, 0.7, 0.6, 0.5, 140),
        Song("2", "Song 2", "Artist B", 80, "Pop", "Dance Pop", 0.8, 0.7, 0.7, 0.4, 160),
        Song("3", "Song 3", "Artist C", 95, "Pop", "Hyper Pop", 1.0, 1.0, 0.1, 0.4, 220),
        Song("4", "Song 4", "Artist C", 60, "Rock", "Alternative", 0.2, 0.3, 0.2, 0.1, 100),
        Song("5", "Song 5", "Artist C", 40, "Rock", "Hard Rock", 0.7, 0.6, 0.8, 0.4, 130)
    ]

    min_tempo = 100
    max_tempo = 240

    for song in test_songs:
        song.setTempo(min_tempo, max_tempo)

    recommender = Recommender(test_songs)
    recommendations = recommender.sonics_recommendation(test_songs[0])

    # Song 3 is the closest in sonics for danceability, energy, acousticness, liveness, and tempo.
    assert recommendations[0].getId() == "2"
    assert recommendations[1].getId() == "5"

def test_genre_popularity_recommendation():
    test_songs = [
        Song("1", "Song 1", "Artist A", 90, "Pop", "Electro Pop", 0.8, 0.7, 0.6, 0.5, 140),
        Song("2", "Song 2", "Artist B", 80, "Pop", "Dance Pop", 0.8, 0.7, 0.7, 0.4, 160),
        Song("3", "Song 3", "Artist C", 95, "Pop", "Hyper Pop", 1.0, 1.0, 0.1, 0.4, 220),
        Song("4", "Song 4", "Artist C", 60, "Rock", "Alternative", 0.2, 0.3, 0.2, 0.1, 100),
        Song("5", "Song 5", "Artist C", 50, "Rock", "Hard Rock", 0.7, 0.6, 0.8, 0.4, 130)
    ]

    recommender = Recommender(test_songs)
    recommendations = recommender.popularity_genre_recommendation(test_songs[0])

    assert len(recommendations) == 2
    assert recommendations[0].getId() == "3"
    assert recommendations[1].getId() == "2"

def test_hybrid_recommendation_popular():
    test_songs = [
        Song("1", "Song 1", "Artist A", 90, "Pop", "Electro Pop", 0.8, 0.7, 0.6, 0.5, 140),
        Song("2", "Song 2", "Artist B", 80, "Pop", "Dance Pop", 0.8, 0.7, 0.7, 0.4, 160),
        Song("3", "Song 3", "Artist C", 95, "Pop", "Hyper Pop", 1.0, 1.0, 0.1, 0.4, 220),
        Song("4", "Song 4", "Artist C", 60, "Rock", "Alternative", 0.2, 0.3, 0.2, 0.1, 100),
        Song("5", "Song 5", "Artist B", 95, "Pop", "Dance Pop", 0.8, 0.7, 0.7, 0.4, 160),
    ]

    recommender = Recommender(test_songs)
    recommendations1 = recommender.hybrid_recommendation(test_songs[0], 1.0, 0.0)
    recommendations2 = recommender.hybrid_recommendation(test_songs[0], 0.0, 1.0)
    recommendations3 = recommender.hybrid_recommendation(test_songs[0], 0.5, 0.5)

    assert recommendations1[0].getId() == "3"
    assert recommendations2[0].getId() == "2"
    assert recommendations3[0].getId() == "5"

def test_check_song():
    song1 = Song("1", "Song 1", "Artist A", 90, "Pop", "Electro Pop", 0.8, 0.7, 0.6, 0.5, 140)
    song2 = Song("2", "Song 2", "Artist B", 80, "Pop", "Dance Pop", 0.8, 0.7, 0.7, 0.4, 160)

    recommender = Recommender([song1, song2])

    assert recommender.check_song("Song 1") == True
    assert recommender.check_song("Song 3") == False
    assert recommender.check_song("Song 2") == True


