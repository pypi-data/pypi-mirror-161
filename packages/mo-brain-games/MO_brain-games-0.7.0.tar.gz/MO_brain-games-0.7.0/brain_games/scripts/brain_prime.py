#!/usr/bin/env python3
from brain_games.play_game import play
from brain_games.games import is_prime


def main():
    play(is_prime)


if __name__ == '__main__':
    main()
