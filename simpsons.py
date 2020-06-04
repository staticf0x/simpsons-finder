#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple script to find episodes of the Simpsons
"""

import argparse
import sys
import re
from dataclasses import dataclass
from colorama import Fore, Style, init

init(autoreset=True)

# Regex to parse the SSxEE episode numbers
EP_NUMBER_REGEX = re.compile(r'(\d{2})x(\d{2})')

# Colors
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
BLUE = Fore.CYAN + Style.BRIGHT
RES = Style.RESET_ALL

# Read args
parser = argparse.ArgumentParser()
parser.add_argument('query', type=str,
                    help='A phrase to search or season and episode number in SSxEE format')

args = parser.parse_args()

@dataclass
class EpisodeInfo:
    season: int
    episode: int
    name: str
    data: str


class SimpsonsFinder:
    def __init__(self):
        self.__data = {}

    def load_db(self):
        """
        Loads the text file into a dict we can access
        """

        data = {}

        with open('db.txt', 'r') as fread:
            lines = []

            for line in fread:
                if m := EP_NUMBER_REGEX.search(line):
                    if lines:
                        ep_data = EpisodeInfo(season, episode, name, '\n'.join(lines))
                        data.setdefault(season, {})
                        data[season][episode] = ep_data

                        lines = []

                    # Header
                    season = int(m.group(1))
                    episode = int(m.group(2))
                    name = line[6:].rstrip('\n')

                else:
                    line = line.lstrip('\t')
                    line = line.rstrip('\n')
                    lines.append(line)

        self.__data = data

    def find(self, query):
        """
        Find query in the database and print matched episode numbers
        """

        print(f'"{BLUE}{query}{RES}" found in following episodes:\n')

        for season in self.__data:
            for episode in self.__data[season]:
                ep_data = self.__data[season][episode]

                if query in ep_data.data.lower() or query in ep_data.name.lower():
                    self.__print_episode_header(season, episode)


    def print_episode_info(self, season, episode):
        """
        Print all episode data
        """

        ep_data = self.__data[season][episode]

        self.__print_episode_header(season, episode)

        print()
        print(ep_data.data)

    def __print_episode_header(self, season, episode):
        """
        Print season, episode and name in colors
        """

        ep_data = self.__data[season][episode]

        print(f'{YELLOW}{season:02d}x{episode:02d} {ep_data.name}')


if __name__ == '__main__':
    finder = SimpsonsFinder()
    finder.load_db()

    if m := EP_NUMBER_REGEX.search(args.query):
        try:
            season = int(m.group(1))
            episode = int(m.group(2))

            finder.print_episode_info(season, episode)
        except KeyError:
            print(f'{RED} No episode {args.query} in database')
    else:
        finder.find(args.query)
