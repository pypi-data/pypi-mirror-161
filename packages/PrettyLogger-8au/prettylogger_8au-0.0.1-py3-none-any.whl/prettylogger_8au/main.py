from datetime import datetime

from colorama import Fore, Style


class Logger:
    def success_log(self, message):
        print(
            f"{Fore.GREEN}[{datetime.utcnow()}] {Fore.WHITE}LOG {Fore.BLUE}{message}{Style.RESET_ALL}"
        )

    def error_log(self, message):
        print(
            f"{Fore.GREEN}[{datetime.utcnow()}] {Fore.WHITE}ERROR {Fore.RED}{message}{Style.RESET_ALL}"
        )

    def warn_log(self, message):
        print(
            f"{Fore.GREEN}[{datetime.utcnow()}] {Fore.WHITE}WARN {Fore.YELLOW}{message}{Style.RESET_ALL}"
        )
