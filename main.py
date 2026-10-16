
import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard

MAX_CPS = 100
BG = "#080808"
PANEL = "#151515"
RED = "#ff2020"
WHITE = "#f5f5f5"
GREY = "#aaaaaa"

mouse = MouseController()
clicking = threading.Event()
shutdown = threading.Event()

root = tk.Tk()
root.title("AutoClicker")
root.geometry("390x360")
root.configure(bg=BG)
root.resizable(False, False)

cps = tk.IntVar(value=50)
hotkey = tk.StringVar(value="F6")
status = tk.StringVar(value="Status: Stopped")


def click_worker():
    while not shutdown.is_set():
        if clicking.is_set():
            delay = 1 / max(1, min(MAX_CPS, cps.get()))
            mouse.click(Button.left, 1)
            time.sleep(delay)
        else:
            time.sleep(0.01)


def toggle_clicking():
    if clicking.is_set():
        clicking.clear()
        status.set("Status: Stopped")
        start_button.configure(text="Start")
    else:
        clicking.set()
        status.set("Status: Clicking")
        start_button.configure(text="Stop")


def on_key_press(key):
    try:
        pressed = str(key).replace("Key.", "").upper()
        if pressed == hotkey.get():
            root.after(0, toggle_clicking)
    except (RuntimeError, tk.TclError):
        pass


def update_cps(value):
    cps_value.configure(text=f"{int(float(value))} CPS")


def close_app():
    shutdown.set()
    clicking.clear()
    root.destroy()


# Header
tk.Label(
    root, text="AutoClicker", bg=BG, fg=RED,
    font=("Segoe UI", 25, "bold")
).pack(pady=(14, 12))

# CPS control
tk.Label(
    root, text="Click Speed", bg=BG, fg=WHITE,
    font=("Segoe UI", 11)
).pack()

cps_value = tk.Label(
    root, text="50 CPS", bg=BG, fg=RED,
    font=("Segoe UI", 12, "bold")
)
cps_value.pack()

speed_slider = tk.Scale(
    root, from_=1, to=MAX_CPS, orient="horizontal",
    variable=cps, command=update_cps,
    bg=BG, fg=RED, troughcolor="#401010",
    activebackground=RED, highlightthickness=0,
    length=300, bd=0
)
speed_slider.pack(pady=(0, 12))

# Hotkey selector
hotkey_row = tk.Frame(root, bg=BG)
hotkey_row.pack(pady=4)

tk.Label(
    hotkey_row, text="Start/Stop Hotkey:",
    bg=BG, fg=WHITE, font=("Segoe UI", 10)
).pack(side="left", padx=8)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Hotkey.TCombobox",
    fieldbackground=PANEL, background=PANEL,
    foreground=RED, arrowcolor=RED
)

hotkey_menu = ttk.Combobox(
    hotkey_row, textvariable=hotkey,
    values=[f"F{i}" for i in range(1, 13)],
    state="readonly", width=6,
    style="Hotkey.TCombobox"
)
hotkey_menu.pack(side="left")


# Buttons
start_button = tk.Button(
    root, text="Start", command=toggle_clicking,
    bg="#300707", fg=RED, activebackground="#600909",
    activeforeground=WHITE, font=("Segoe UI", 12, "bold"),
    relief="flat", width=12, pady=8, cursor="hand2"
)
start_button.pack(pady=(20, 10))

tk.Label(
    root, textvariable=status, bg=BG, fg=RED,
    font=("Segoe UI", 11, "bold")
).pack(pady=4)

tk.Label(
    root, text="Press your selected hotkey to start or stop",
    bg=BG, fg=GREY, font=("Segoe UI", 8)
).pack(pady=8)

threading.Thread(target=click_worker, daemon=True).start()
listener = keyboard.Listener(on_press=on_key_press)
listener.start()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()

shutdown.set()
clicking.clear()
listener.stop()
