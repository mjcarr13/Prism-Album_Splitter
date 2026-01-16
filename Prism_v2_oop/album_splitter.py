import os
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

class AlbumSplitter():
    def __init__(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.file_destination = desktop_path


    def album_splitter(self, audio_filepath, metadata):
        #1 load audio as audiosegment
        full_album_audio = AudioSegment.from_file(audio_filepath)

        #2 create output folder using worker method
        album_folder = self._create_folder(metadata["Album"])

        #3 prepare the loop variables
        tracks = list(metadata["Tracklist"].keys())
        durations = list(metadata["Tracklist"].values())
        start_time = 0

        #4 begin slicing loop
        for i, track_title in enumerate(tracks):
            current_track_length = int(durations[i])
            end_time = start_time + current_track_length

            #5 use worker method to sanitise filename and create final filepath
            track_filename = self._get_safe_filename(i + 1, track_title)
            track_filepath = os.path.join(album_folder, track_filename)

            #6 begin slicing user worker method, passing in all needed info
            self._export_track(
                audio_segment=full_album_audio,
                start=start_time,
                end=end_time,
                output_path=track_filepath,
                tags={
                    "artist": metadata["Artist"],
                    "album": metadata["Album"],
                    "title": track_title,  # Keep original title for tags
                    "track": str(i + 1),
                    "date": metadata["Year"]
                }
            )
            #7 update the start time before the next loop begins
            start_time += current_track_length

            #8 If artwork exists, add to track using worker method
            if metadata["Album Artwork"]:
                self._add_artwork(track_filepath, metadata["Album Artwork"])
            print(f"Export of '{track_title}' complete.")

        print(f"Export of {metadata['Album']} to the Desktop complete.")


    def _create_folder(self, album_name):
        folder_path = os.path.join(self.file_destination, album_name)
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            print("This album already exists on your desktop.")
            pass
        return folder_path

    def _get_safe_filename(self, track_number, track_title):
        safe_title = track_title.replace("/", "-").replace(":", "-").replace("?", "")
        return f"{track_number}. {safe_title}.mp3"

    def _export_track(self, audio_segment, start, end, output_path, tags):
        track_to_export = audio_segment[start:end]
        track_to_export.export(output_path, format="mp3", tags=tags)

    def _add_artwork(self, filepath, artwork):
        try:
            audio = MP3(filepath, ID3 = ID3)
            try:
                audio.add_tags()
            except error:
                pass
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc=u'Cover',
                    data=artwork
                )
            )
            audio.save()
        except Exception:
            print(f"Warning: Could not add artwork to {filepath}")

