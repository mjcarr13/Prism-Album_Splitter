import musicbrainzngs
import time


class MetadataFinder:
    def __init__(self):
        musicbrainzngs.set_useragent(
            "Prism",
            "2.0",
            "michaeljcarr13@gmail.com"
        )

    def get_metadata(self, artist_name, album_name):
        print(f"searching for {album_name} by {artist_name}...")
        #Step 1, find album ID
        album_id = self._get_release_id(artist_name, album_name)
        if not album_id:
            return None

        #Step 2, find the artwork
        artwork_binary = self._get_artwork(album_id)

        # Step 3, get track data
        release_data = self._get_track_data(album_id)

        #Step 4, return the completed metadata dictionary
        return self._build_dictionary(artist_name, album_name, release_data, artwork_binary)

    def _get_release_id(self, artist_name, album_name):
        result = ""
        for attempt in range(5):
            try:
                result = musicbrainzngs.search_releases(artist=artist_name, release=album_name, limit=1)
                if result != None:
                    return result["release-list"][0]["id"]
            # If attempt returns .NetworkError or .ResponseError, wait three seconds before trying again
            except (musicbrainzngs.NetworkError, musicbrainzngs.ResponseError):
                print("Connection denied. Waiting 3 seconds before retrying...")
                time.sleep(3)
        print("Unable to connect to metadata service - please try again after waiting a short while.")
        return None


    def _get_artwork(self, album_id):
        album_artwork = ""
        for attempt in range(5):
            try:
                album_artwork = musicbrainzngs.get_image_front(album_id, size=None)
                print("Album artwork found!")
                return album_artwork
            except Exception:
                print(f"Attempt {attempt + 1} to extract album artwork denied... waiting 3 seconds to try again.")
                time.sleep(3)
        if not album_artwork:
            print("Five attempts to extract album artwork failed... try again when server less busy")
            return None

    def _get_track_data(self, album_id):
        for attempt in range(5):
            try:
                return musicbrainzngs.get_release_by_id(album_id, includes=["recordings", "release-groups"])
            except (musicbrainzngs.NetworkError, musicbrainzngs.ResponseError):
                print(f"Connection error. Retrying... ({attempt + 1}/5)")
                time.sleep(3)
        return None

    def _build_dictionary(self, artist_name, album_name, release_data, artwork_binary):
        release_year = release_data["release"]["release-group"]["first-release-date"][:4]
        tracks = (release_data["release"]["medium-list"][0]["track-list"])
        tracklist = {}
        for track in tracks:
            # extract track title and track length from dictionary data for each track inside list
            track_title = track["recording"]["title"]
            track_length = track["recording"]["length"]
            # add title as new key and duration as new value to the empty "Tracklist" dictionary
            tracklist[track_title] = track_length
        return {
            "Artist": artist_name,
            "Album": album_name,
            "Year": release_year,
            "Tracklist": tracklist,
            "Album Artwork": artwork_binary,
        }







