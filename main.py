from app import BumpMappingApp

import os
os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"

if __name__ == "__main__":
    app = BumpMappingApp()
    app.run()