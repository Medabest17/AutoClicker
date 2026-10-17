import time
import threading
import tkinter as tk
import customtkinter as ctk
from pynput import keyboard
from pynput.mouse import Button, Controller

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#080a0f"
PANEL = "#11151e"
RED = "#ff2348"
MUTED = "#93a0b5"
WHITE = "#f4f6fb"
GREEN = "#32d583"
MAX_CPS = 100

mouse = Controller()
running = threading.Event()
closing = threading.Event()
lock = threading.Lock()

settings = {"cps": 50, "hotkey": "F6", "mode": "Left Click"}
stats = {"clicks": 0, "elapsed": 0.0}
start_time = 0.0
hotkey_down = False


app = ctk.CTk()
app.title("AutoClicker v2.0")
app.geometry("1050x720")
app.minsize(850, 620)
app.configure(fg_color=BG)


def make_label(parent, text, size=14, color=WHITE, weight="normal"):
    return ctk.CTkLabel(
        parent, text=text, text_color=color,
        font=("Segoe UI", size, weight)
    )


def make_card(parent, title):
    card = ctk.CTkFrame(
        parent, fg_color=PANEL, corner_radius=16,
        border_width=1, border_color="#252d3c"
    )
    make_label(card, title, 13, RED, "bold").pack(
        anchor="w", padx=20, pady=(18, 8)
    )
    return card


def toggle():
    global start_time

    if running.is_set():
        running.clear()
        return

    with lock:
        stats["clicks"] = 0
        stats["elapsed"] = 0.0

    start_time = time.perf_counter()
    running.set()


def click_loop():
    next_click = time.perf_counter()

    while not closing.is_set():
        if not running.is_set():
            time.sleep(0.005)
            next_click = time.perf_counter()
            continue

        with lock:
            cps = max(1, min(MAX_CPS, settings["cps"]))
            mode = settings["mode"]

        now = time.perf_counter()
        if now < next_click:
            time.sleep(min(next_click - now, 0.002))
            continue

        try:
            button = Button.left if mode == "Left Click" else Button.right
            mouse.click(button, 1)
        except Exception:
            running.clear()
            continue

        finished = time.perf_counter()

        with lock:
            stats["clicks"] += 1
            stats["elapsed"] = finished - start_time

        next_click += 1 / cps
        if finished - next_click > 0.05:
            next_click = finished + 1 / cps


def on_press(key):
    global hotkey_down

    try:
        name = str(key).replace("Key.", "").upper()
        with lock:
            target = settings["hotkey"]

        if name == target and not hotkey_down:
            hotkey_down = True
            app.after(0, toggle)
    except (RuntimeError, tk.TclError):
        pass


def on_release(key):
    global hotkey_down

    try:
        name = str(key).replace("Key.", "").upper()
        with lock:
            target = settings["hotkey"]
        if name == target:
            hotkey_down = False
    except Exception:
        pass


def change_speed(value):
    speed = int(float(value))
    with lock:
        settings["cps"] = max(1, min(MAX_CPS, speed))
    speed_text.configure(text=f"{speed} CPS")


def change_hotkey(value):
    with lock:
        settings["hotkey"] = value
    hotkey_text.configure(text=value)


def change_mode(value):
    with lock:
        settings["mode"] = value


def close_app():
    closing.set()
    running.clear()
    app.destroy()


# Top bar
top = ctk.CTkFrame(app, fg_color="#0c0f16", corner_radius=0, height=76)
top.pack(fill="x")
top.pack_propagate(False)

make_label(top, "◉  Auto", 27, WHITE, "bold").pack(
    side="left", padx=(24, 0)
)
make_label(top, "Clicker", 27, RED, "bold").pack(side="left")
make_label(top, "  v2.0.0", 12, MUTED).pack(
    side="left", padx=12
)

status_top = make_label(top, "●  READY", 12, GREEN, "bold")
status_top.pack(side="right", padx=28)

# Main dashboard
body = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)
body.pack(fill="both", expand=True, padx=22, pady=20)
body.grid_columnconfigure(0, weight=3)
body.grid_columnconfigure(1, weight=2)
body.grid_rowconfigure(0, weight=1)

left = ctk.CTkFrame(body, fg_color=BG, corner_radius=0)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

right = ctk.CTkFrame(body, fg_color=BG, corner_radius=0)
right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

# Hero
make_label(left, "AutoClicker", 32, WHITE, "bold").pack(
    anchor="w", padx=4, pady=(2, 0)
)
make_label(left, "FAST  •  RELIABLE  •  SIMPLE", 12, MUTED).pack(
    anchor="w", padx=5, pady=(0, 18)
)

# Speed panel
speed_card = make_card(left, "CLICKS PER SECOND")
speed_card.pack(fill="x", pady=(0, 14))

speed_text = make_label(speed_card, "50 CPS", 34, WHITE, "bold")
speed_text.pack(anchor="w", padx=20)

make_label(
    speed_card, "Adjust the speed from 1 to 100",
    12, MUTED
).pack(anchor="w", padx=20, pady=(0, 10))

