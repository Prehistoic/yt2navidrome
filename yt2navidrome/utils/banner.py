import pyfiglet

from yt2navidrome.config import PROJECT_NAME


def display_banner(font: str = "slant") -> None:
    """
    Displaying a nice looking ASCII banner :)
    """
    f = pyfiglet.figlet_format(PROJECT_NAME.upper(), font=font)
    print(f)
