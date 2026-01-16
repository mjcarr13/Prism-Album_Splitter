from prism import Prism

"""
so as it turns out I need to use this weird looking code below to ensure the code is executed when the file
runs as a script, rather than when it's being imported as a module (which as it turns out will always
trigger a function. Because the gui uses mainloop() we're at risk of being stuck in an infinite loop until
the window is closed otherwise. 

Janky looking thing, but hey, it works. 
"""

if __name__ == "__main__":
    app = Prism()