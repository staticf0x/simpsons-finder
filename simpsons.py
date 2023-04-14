#!/usr/bin/env python3
"""A simple script to find episodes of the Simpsons."""

import argparse
import re
from dataclasses import dataclass

import rich
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

# Regex to parse the SSxEE episode numbers
EP_NUMBER_REGEX = re.compile(r"(\d{2})x(\d{2})")

# Read args
parser = argparse.ArgumentParser()
parser.add_argument(
    "query",
    type=str,
    help="A phrase to search or season and episode number in SSxEE format",
)

args = parser.parse_args()


@dataclass
class EpisodeInfo:
    season: int
    episode: int
    name: str
    data: str


class DescHighlighter(RegexHighlighter):
    base_style = "desc."
    highlights = [r"\"(?P<quote>.+)\"", r"(?P<character>[\w ]+):"]


class SimpsonsFinder:
    def __init__(self):
        self.__data = {}

    def load_db(self) -> None:
        """Load the text file into a dict we can access."""
        data = {}

        with open("db.txt", "r") as fread:
            lines = []
            season = episode = 0
            name = ""

            for line in fread:
                if m := EP_NUMBER_REGEX.search(line):
                    if lines:
                        ep_data = EpisodeInfo(season, episode, name, "\n".join(lines))
                        data.setdefault(season, {})
                        data[season][episode] = ep_data

                        lines = []

                    # Header
                    season = int(m.group(1))
                    episode = int(m.group(2))
                    name = line[6:].rstrip("\n")

                    continue

                line = line.lstrip("\t")
                line = line.rstrip("\n")
                lines.append(line)

        self.__data = data

    def find(self, query: str) -> None:
        """Find query in the database and print matched episode numbers."""
        rich.print(f'"[bold cyan]{query}[/bold cyan]" found in following episodes:\n')

        for season in self.__data:
            for episode in self.__data[season]:
                ep_data = self.__data[season][episode]

                if query in ep_data.data.lower() or query in ep_data.name.lower():
                    self.print_episode_header(season, episode)

    def print_episode_info(self, season: int, episode: int) -> None:
        """Print all episode data."""
        ep_data = self.__data[season][episode]

        self.print_episode_header(season, episode)

        theme = Theme({"desc.quote": "italic", "desc.character": "cyan"})
        console = Console(highlighter=DescHighlighter(), theme=theme)

        print()
        console.print(ep_data.data)

    def print_episode_header(self, season: int, episode: int) -> None:
        """Print season, episode and name in colors."""
        ep_data = self.__data[season][episode]

        rich.print(
            f"[bold yellow]{season:02d}x{episode:02d} {ep_data.name}[/bold yellow]"
        )


if __name__ == "__main__":
    finder = SimpsonsFinder()
    finder.load_db()

    if m := EP_NUMBER_REGEX.search(args.query):
        try:
            season = int(m.group(1))
            episode = int(m.group(2))

            finder.print_episode_info(season, episode)
        except KeyError:
            rich.print(f"[bold red]No episode {args.query} in database[/bold red]")
    else:
        finder.find(args.query)
