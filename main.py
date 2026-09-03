import argparse
import math
from random import randrange
from string import ascii_letters
import subprocess
import sys
import webbrowser
from time import sleep

DEFAULT_SEARCH_COUNT = 15
DEFAULT_SEARCH_DELAY_SECONDS = 7
TAB_CLOSE_DELAY_SECONDS = 0.5


def create_term():
    term = ""
    for _ in range(9):
        term += ascii_letters[randrange(len(ascii_letters) - 4)]

    return term


def open_tabs(tab_count, search_delay):
    base_url = "https://www.bing.com/search?q=como "
    end_url = "&form=TSASDS"

    for _ in range(tab_count):
        search_url = base_url + create_term() + end_url
        webbrowser.open(search_url)
        sleep(search_delay)

    close_tabs(tab_count)


def close_tabs(tab_count):
    for _ in range(tab_count):
        subprocess.run(
            ["ydotool", "key", "29:1", "17:1", "17:0", "29:0"],
            check=False,
        )
        sleep(TAB_CLOSE_DELAY_SECONDS)
    print("TUDO FEITO")


def positive_integer(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um número inteiro") from None

    if number <= 0:
        raise argparse.ArgumentTypeError("deve ser maior que zero")

    return number


def positive_number(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um número") from None

    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("deve ser maior que zero")

    return number


def parse_arguments(arguments=None):
    parser = argparse.ArgumentParser(
        description="Automatiza pesquisas de recompensas no Linux/Wayland."
    )
    parser.add_argument(
        "-n",
        "--searches",
        type=positive_integer,
        default=DEFAULT_SEARCH_COUNT,
        help=f"quantidade de pesquisas (padrão: {DEFAULT_SEARCH_COUNT})",
    )
    parser.add_argument(
        "--delay",
        type=positive_number,
        default=DEFAULT_SEARCH_DELAY_SECONDS,
        metavar="SECONDS",
        help=f"segundos entre pesquisas (padrão: {DEFAULT_SEARCH_DELAY_SECONDS})",
    )

    return parser.parse_args(arguments)


def main(arguments=None):
    options = parse_arguments(arguments)

    try:
        open_tabs(options.searches, options.delay)
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
