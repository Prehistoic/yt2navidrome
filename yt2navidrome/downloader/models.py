from dataclasses import dataclass


@dataclass
class Video:
    url: str
    title: str
    uploader: str


@dataclass
class Playlist:
    title: str
    videos: list[Video]
