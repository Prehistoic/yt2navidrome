from dataclasses import dataclass


@dataclass
class MetadataParser:
    """Represents a parser used to process video information
    and convert it into metadata for the downloaded video file"""

    input: str
    regex: str

    def summary(cls) -> str:
        return f"{cls.input} = {cls.regex}"


@dataclass
class Template:
    """Represents the configuration required to download a YT video or playlist with yt-dlp"""

    name: str
    url: str
    playlist: bool
    parsers: list[MetadataParser]

    def summary(cls) -> str:
        template_type = "playlist" if cls.playlist else "video"
        return f"{cls.name} ({template_type}) -> {cls.url}"