speed_slider = ctk.CTkSlider(
    speed_card, from_=1, to=100,
    number_of_steps=99, progress_color=RED,
    button_color=RED, button_hover_color="#ff6078",
    fg_color="#39202a", command=change_speed
)
speed_slider.set(50)
speed_slider.pack(fill="x", padx=20, pady=(0, 8))

make_label(speed_card, "1 CPS", 10, MUTED).pack(
    side="left", padx=20, pady=(0, 16)
)
make_label(speed_card, "MAX 100", 10, RED, "bold").pack(
    side="right", padx=20, pady=(0, 16)
)

# Hotkey and click mode
options = ctk.CTkFrame(left, fg_color=BG, corner_radius=0)
options.pack(fill="x", pady=(0, 14))
options.grid_columnconfigure((0, 1), weight=1)

hotkey_card = make_card(options, "START / STOP HOTKEY")
hotkey_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

hotkey_text = make_label(hotkey_card, "F6", 23, WHITE, "bold")
hotkey_text.pack(anchor="w", padx=18, pady=(2, 8))

hotkey_menu = ctk.CTkComboBox(
    hotkey_card,
    values=[f"F{i}" for i in range(1, 13)],
    command=change_hotkey,
    width=130, height=36,
    fg_color="#1b2230", border_color="#30394a",
    button_color=RED
)
hotkey_menu.set("F6")
hotkey_menu.pack(anchor="w", padx=18, pady=(0, 16))

mode_card = make_card(options, "CLICK MODE")
mode_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

make_label(mode_card, "Mouse button", 12, MUTED).pack(
    anchor="w", padx=18, pady=(2, 8)
)

mode_menu = ctk.CTkComboBox(
    mode_card, values=["Left Click", "Right Click"],
    command=change_mode, width=145, height=36,
    fg_color="#1b2230", border_color="#30394a",
    button_color=RED
)
mode_menu.set("Left Click")
mode_menu.pack(anchor="w", padx=18, pady=(0, 16))

# Main controls
start_button = ctk.CTkButton(
    left, text="▶   START CLICKING",
    command=toggle, height=58, corner_radius=12,
    fg_color=RED, hover_color="#d91b3c",
    text_color="white", font=("Segoe UI", 17, "bold")
)
start_button.pack(fill="x", pady=(2, 10))

stop_button = ctk.CTkButton(
    left, text="■   STOP", command=lambda: running.clear(),
    height=48, corner_radius=12,
    fg_color="#1a202b", hover_color="#2a3343",
    border_width=1, border_color="#30394a",
    text_color=WHITE, font=("Segoe UI", 14, "bold")
)
stop_button.pack(fill="x")

# Statistics
stats_card = make_card(right, "LIVE STATISTICS")
stats_card.pack(fill="x", pady=(0, 14))

current_cps = make_label(stats_card, "0.0", 30, WHITE, "bold")
current_cps.pack(anchor="w", padx=20, pady=(4, 0))
make_label(stats_card, "CURRENT CPS", 11, MUTED).pack(
    anchor="w", padx=20, pady=(0, 12)
)

total_clicks = make_label(stats_card, "0", 25, WHITE, "bold")
total_clicks.pack(anchor="w", padx=20)
make_label(stats_card, "TOTAL CLICKS", 11, MUTED).pack(
    anchor="w", padx=20, pady=(0, 12)
)

elapsed_label = make_label(stats_card, "0.0s", 25, WHITE, "bold")
elapsed_label.pack(anchor="w", padx=20)
make_label(stats_card, "ELAPSED TIME", 11, MUTED).pack(
    anchor="w", padx=20, pady=(0, 18)
)

# Tips panel
tips = make_card(right, "QUICK TIPS")
tips.pack(fill="x", pady=(0, 14))

make_label(
    tips, "•  Choose your CPS before starting\n\n"
          "•  Use F6 or select another F-key\n\n"
          "•  Press the hotkey again to stop\n\n"
          "•  Use only where autoclicking is allowed",
    12, MUTED
).pack(anchor="w", padx=18, pady=(2, 18))

make_label(
    right, "BLACK & RED EDITION  •  v2.0.0",
    10, RED, "bold"
).pack(pady=10)


def refresh():
    if closing.is_set():
        return

    active = running.is_set()

    with lock:
        count = stats["clicks"]
        elapsed = stats["elapsed"]
        actual = count / elapsed if elapsed > 0 else 0

    current_cps.configure(text=f"{actual:.1f}" if active else "0.0")
    total_clicks.configure(text=str(count))
    elapsed_label.configure(text=f"{elapsed:.1f}s")

    status_top.configure(
        text="●  CLICKING" if active else "●  READY",
        text_color=RED if active else GREEN
    )
    start_button.configure(
        text="●  CLICKING... (PRESS TO STOP)"
        if active else "▶   START CLICKING"
    )

    app.after(100, refresh)


threading.Thread(target=click_loop, daemon=True).start()

listener = keyboard.Listener(
    on_press=on_press, on_release=on_release
)
listener.start()

app.protocol("WM_DELETE_WINDOW", close_app)
app.after(100, refresh)
app.mainloop()

closing.set()
running.clear()
listener.stop()
