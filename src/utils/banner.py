import sys

import fastapi


class ColorCode:
    GREEN = "\x1b[32;20m"
    BLUE = "\033[38;5;39m"
    RESET = "\033[0m"


class Banner:
    @staticmethod
    def get_fastapi_version() -> str:
        return fastapi.__version__

    @staticmethod
    def get_python_version() -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def generate_banner() -> list[str]:
        return [
            r"  ______         _                 ____   _____ ",
            r" |  ____|       | |         /\    |  __ \|_   _|",
            r" | |__ __   ___ | |_       /  \   | |__| | | |  ",
            r" |  __/ _ \/ __|| __|     / /\ \  |  ___/  | |  ",
            r" | | | (_| \__ \| |_     / /__\ \ | |     _| |_ ",
            r" |_|  \__,_|___/ \__|   /_/    \_\|_|    |_____|",
            r"                                                 ",
        ]

    @staticmethod
    def generate_info() -> list[str]:
        version = Banner.get_fastapi_version()
        python_version = Banner.get_python_version()

        return [
            f":: FastAPI Version :: ({version})",
            f":: Python {python_version} ::",
        ]

    @staticmethod
    def print_banner() -> None:
        banner_lines = Banner.generate_banner()
        info_lines = Banner.generate_info()

        print("")
        for line in banner_lines:
            print(f"{ColorCode.GREEN}{line}{ColorCode.RESET}")

        for line in info_lines:
            print(f"{ColorCode.BLUE}{line}{ColorCode.RESET}")
        print("")
