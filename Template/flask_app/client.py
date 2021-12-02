import requests


class Song(object):
    def __init__(self, deezer_json):
        self.id = deezer_json["id"]
        self.title = deezer_json["title"]
        self.album = deezer_json["album"]["title"]
        self.artist = deezer_json["artist"]["name"]
        self.duration = deezer_json["duration"]
        self.image = deezer_json["album"]["cover_medium"]

    def __repr__(self):
        return self.title


class DeezerClient(object):
    def __init__(self):
        self.sess = requests.Session()
        self.base_url = f"https://api.deezer.com/search"

    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        search_string = "+".join(search_string.split())
        page = 1

        search_url = f"?q={search_string}"

        resp = self.sess.get(self.base_url + search_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        # if data["Response"] == "False":
        #     raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        search_results_json = data["data"]
        remaining_results = int(data["total"])

        result = []

        ## We may have more results than are first displayed
        while remaining_results > 0:
            for item_json in search_results_json:
                result.append(Song(item_json))
                remaining_results -= len(search_results_json)
            page += 25
            search_url = f"?q={search_string}&index={page}"
            resp = self.sess.get(self.base_url + search_url)
            if resp.status_code != 200:
                break
            search_results_json = resp.json()["data"]

        return result

    def retrieve_song_by_id(self, deezer_id):
        """
        Use to obtain a Movie object representing the movie identified by
        the supplied imdb_id
        """
        track_url = 'https://api.deezer.com/track/' + str(deezer_id)

        resp = self.sess.get(track_url)

        data = resp.json()

        track = Song(data)

        return track


## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client = DeezerClient()

    songs = client.search("location")

    for song in songs:
        print(song.artist)

    print(client.retrieve_song_by_id(120352046))