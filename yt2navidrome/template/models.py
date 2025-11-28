from dataclasses import dataclass


@dataclass
class Template:
    """Represents the configuration required to download a YT video or playlist with yt-dlp"""

    name: str
    url: str
    playlist: bool
    parsers: list[str]

    def summary(cls) -> str:
        template_type = "playlist" if cls.playlist else "video"
        return f"{cls.name} ({template_type}) -> {cls.url}"
