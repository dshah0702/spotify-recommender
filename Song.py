class Song:
    def __init__(self, identity, name, artist, popularity, genre, subgenre):
        self._id = identity
        self._name = name
        self._artist = artist
        self._popularity = popularity
        self._genre = genre
        self._subgenre = subgenre

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

    def __str__(self):
        return f"{self._name} by {self._artist} | Link: http://open.spotify.com/track/{self._id}"