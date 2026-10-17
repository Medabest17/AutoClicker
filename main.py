
import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller
from pynput import keyboard

BG = "#080808"
RED = "#ff2020"
WHITE = "#ffffff"

mouse = Controller()
running = threading.Event()
closing = threading.Event()

root = tk.Tk()
root.title("AutoClicker")
root.geometry("380x350")
root.configure(bg=BG)
root.resizable(False, False)

cps = tk.IntVar(value=10)
hotkey = tk.StringVar(value="F6")
status = tk.StringVar(value="STOPPED")


def click_loop():
    while not closing.is_set():
        if running.is_set():
            delay = 1 / max(1, min(100, cps.get()))
            mouse.click(Button.left)
            time.sleep(delay)
        else:
            time.sleep(0.01)


def toggle():
    if running.is_set():
        running.clear()
        status.set("STOPPED")
        button.config(text="START")
    else:
        running.set()
        status.set("CLICKING")
        button.config(text="STOP")


def key_pressed(key):
    if str(key).replace("Key.", "").upper() == hotkey.get():
        root.after(0, toggle)


def update_speed(value):
    speed_label.config(text=f"{int(float(value))} CPS")


tk.Label(
    root, text="AutoClicker", bg=BG, fg=RED,
    font=("Segoe UI", 25, "bold")
).pack(pady=(20, 12))

tk.Label(
    root, text="CLICK SPEED", bg=BG, fg=WHITE
).pack()

speed_label = tk.Label(
    root, text="10 CPS", bg=BG, fg=RED,
    font=("Segoe UI", 14, "bold")
)
speed_label.pack()

tk.Scale(
    root, from_=1, to=100, variable=cps,
    orient="horizontal", command=update_speed,
    bg=BG, fg=RED, troughcolor="#400000",
    highlightthickness=0, length=300
).pack(pady=8)

row = tk.Frame(root, bg=BG)
row.pack(pady=5)

tk.Label(
    row, text="HOTKEY", bg=BG, fg=WHITE
).pack(side="left", padx=8)

ttk.Combobox(
    row, textvariable=hotkey,
    values=[f"F{i}" for i in range(1, 13)],
    state="readonly", width=7
).pack(side="left")


def close():
    closing.set()
    running.clear()
    root.destroy()


button = tk.Button(
    root, text="START", command=toggle,
    bg="#350000", fg=RED,
    activebackground=RED, activeforeground=WHITE,
    font=("Segoe UI", 13, "bold"),
    relief="flat", width=15, pady=8
)
button.pack(pady=16)

tk.Label(
    root, textvariable=status, bg=BG, fg=RED,
    font=("Segoe UI", 11, "bold")
).pack()

threading.Thread(target=click_loop, daemon=True).start()
listener = keyboard.Listener(on_press=key_pressed)
listener.start()
