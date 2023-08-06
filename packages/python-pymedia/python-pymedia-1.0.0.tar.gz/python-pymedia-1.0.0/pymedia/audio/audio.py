from __future__ import annotations
import pydub
import pydub.playback
import threading
import io
import urllib.request
import os
import typing
import time

class Audio:
    """
        An object representing any type of audio

        Usage:
            Audio(source)

            source - Path to audio file or url. If None, defaults to empty file
    """
    def __init__(self, source: typing.Union[os.PathLike, str]=None) -> None:
        if source:
            if os.path.isfile(source):
                source_path, source_extension = os.path.splitext(source)
                match source_extension:
                    case ".wav":
                        self._audio_segment = pydub.AudioSegment.from_wav(source)
                    case ".ogg":
                        self._audio_segment = pydub.AudioSegment.from_ogg(source)
                    case ".mp3":
                        self._audio_segment = pydub.AudioSegment.from_mp3(source)
                    case _:
                        self._audio_segment = pydub.AudioSegment.from_file(source)
                
            elif source.startswith("http://") or source.startswith("https://"):
                data = urllib.request.urlopen(source).read()
                io_stream = io.BytesIO(data)
                self._audio_segment = pydub.AudioSegment.from_file(io_stream)
        
        else:
            self._audio_segment = pydub.AudioSegment.empty()
   
    def play(self, block: bool =True) -> threading.Thread:
        """
            Outputs stored audio through speakers. If blocking is set to False, method will return immediatly and will audio will play in background.

            Usage:
                Audio.play()
        """
        th = threading.Thread(target=self._play, daemon=True)
        th.start()
        if block:
            time.sleep(len(self._audio_segment)/1000)
        else:
            return th
    
    def _play(self):
        pydub.playback.play(self._audio_segment)

    def split(self, point: int) -> tuple:
        """
        Divide the audio into two parts

        Usage:
            audio1, audio2 = Audio.split(index)

        """
        audio1 = Audio()
        audio2 = Audio()
        audio1._audio_segment = self._audio_segment[:point]
        audio2._audio_segment = self._audio_segment[point:]
        return audio1, audio2

    def cut(self, point: int) -> Audio:
        audio1 = Audio()
        audio1._audio_segment = self._audio_segment[:point]
        return audio1

    def cut_ip(self, point: int) -> None:
        self._audio_segment = self._audio_segment[:point]
