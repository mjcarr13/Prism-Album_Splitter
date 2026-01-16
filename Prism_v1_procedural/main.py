import os
import musicbrainzngs
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import time

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

#Function to create dictionary containing artist name, album name, tracks and durations, and artwork to add artwork to mop3
def get_album_metadata(artist_name, album_name):
    #pass useragent info to musicbrainz
    musicbrainzngs.set_useragent(
        "Prism",
        "0.2",
        "michaeljcarr13@gmail.com",
    )
    #take artist and album info from user as inputs, converting to title case

    #Attempt no more than 5 times to search musicbrainzngs for the artist and album info, saving as variable
    result = None
    for attempt in range(5):
        try:
            result = musicbrainzngs.search_releases(artist=artist_name, release=album_name, limit=1)
            break
        #If attempt returns .NetworkError or .ResponseError, wait three seconds before trying again
        except musicbrainzngs.NetworkError:
            print("Connection denied. Waiting 3 seconds before retrying...")
            time.sleep(3)
        except musicbrainzngs.ResponseError:
            print("Connection error accessing metadata. Waiting 3 seconds...")
            time.sleep(3)

    #If after 5 results our variable remains empty, give up to avoid being banned from server
    if result is None:
        print("Unable to connect to metadata service - please try again after waiting a short while.")
        return None

    #Assuming successful, extract album ID code from resulting data
    album_id = result["release-list"][0]["id"]
    #create empty album artwork variable so we can check after loop if it remains empty
    album_artwork = None
    #Use this ID code to attempt, no more than 5 times, to request album artwork via musicbrainzngs.get_image_front
    for attempt in range(5):
        try:
            #size=None requests album artwork in the largest maximum size
            album_artwork = musicbrainzngs.get_image_front(album_id, size=None)
            print("Album artwork found!")
            break
        except Exception:
            print(f"Attempt {attempt+1} to extract album artwork denied... waiting 5 seconds to try again.")
            time.sleep(5)
    #Check to see if album artwork has failed to be saved and print message accordingly
    if not album_artwork:
        print("Five attempts to extract album artwork failed... try again when server less busy")

    #get album information for specific release via musicbrainzngs.get_release_by_id
    new_result = musicbrainzngs.get_release_by_id(album_id, includes=["recordings", "release-groups"])
    #save track list for album as new list of dictionaries
    tracks = (new_result["release"]["medium-list"][0]["track-list"])
    #create metadata dictionary for album information, passing in artist and album name
    album_metadata = {
        "Artist": artist_name,
        "Album": album_name,
        #retreieve release data, taking only first four characters (the year)
        "Year": new_result["release"]["release-group"]["first-release-date"][:4],
        #create empty dictionary to store the track names and durations
        "Tracklist": {},
        #store album artwork within dictionary
        "Album Artwork": album_artwork,
    }
    #begin for loop which iterates through tracks list
    for track in tracks:
        #extract track title and track length from dictionary data for each track inside list
        track_title = track["recording"]["title"]
        track_length = track["recording"]["length"]
        #add title as new key and duration as new value to the empty "Tracklist" dictionary
        album_metadata["Tracklist"][track_title] = track_length
    return album_metadata


#ABBEY ROAD FILEPATH =  /Users/michaelcarr/Desktop/thebeatles/BEATLES/ABR.WAV
#PLEASE PLEASE ME FILEPATH =  /Users/michaelcarr/Desktop/thebeatles/BEATLES/PPM.wav
#Dark Side of the Moon FILEPATH = /Users/michaelcarr/Movies/4K Video Downloader+/Pink Floyd - The Dark Side Of The Moon (50th Anniversary) [2023 Remaster] {Full Album}.m4a

#Function to splice tracks, outputting them with correct file names
def splicer(album_filepath, album_metadata):
    tracks = list(album_metadata["Tracklist"].keys())
    durations = list(album_metadata["Tracklist"].values())
    start_time = 0
    try:
        os.mkdir(f"{DESKTOP_PATH}/{album_metadata['Album']}")
    except FileExistsError:
        print("This album already exists on your desktop.")

    print("Loading your album...")
    album_metadata["album"] = AudioSegment.from_file(album_filepath)
    for i, track_title in enumerate(tracks):
        current_track_length = int(durations[i])
        end_time = start_time + current_track_length
        #sanitise the track titles before dealing with filepaths
        title = track_title.replace("/", "-").replace(":", "-").replace("?", "")
        album_metadata["album"][start_time:end_time].export(
            f"{DESKTOP_PATH}/{album_metadata['Album']}/{i+1}. {title}.mp3",
            format="mp3",
            tags={
                "artist": album_metadata["Artist"],
                "album": album_metadata["Album"],
                "title": f"{title}",
                "track": f"{i+1}",
                "date": album_metadata["Year"],
            }
        )
        #Add album artwork to exported mp3s
        if album_metadata["Album Artwork"]:
            track = MP3(f"{DESKTOP_PATH}/{album_metadata['Album']}/{i+1}. {title}.mp3", ID3=ID3)
            try:
                track.add_tags()
            except error:
                pass
            track.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc=u'Cover',
                    data=album_metadata["Album Artwork"]
                )
            )
            track.save()

        start_time += current_track_length
        print(f"Export of '{tracks[i]}' complete")
    print(f"Export of {album_metadata['Album']} to the Desktop complete.")


