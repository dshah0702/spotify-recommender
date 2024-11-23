from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, songs):
        self._songs = songs

    def input_song(self):
        song = input("What type of song are you trying to hear more of: ")
        return song

    def check_song(self, song):
        for s in self._songs:
            if song == s.getName():
                return True

    def get_song_num(self, song):
        for i in range(len(self._songs)):
            if song == self._songs[i].getName():
                return i

    def popularity_genre_recommendation(self, song, num_rec = 5):
        similar_songs = []

        for s in self._songs:
            if s.getGenre() == song.getGenre() and s.getId() != song.getId():
                similar_songs.append(s)

        similar_songs.sort(key=lambda s: abs(s.getPopularity() - song.getPopularity()))

        return similar_songs[:num_rec]

    def print_genre_recommendation(self, song, recomend_songs):
        print(f"Here are some recommendations based on popularity and genre for: {song.getName()}")
        for s in recomend_songs:
            print(f"{s.getName()} by {s.getArtist()}")

    def sonics_recommendation(self, song, num_rec = 5):
        input_features = song.sonic_features().reshape(1,-1)
        recommended = []

        for s in self._songs:
            if s.getId() != song.getId():
                rec = cosine_similarity(input_features, s.sonic_features().reshape(1,-1))[0,0]
                recommended.append((s, rec))

        recommended.sort(key=lambda x: x[1], reverse=True)

        return [rec[0] for rec in recommended[:num_rec]]

    def print_sonics_recommendation(self, song, recomend_songs):
        print(f"Here are some recommendations based on the sonics of the song: {song.getName()} by {song.getArtist()} | Danceability: {song.getDanceability():.2f} | Energy: {song.getEnergy():.2f} | Tempo: {song.getTempo():.2f}")
        for s in recomend_songs:
            print(f"{s.getName()} by {s.getArtist()} | Danceability: {s.getDanceability():.2f} | Energy: {s.getEnergy():.2f} | Tempo: {s.getTempo():.2f}")