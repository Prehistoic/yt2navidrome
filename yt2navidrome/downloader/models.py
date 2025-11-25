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


@dataclass
class Song:
    title: str
    release_date: str
    genre: str
    track_number: int


@dataclass
class Album:
    name: str
    release_date: str
    genre: str
    songs: list[Song]


@dataclass
class Artist:
    name: str
    albums: list[Album]
