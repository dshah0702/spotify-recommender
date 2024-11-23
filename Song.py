import numpy as np

class Song:
    def __init__(self, identity, name, artist, popularity, genre, subgenre, danceability, energy, acousticness, liveness, tempo):
        self._id = identity
        self._name = name
        self._artist = artist
        self._popularity = popularity
        self._genre = genre
        self._subgenre = subgenre
        self._danceability = danceability
        self._energy = energy
        self._acousticness = acousticness
        self._liveness = liveness
        self._tempo = tempo

    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def getArtist(self):
        return self._artist

    def getPopularity(self):
        return self._popularity

    def getGenre(self):
        return self._genre

    def getSubgenre(self):
        return self._subgenre

    def getDanceability(self):
        return self._danceability

    def getEnergy(self):
        return self._energy

    def getAcousticness(self):
        return self._acousticness

    def getLiveness(self):
        return self._liveness

    def getTempo(self):
        return self._tempo

    def setTempo(self, min_tempo, max_tempo):
        self._tempo = (self._tempo - min_tempo) / (max_tempo - min_tempo)

    def sonic_features(self):
        return np.array([self._danceability, self._energy, self._acousticness, self._liveness, self._tempo])

    def __str__(self):
        return f"{self._name} by {self._artist} | Link: http://open.spotify.com/track/{self._id}"