from file import Album
import sys

if __name__ == "__main__":
    path_to_folder = sys.argv[1]
    cover_path = None

    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ("--cover", "-c") and i + 1 < len(sys.argv):
            cover_path = sys.argv[i + 1]
            break


    try:
        print()
        
        album = Album(path_to_folder)
        if cover_path is not None:
            album.set_cover(cover_path)
        
        album.slice()

    except Exception as e:
        print(f"Unexpected error: {e}")