###### GUI

from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox



#GUI CONSTANTS
GREY = "#CDD5D8"
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 450
ARTIST_PLACEHOLDER = "Enter artist name..."
ALBUM_PLACEHOLDER = "Enter album name..."
PERMITTED_FILES = (".MP3", ".WAV", ".AAC", ".FLAC", ".M4A", ".OGG")
APP_FONT = ("Avenir", 13)

#empty_variables
filepath = ""
artist = ""
album = ""

#WINDOW SETUP
window = Tk()
window.title("Prism")
window.configure(bg=GREY)

#WINDOW POSITIONING
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - WINDOW_WIDTH) / 2)
y_position = int((screen_height - WINDOW_HEIGHT) / 3)
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_position}+{y_position}")
window.resizable(False, False)

#App Icon
app_icon = PhotoImage(file="prism_app_icon.png")
window.iconphoto(True, app_icon)

#CANVAS SETUP
canvas = Canvas(width=300, height = 300, bg=GREY, highlightthickness=0)
prism_img = PhotoImage(file="Prism_Logo_Small.png")
canvas.create_image(150,150,image=prism_img)
canvas.grid(column =0, row = 0)


#Function to clear/reinsert placeholder text in the boxes
def on_focus_in(event, entry_widget, default_text):
    # If the text currently in the box matches the default placeholder...
    if entry_widget.get() == default_text:
        # ...delete everything from index 0 to the end...
        entry_widget.delete(0, "end")
        # ...and change the text color to black (so user input looks normal)
        entry_widget.config(fg='black')
        entry_widget.focus_set()

# 2. Function to handle clicking OUTSIDE the box
def on_focus_out(event, entry_widget, default_text):
    # If the box is completely empty...
    if entry_widget.get() == "":
        # ...insert the default text back at index 0...
        entry_widget.insert(0, default_text)
        # ...and change the color back to grey to look like a placeholder
        entry_widget.config(fg='grey')

#INPUT AND BUTTON SETUP

def get_file():
    global filepath
    filepath = fd.askopenfilename()
    if not filepath:
        return
    if not filepath.upper().endswith(PERMITTED_FILES):
        messagebox.showinfo(title="Prism", message="Invalid File, Please select a valid audio file (MP3, WAV, FLAC, etc).")
        filepath = ""
    else:
        filename = os.path.basename(filepath)
        if len(filename) > 20:
            display_filename = filename[:17] + "..."
        else:
            display_filename = filename
        file_button.config(text=f"{display_filename} Selected")
    print(filepath)

def start_export():
    global artist
    global album
    global filepath
    artist = artist_box.get().title()
    album = album_box.get().title()
    if artist == "" or album == "":
        messagebox.showinfo(title="Prism", message="Please don't leave any fields empty!")
        return
    elif filepath == "":
        messagebox.showinfo(title="Prism", message="Please select a file")
        return
    metadata = get_album_metadata(artist_name=artist, album_name=album)
    splicer(album_metadata=metadata, album_filepath=filepath)
    messagebox.showinfo(title="Prism", message="Export complete!")



#FILE SECTION
file_button = Button(width=23, bg="white", highlightbackground = GREY, text="Select Audio File", command=get_file,font=APP_FONT)
file_button.grid(column = 0, row= 1, pady=2)

#ARTIST ENTRY
artist_box = Entry(width=25, fg="grey", bg="white", highlightbackground = GREY, insertbackground='black',font=APP_FONT)
artist_box.insert(0, ARTIST_PLACEHOLDER)
artist_box.bind('<FocusIn>', lambda event: on_focus_in(event, artist_box, default_text=ARTIST_PLACEHOLDER))
artist_box.bind('<FocusOut>', lambda event: on_focus_out(event, artist_box, default_text=ARTIST_PLACEHOLDER))
artist_box.grid(column=0, row=2, pady=2)

#ALBUM ENTRY
album_box = Entry(width=25, fg="grey", bg="white", highlightbackground=GREY, insertbackground='black',font=APP_FONT)
# Use the variable
album_box.insert(0, ALBUM_PLACEHOLDER)
album_box.bind('<FocusIn>', lambda event: on_focus_in(event, album_box, ALBUM_PLACEHOLDER))
album_box.bind('<FocusOut>', lambda event: on_focus_out(event, album_box, ALBUM_PLACEHOLDER))
album_box.grid(column=0, row=3, pady=2)

#START BUTTON
start_button = Button(width=23, bg=GREY, highlightbackground = GREY, text="Start", command=start_export,font=APP_FONT)
start_button.grid(column = 0, row= 4, pady=(0, 10))


window.bind('<Return>', lambda event: start_export())

#window loop
window.mainloop()