from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from metadata_finder import MetadataFinder
from album_splitter import AlbumSplitter
import os

class Prism:
    def __init__(self):
        #GUI CONSTANTS
        self.GREY = "#CDD5D8"
        self.APP_FONT = ("Avenir", 13)
        self.PERMITTED_FILES = (".MP3", ".WAV", ".AAC", ".FLAC", ".M4A", ".OGG")

        #GUI empty variables for later
        self.filepath = ""

        #import and save metadata dinfer and splicer to be called later
        self.finder = MetadataFinder()
        self.splitter = AlbumSplitter()

        #window setup
        self.window = Tk()
        self.window.title("Prism")
        self.window.configure(bg=self.GREY)
        self.app_icon = PhotoImage(file="prism_app_icon.png")
        self.window.iconphoto(True, self.app_icon)

        #Centre the window (thank
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 300
        window_height = 450
        x_pos = int((screen_width - window_width) / 2)
        y_pos = int((screen_height - window_height) / 3)
        self.window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.window.resizable(False, False)

        #build UI using worker method
        self._setup_gui()

        #intitate loop
        self.window.mainloop()

    def _setup_gui(self):
        #add logo to top using canvas
        canvas = Canvas(self.window, width=300, height=300, bg=self.GREY, highlightthickness=0) #why inputting self.window into this?
        self.prism_img = PhotoImage(file="Prism_Logo_Small.png")
        canvas.create_image(150, 150, image=self.prism_img)
        canvas.grid(column=0, row=0)

        #Add file button, link command
        self.file_button = Button(
            self.window,
            width = 23,
            bg = "white",
            highlightbackground=self.GREY,
            text = "Select Audio File",
            font = self.APP_FONT,
            command = self.select_file,
            )
        #set location on grid
        self.file_button.grid(column=0, row=1, pady=2)

        #add artist entry box
        self.artist_entry = Entry(
            self.window,
            width=25,
            fg="grey",
            bg="white",
            highlightbackground=self.GREY,
            font=self.APP_FONT,
            insertbackground='black',

        )
        self.artist_entry.insert(0, "Enter artist name...")
        #binding events for text box
        self.artist_entry.bind('<FocusIn>', lambda event: self.on_focus_in(self.artist_entry, "Enter artist name..."))
        self.artist_entry.bind('<FocusOut>', lambda event: self.on_focus_out(self.artist_entry, "Enter artist name..."))
        # set location on grid
        self.artist_entry.grid(column=0, row=2, pady=2)

        #add album entry box
        self.album_entry = Entry(
            self.window,
            width=25,
            fg="grey",
            bg="white",
            highlightbackground=self.GREY,
            font=self.APP_FONT,
            insertbackground = 'black',
        )
        self.album_entry.insert(0, "Enter album name...")
        #binding events for text box
        self.album_entry.bind('<FocusIn>', lambda e: self.on_focus_in(self.album_entry, "Enter album name..."))
        self.album_entry.bind('<FocusOut>', lambda e: self.on_focus_out(self.album_entry, "Enter album name..."))
        # set location on grid
        self.album_entry.grid(column=0, row=3, pady=2)

        #add start button
        start_button = Button(
            self.window,
            width=23,
            text="Start",
            highlightbackground=self.GREY,
            font=self.APP_FONT,
            command=self.run_prism
        )
        # set location on grid
        start_button.grid(column=0, row=4, pady=(0, 10))

# methods to clear/reinsert placeholder text in the boxes
    def on_focus_in(self, entry_widget, default_text):
        if entry_widget.get() == default_text:
            entry_widget.delete(0, "end")
            entry_widget.config(fg='black')
            entry_widget.focus_set()

    def on_focus_out(self, entry_widget, default_text):
        if entry_widget.get() == "":
            entry_widget.insert(0, default_text)
            entry_widget.config(fg='grey')

    #Button commands

    def select_file(self):
        filename = fd.askopenfilename()
        if not filename:
            return
        if not filename.upper().endswith(self.PERMITTED_FILES):
            messagebox.showinfo(title="Prism", message="Invalid File. Please select MP3, WAV, FLAC, etc.")
            return
        self.filepath = filename
        print(f"File selected: {self.filepath}")
        #update the button text with the name of the file,
        display_name = os.path.basename(filename)
        if len(filename) > 20:
            display_filename = filename[:17] + "..."
        self.file_button.config(text=f"{display_name} Selected")


    def run_prism(self):
        #get inputs from boxes
        artist = self.artist_entry.get().title()
        album = self.album_entry.get().title()
        #check that both boxes have been filled and a file has been selected
        if artist == "" or album == "":
            messagebox.showinfo(title="Prism", message="Please don't leave any fields empty!")
            return
        elif self.filepath == "":
            messagebox.showinfo(title="Prism", message="Please select a file")
            return

        #get metadata
        album_metadata = self.finder.get_metadata(artist, album)
        self.splitter.album_splitter(audio_filepath=self.filepath, metadata=album_metadata)
















