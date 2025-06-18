from debug import debug
from pydub import AudioSegment
from mutagen.flac import FLAC
from mutagen.flac import Picture
import os
import re

class Track:
    def __init__(self,title, artist, start_time):
        self.title = title
        self.artist = artist
        self.start_time = start_time

class Album:
    def __init__(self, path_to_folder: str):
        self._songs = []
        self.folder = path_to_folder
        self.cue = os.path.abspath(os.path.join(path_to_folder, [f for f in os.listdir(path_to_folder) if f.endswith('.cue')][0]))
        
        debug("Initiated an album")
        debug(f"Folder: {self.folder}")
        debug(f"CUE: {self.cue}")

        self._parse()

    def set_cover(self, cover_path):
        self.cover = cover_path

    def songs(self):
        return self._songs
        
    def _parse(self):
        self.title = None
        self.genre = None
        self.year = None
        self.composer = None
        self.flac = None

        with open(self.cue, 'r', encoding='windows-1251') as cue_file:
            cue_data = cue_file.readlines()

        # Ищем название альбома
        for line in cue_data:
            line = line.strip()
            if line.startswith("TITLE") and not self.title:
                match = re.search(r'TITLE "(.*)"', line)
                if match:
                    self.title = match.group(1)
                break 
        
        # Ищем жанр альбома
        for line in cue_data:
            line = line.strip()
            if line.startswith("REM GENRE") and not self.genre:
                match = re.search(r'REM GENRE (.*)', line)
                if match:
                    self.genre = match.group(1)
                break 

        # Ищем год выпуска альбома
        for line in cue_data:
            line = line.strip()
            if line.startswith("REM DATE") and not self.year:
                match = re.search(r'REM DATE (.*)', line)
                if match:
                    self.year = match.group(1)
                break 
        
        # Ищем композитора альбома
        for line in cue_data:
            line = line.strip()
            if line.startswith("REM COMPOSER") and not self.composer:
                match = re.search(r'REM COMPOSER (.*)', line)
                if match:
                    self.composer = match.group(1)
                break 

        for line in cue_data:
            line = line.strip()
            if line.startswith("FILE") and not self.flac:
                match = re.search(r'FILE "(.*)" WAVE', line)
                if match:
                    self.flac = os.path.abspath(os.path.join(os.path.dirname(self.cue), match.group(1)))
                break 

        current_title = None
        current_artist = None
        current_start_time = None

        for line in cue_data:
            line = line.strip()
            
            if line.startswith("TITLE"):
                match = re.search(r'TITLE "(.*)"', line)
                if match:
                    current_title = match.group(1)

            elif line.startswith("PERFORMER"):
                match = re.search(r'PERFORMER "(.*)"', line)
                if match:
                    current_artist = match.group(1)

            elif line.startswith("INDEX 01"):
                match = re.search(r'INDEX 01 (\d+:\d+:\d+)', line)
                if match:
                    current_start_time = match.group(1)
                    current_start_time_ms = convert_time_to_milliseconds(current_start_time)
                
                    if current_title and current_artist and current_start_time_ms:
                        song = Track(title=current_title, artist=current_artist, start_time=current_start_time_ms)
                        debug(f"Track: {song.title}")
                        self._songs.append(song)

                        current_title = None
                        current_artist = None
                        current_start_time_ms = None
        
        # Находим время окончания каждой песни в альбоме
        for i, song in enumerate(self._songs):
            self._songs[i].end_time = self._songs[i + 1].start_time if i + 1 < len(self._songs) else None

        debug("Parsing has done")

    def slice(self):
        for song in self.songs():
            debug(f'Обрабатываем {song.title}')
            audio = AudioSegment.from_file(self.flac, format="flac")

            # Нарезаем аудио по указанному интервалу
            sliced_audio = audio[song.start_time:song.end_time]

            filename = f"{song.title} - {song.artist}.flac"
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)

            output_path = os.path.join(self.folder, filename)

            # Сохраняем нарезанное аудио в новый файл
            sliced_audio.export(output_path, format="flac")

            audio = FLAC(output_path)
            audio["title"] = song.title
            audio["artist"] = song.artist
            audio["album"] = self.title

            if self.cover:
                audio.clear_pictures()
                with open(self.cover, 'rb') as f:
                    image_data = f.read()
                
                picture = Picture()
                picture.data = image_data
                picture.type = 3  # 3 - это тип обложки альбома
                
                # Определяем mime-тип картинки
                if self.cover.lower().endswith((".jpg", ".jpeg")):
                    picture.mime = "image/jpeg"
                elif self.cover.lower().endswith(".png"):
                    picture.mime = "image/png"
                else:
                    picture.mime = "image/png"
                    debug("Unsupported image format. Using default image/png mime type.")
                
                audio.add_picture(picture)

            audio.save()

            print(f"# \033[1m{song.title}\033[0m - {song.artist}")
        debug("Done")

def convert_time_to_milliseconds(time_str):
    minutes, seconds, frames = map(int, time_str.split(':'))
    milliseconds = (minutes * 60 * 1000) + (seconds * 1000) + (frames * (1000 // 75))
    return milliseconds