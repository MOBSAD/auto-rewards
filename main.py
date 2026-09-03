import argparse
import math
import os
from random import randrange
import shlex
import shutil
from string import ascii_letters
import subprocess
import sys
from time import sleep
import webbrowser

DEFAULT_SEARCH_COUNT = 15
DEFAULT_SEARCH_DELAY_SECONDS = 7
TAB_CLOSE_DELAY_SECONDS = 0.5
COMMON_BROWSERS = ("firefox", "chromium", "google-chrome", "brave-browser")


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


def detect_session(environment=None):
    environment = os.environ if environment is None else environment
    session_type = environment.get("XDG_SESSION_TYPE")
    return session_type.lower() if session_type else None


def detect_compositor(environment=None):
    environment = os.environ if environment is None else environment
    if environment.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "Hyprland"

    return None


def find_browser(environment=None):
    environment = os.environ if environment is None else environment
    configured_browsers = environment.get("BROWSER", "")

    for browser_entry in configured_browsers.split(os.pathsep):
        if not browser_entry:
            continue

        try:
            command = shlex.split(browser_entry)[0]
        except (ValueError, IndexError):
            continue

        if shutil.which(command):
            return browser_entry

    for browser_name in COMMON_BROWSERS:
        if shutil.which(browser_name):
            return browser_name

    try:
        browser_controller = webbrowser.get()
    except webbrowser.Error:
        return None

    return getattr(browser_controller, "name", browser_controller.__class__.__name__)


def check_environment(environment=None):
    session_type = detect_session(environment)
    detect_compositor(environment)
    environment_ready = True

    if session_type is None:
        print(
            "[!] Não foi possível identificar a sessão gráfica "
            "(XDG_SESSION_TYPE ausente).",
            file=sys.stderr,
        )
    elif session_type != "wayland":
        print(
            f"[!] Sessão {session_type.upper()} detectada; "
            "este programa é focado em Wayland.",
            file=sys.stderr,
        )

    if shutil.which("ydotool") is None:
        print("[x] ydotool não encontrado.", file=sys.stderr)
        print("Instale no Arch Linux: sudo pacman -S ydotool", file=sys.stderr)
        environment_ready = False

    if find_browser(environment) is None:
        print("[x] Nenhum navegador disponível foi encontrado.", file=sys.stderr)
        environment_ready = False

    return environment_ready


def main(arguments=None):
    options = parse_arguments(arguments)

    try:
        if not check_environment():
            return 1

        open_tabs(options.searches, options.delay)
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
