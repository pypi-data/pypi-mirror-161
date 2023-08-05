import os
import tkinter as tk
from tkinter import filedialog
import threading
import ctypes
import time
import random
import shutil
import queue

from .functions import remove_duplicate
from .colors import COLORS, RESET


class Checker:
    def __init__(self, title: str, banner: str = "", proxy: bool = False, color: str = "red",
                 mode: str = "log") -> None:
        self.banner = banner
        self.proxy = proxy
        self.color = COLORS[color]
        self.mode = mode
        self.title = title
        self.cpm = 0
        self.cui_thread_status = True  # When this is false, the cui thread will stop
        self.threads = []

        self.data = {
            "checked": 0,
            "hits": 0,
            "custom": 0,
            "bad": 0,
            "errors": 0,
            "retries": 0,
            "loaded": 0
        }
        self.proxy_settings = {
            "proxy_type": "",
            "proxy_path": None
        }

        root = tk.Tk()
        root.withdraw()

    def load_combo(self) -> list:
        combo_path = filedialog.askopenfilename(title="Select your combo")
        with open(combo_path, "r", encoding="latin-1") as f:
            content = f.readlines()
        self.data["loaded"] = len(content)

        return remove_duplicate(content)

    def load_proxies(self) -> None:
        self.data["proxy_location"] = filedialog.askopenfilename(title="Select your proxies")

    def set_proxy_type(self, proxy_choice: int) -> None:
        if proxy_choice == 1:
            self.proxy_settings["proxy_type"] = "https"
        elif proxy_choice == 2:
            self.proxy_settings["proxy_type"] = "socks4"
        elif proxy_choice == 3:
            self.proxy_settings["proxy_type"] = "socks5"

    def get_proxy(self) -> dict:
        proxy_list = []
        with open(self.data["proxy_path"], "r", encoding="UTF-8") as message:
            lines = message.readlines()

        for line in lines:
            proxy_list.append(line.replace("\n", ""))
        proxy = {"http": "%s://%s" % (self.data["proxy_type"], random.choice(proxy_list))}

        return proxy

    def console_title(self) -> None:
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW(
                "%s - Hits: %s | Customs: %s | Bad: %s | CPM: %s | Checked: %s/%s | Retries: %s | Errors: %s" %
                (self.title, self.data["hits"], self.data["custom"], self.data["bad"], self.cpm, self.data["checked"],
                 self.data["loaded"], self.data["retries"], self.data["errors"]))

    def get_cpm(self) -> None:
        while True:
            previous = self.data['checked']
            time.sleep(1)
            after = self.data['checked']
            self.cpm = (after - previous) * 60

    def print_logo(self) -> None:
        os.system("cls")
        width = shutil.get_terminal_size().columns
        banner = self.banner.split('\n')
        for lines in banner:
            print(self.color + lines.center(width) + RESET)
        print('\n\n')

    def cui(self):
        while True:
            if not self.cui_thread_status:
                break
            self.print_logo()
            print('''
     %s(%s~%s) %s- Lines Loaded: %s
     %s(%s~%s) %s- Checked: %s

     %s(%s~%s) %s- Hits: %s
     %s(%s~%s) %s- Customs: %s
     %s(%s~%s) %s- Bad: %s

     %s(%s~%s) %s- CPM: %s
     %s(%s~%s) %s- Errors: %s
     %s(%s~%s) %s- Retries: %s%s
    ''' % (self.color, COLORS["light_turquoise"], self.color, COLORS["light_turquoise"], self.data['loaded'],
           self.color,
           COLORS["light_turquoise"], self.color, COLORS["light_turquoise"], self.data['checked'], self.color,
           COLORS["green"], self.color, COLORS["green"], self.data['hits'], self.color, COLORS["orange"], self.color,
           COLORS["orange"], self.data['custom'], self.color, COLORS["red"], self.color, COLORS["red"],
           self.data['bad'],
           self.color, COLORS["purple"], self.color, COLORS["purple"], self.cpm, self.color, COLORS["purple"],
           self.color, COLORS["purple"], self.data['errors'], self.color, COLORS["purple"], self.color,
           COLORS["purple"],
           self.data['retries'], RESET))

            time.sleep(1)
            os.system('cls')

    def initialise_console(self) -> None:
        ctypes.windll.kernel32.SetConsoleTitleW(self.title)
        self.print_logo()

    def start_threads(self) -> None:
        self.threads.append(threading.Thread(target=self.get_cpm, daemon=True))
        self.threads.append(threading.Thread(target=self.console_title, daemon=True))
        if self.mode == "cui":
            self.threads.append(threading.Thread(target=self.cui, daemon=True))

        for thread in self.threads:
            thread.start()

    def worker(self, check, q, proxy):
        while True:
            try:
                combo = q.get()
                email, password = combo.split(":")
            except queue.Empty:
                return

            result = check(email, password, proxy)
            match result:
                case "good":
                    self.data["hits"] += 1
                    self.data["checked"] += 1
                    if self.mode == "log":
                        print(f"[{COLORS['green']}+{RESET}] {COLORS['green']}-{RESET} {combo}")
                case "bad":
                    self.data["bad"] += 1
                    self.data["checked"] += 1
                case "custom":
                    self.data["custom"] += 1
                    self.data["checked"] += 1
                    if self.mode == "log":
                        print(f"[{COLORS['yellow']}+{RESET}] {COLORS['yellow']}-{RESET} {combo}")
                case "retry":
                    self.data["retries"] += 1
                    self.worker(check, q, proxy)
                case "error":
                    self.data["errors"] += 1
                    self.worker(check, q, proxy)
                case _:
                    raise TypeError

            '''
            Your check function must return the following strings:
            - "good"
            - "bad"
            - "custom"
            - "retry"
            - "error"
            
            Failure to do so will raise an error
            '''

            q.task_done()

    def run(self, check):
        self.initialise_console()
        if self.proxy:
            input(f"[{self.color}+{RESET}] {self.color}-{RESET} Press ENTER to load your proxies...")
            self.load_proxies()
            self.print_logo()
            try:
                proxy_choice = int(input(f'''
 [{self.color}1{RESET}] {self.color}-{RESET} HTTPS
 [{self.color}2{RESET}] {self.color}-{RESET} SOCKS 4
 [{self.color}3{RESET}] {self.color}-{RESET} SOCKS 5

 {self.color}>>{RESET}'''))
            except TypeError:
                self.run(check)
            self.set_proxy_type(proxy_choice)
            self.print_logo()

        input(f"[{self.color}+{RESET}] {self.color}-{RESET} Press ENTER to load your combo...")
        combo = self.load_combo()

        self.print_logo()
        thread_count = int(input(f"[{self.color}+{RESET}] {self.color}-{RESET} How many threads: "))

        self.print_logo()
        input(f"[{self.color}+{RESET}] {self.color}-{RESET} Press ENTER to start... ")
        self.start_threads()

        q = queue.Queue()
        for line in combo:
            q.put_nowait(line)

        for _ in range(thread_count):
            if self.proxy:
                proxy = self.get_proxy()
            else:
                proxy = None
            threading.Thread(target=self.worker, args=(check, q, proxy)).start()

        '''
        Your check function must have 3 parameters: email, password and proxy.
        Whether you use proxies or not the parameter must be present.
        If you don't use proxies your parameter will have a None type.
        '''

        q.join()
        self.cui_thread_status = False
        for thread in self.threads:
            thread.join()
        time.sleep(5)
        self.print_logo()
        print(f"[{self.color}+{RESET}] {self.color}-{RESET} Done, you can now close the window...")
