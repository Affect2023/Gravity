"""
Monty Hall Problem Simulator
Run: python monty_hall.py
Convert to EXE: pyinstaller --onefile --windowed monty_hall.py
"""

import tkinter as tk
from tkinter import ttk, font
import random
import math


# ─── Palette ────────────────────────────────────────────────────────────────
BG        = "#0f0f1a"
PANEL     = "#1a1a2e"
ACCENT    = "#e8b84b"
ACCENT2   = "#c0392b"
TEXT      = "#f0e6d3"
MUTED     = "#7a7a9a"
DOOR_IDLE = "#2a2a4a"
DOOR_HL   = "#3a3a6a"
DOOR_GOOD = "#1a4a2a"
DOOR_BAD  = "#4a1a1a"
DOOR_OPEN = "#16213e"

FONT_TITLE  = ("Georgia", 28, "bold")
FONT_SUB    = ("Georgia", 13, "italic")
FONT_LABEL  = ("Courier New", 11, "bold")
FONT_SMALL  = ("Courier New", 10)
FONT_DOOR   = ("Georgia", 22, "bold")
FONT_DOOR_S = ("Courier New", 9)
FONT_BTN    = ("Courier New", 12, "bold")
FONT_STAT   = ("Courier New", 11)


# ─── Main App ───────────────────────────────────────────────────────────────
class MontyHallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monty Hall Simulator")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(860, 580)

        # Center window
        self.geometry("960x640")
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 960) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"960x640+{x}+{y}")

        self._show_startup()

    # ── Startup Screen ──────────────────────────────────────────────────────
    def _show_startup(self):
        self._clear()
        f = tk.Frame(self, bg=BG)
        f.pack(expand=True, fill="both")

        # Decorative top bar
        bar = tk.Frame(f, bg=ACCENT, height=4)
        bar.pack(fill="x")

        inner = tk.Frame(f, bg=BG)
        inner.pack(expand=True)

        tk.Label(inner, text="🚪  THE MONTY HALL PROBLEM", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(pady=(40, 6))
        tk.Label(inner, text="Switch or stay — does it really matter?",
                 font=FONT_SUB, bg=BG, fg=MUTED).pack(pady=(0, 40))

        # Door count selector
        card = tk.Frame(inner, bg=PANEL, padx=40, pady=30)
        card.pack(ipadx=20)

        tk.Label(card, text="HOW MANY DOORS?", font=FONT_LABEL,
                 bg=PANEL, fg=TEXT).pack(pady=(0, 16))

        btn_row = tk.Frame(card, bg=PANEL)
        btn_row.pack()

        self._door_count = tk.IntVar(value=3)
        for n in [3, 4, 5, 6, 8, 10]:
            self._door_btn(btn_row, n)

        # Custom entry
        custom_row = tk.Frame(card, bg=PANEL)
        custom_row.pack(pady=(14, 0))
        tk.Label(custom_row, text="Custom:", font=FONT_SMALL,
                 bg=PANEL, fg=MUTED).pack(side="left", padx=(0, 8))
        self._custom_var = tk.StringVar()
        entry = tk.Entry(custom_row, textvariable=self._custom_var, width=5,
                         font=FONT_LABEL, bg=DOOR_IDLE, fg=ACCENT,
                         insertbackground=ACCENT, relief="flat",
                         justify="center")
        entry.pack(side="left")
        tk.Button(custom_row, text="SET", font=FONT_DOOR_S, bg=ACCENT,
                  fg=BG, relief="flat", activebackground=TEXT, cursor="hand2",
                  command=self._apply_custom).pack(side="left", padx=(8, 0))

        self._door_label = tk.Label(card, text="Selected: 3 doors",
                                    font=FONT_SMALL, bg=PANEL, fg=ACCENT)
        self._door_label.pack(pady=(14, 0))

        # Start button
        tk.Button(inner, text="▶  START GAME", font=FONT_BTN,
                  bg=ACCENT, fg=BG, relief="flat", padx=30, pady=12,
                  activebackground=TEXT, cursor="hand2",
                  command=self._start_game).pack(pady=30)

        tk.Label(inner, text="One door hides a car. The rest hide goats.",
                 font=FONT_SMALL, bg=BG, fg=MUTED).pack()
        tk.Label(inner,
                 text="After you pick, Monty opens a goat door. Then you decide: switch or stay?",
                 font=FONT_SMALL, bg=BG, fg=MUTED).pack(pady=(4, 0))

        # Bottom bar
        tk.Frame(f, bg=ACCENT2, height=4).pack(side="bottom", fill="x")

    def _door_btn(self, parent, n):
        var = self._door_count
        lbl = self._door_label if hasattr(self, "_door_label") else None

        def select():
            var.set(n)
            self._door_label.config(text=f"Selected: {n} doors")

        btn = tk.Button(parent, text=str(n), font=FONT_BTN, width=3,
                        bg=DOOR_IDLE, fg=TEXT, relief="flat",
                        activebackground=DOOR_HL, cursor="hand2",
                        command=select)
        btn.pack(side="left", padx=5)

    def _apply_custom(self):
        try:
            n = int(self._custom_var.get())
            if n < 3:
                n = 3
            if n > 30:
                n = 30
            self._door_count.set(n)
            self._door_label.config(text=f"Selected: {n} doors")
        except ValueError:
            pass

    def _start_game(self):
        doors = self._door_count.get()
        self._clear()
        GameScreen(self, doors, back_cb=self._show_startup)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()


# ─── Game Screen ─────────────────────────────────────────────────────────────
class GameScreen(tk.Frame):
    def __init__(self, master, num_doors, back_cb):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)
        self.num_doors   = num_doors
        self.back_cb     = back_cb

        # Stats
        self.stats = {"stay_wins": 0, "stay_total": 0,
                      "switch_wins": 0, "switch_total": 0}

        # Game state
        self.prize_door   = None
        self.chosen_door  = None
        self.revealed     = []   # doors Monty opened
        self.phase        = "pick"  # pick → switch_choice → result

        self._build_ui()
        self._new_round()

    # ── UI Construction ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=PANEL, pady=8, padx=16)
        topbar.pack(fill="x")

        tk.Button(topbar, text="← BACK", font=FONT_DOOR_S, bg=BG, fg=MUTED,
                  relief="flat", cursor="hand2",
                  command=self.back_cb).pack(side="left")

        tk.Label(topbar, text=f"MONTY HALL  ·  {self.num_doors} DOORS",
                 font=FONT_LABEL, bg=PANEL, fg=ACCENT).pack(side="left", padx=20)

        self.auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(topbar, text="Auto-simulate", variable=self.auto_var,
                       font=FONT_SMALL, bg=PANEL, fg=MUTED,
                       selectcolor=PANEL, activebackground=PANEL,
                       command=self._toggle_auto).pack(side="right", padx=8)

        self.speed_var = tk.IntVar(value=300)
        tk.Label(topbar, text="Speed:", font=FONT_SMALL,
                 bg=PANEL, fg=MUTED).pack(side="right", padx=(8, 0))
        tk.Scale(topbar, from_=50, to=1000, orient="horizontal",
                 variable=self.speed_var, bg=PANEL, fg=MUTED,
                 highlightthickness=0, length=100,
                 showvalue=False, troughcolor=DOOR_IDLE).pack(side="right")

        # Status message
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(self, textvariable=self.status_var,
                                   font=("Georgia", 13), bg=BG, fg=TEXT,
                                   wraplength=800)
        self.status_lbl.pack(pady=(18, 6))

        # Door canvas area (scrollable for many doors)
        self.door_outer = tk.Frame(self, bg=BG)
        self.door_outer.pack(fill="both", expand=True, padx=20)

        self.door_canvas = tk.Canvas(self.door_outer, bg=BG,
                                     highlightthickness=0, height=230)
        self.door_canvas.pack(side="left", fill="both", expand=True)

        vsb = tk.Scrollbar(self.door_outer, orient="vertical",
                           command=self.door_canvas.yview)
        if self.num_doors > 10:
            vsb.pack(side="right", fill="y")
        self.door_canvas.configure(yscrollcommand=vsb.set)

        self.door_frame = tk.Frame(self.door_canvas, bg=BG)
        self.door_canvas_window = self.door_canvas.create_window(
            (0, 0), window=self.door_frame, anchor="nw")
        self.door_frame.bind("<Configure>", self._on_frame_configure)
        self.door_canvas.bind("<Configure>", self._on_canvas_configure)

        # Action buttons
        self.action_frame = tk.Frame(self, bg=BG, pady=10)
        self.action_frame.pack()

        self.switch_btn = tk.Button(self.action_frame, text="🔄  SWITCH",
                                    font=FONT_BTN, bg=ACCENT2, fg=TEXT,
                                    relief="flat", padx=20, pady=8,
                                    activebackground="#e74c3c", cursor="hand2",
                                    command=lambda: self._make_choice("switch"))
        self.switch_btn.pack(side="left", padx=12)

        self.stay_btn = tk.Button(self.action_frame, text="🔒  STAY",
                                  font=FONT_BTN, bg="#2c6e49", fg=TEXT,
                                  relief="flat", padx=20, pady=8,
                                  activebackground="#3a9d6a", cursor="hand2",
                                  command=lambda: self._make_choice("stay"))
        self.stay_btn.pack(side="left", padx=12)

        self.next_btn = tk.Button(self.action_frame, text="▶  NEXT ROUND",
                                  font=FONT_BTN, bg=DOOR_IDLE, fg=MUTED,
                                  relief="flat", padx=20, pady=8,
                                  cursor="hand2",
                                  command=self._new_round)
        self.next_btn.pack(side="left", padx=12)

        # Stats panel
        stats_outer = tk.Frame(self, bg=PANEL, padx=20, pady=12)
        stats_outer.pack(fill="x", side="bottom")

        tk.Label(stats_outer, text="STATISTICS", font=FONT_LABEL,
                 bg=PANEL, fg=ACCENT).pack()

        row = tk.Frame(stats_outer, bg=PANEL)
        row.pack()

        self.stat_labels = {}
        for key, title, color in [
            ("stay_pct",   "STAY win %",   "#3a9d6a"),
            ("stay_wins",  "Stay wins",    TEXT),
            ("stay_total", "Stay games",   MUTED),
            ("switch_pct",   "SWITCH win %", ACCENT),
            ("switch_wins",  "Switch wins",  TEXT),
            ("switch_total", "Switch games", MUTED),
            ("total",        "Total rounds", MUTED),
        ]:
            col = tk.Frame(row, bg=PANEL, padx=16)
            col.pack(side="left")
            tk.Label(col, text=title, font=FONT_DOOR_S,
                     bg=PANEL, fg=MUTED).pack()
            lbl = tk.Label(col, text="—", font=FONT_STAT,
                           bg=PANEL, fg=color)
            lbl.pack()
            self.stat_labels[key] = lbl

        tk.Button(stats_outer, text="Reset Stats", font=FONT_DOOR_S,
                  bg=BG, fg=MUTED, relief="flat", cursor="hand2",
                  command=self._reset_stats).pack(side="right")

    def _on_frame_configure(self, e):
        self.door_canvas.configure(
            scrollregion=self.door_canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.door_canvas.itemconfig(
            self.door_canvas_window, width=e.width)

    # ── Door Widget ──────────────────────────────────────────────────────────
    def _build_doors(self):
        for w in self.door_frame.winfo_children():
            w.destroy()
        self.door_widgets = []

        cols = min(self.num_doors, 10)
        for i in range(self.num_doors):
            r, c = divmod(i, cols)
            dw = DoorWidget(self.door_frame, i, self._on_door_click)
            dw.grid(row=r, column=c, padx=8, pady=8)
            self.door_widgets.append(dw)

    # ── Game Logic ───────────────────────────────────────────────────────────
    def _new_round(self):
        self._cancel_auto()
        self.prize_door  = random.randint(0, self.num_doors - 1)
        self.chosen_door = None
        self.revealed    = []
        self.phase       = "pick"

        self._build_doors()
        self._set_buttons(pick=False, choice=False, next_=False)
        self.status_var.set("🚪  Pick a door — one hides a car, the rest hide goats.")
        self.status_lbl.config(fg=TEXT)

        for dw in self.door_widgets:
            dw.reset()

        if self.auto_var.get():
            self._schedule_auto()

    def _on_door_click(self, idx):
        if self.phase != "pick":
            return
        self._player_pick(idx)

    def _player_pick(self, idx):
        self.chosen_door = idx
        self.phase = "reveal"
        self.door_widgets[idx].set_chosen()

        # Monty reveals all goat doors except chosen and prize
        candidates = [i for i in range(self.num_doors)
                      if i != self.chosen_door and i != self.prize_door]
        # Reveal all but one
        to_reveal = random.sample(candidates, len(candidates) - 1) \
                    if len(candidates) > 1 else candidates
        self.revealed = to_reveal
        for i in to_reveal:
            self.door_widgets[i].reveal_goat()

        n_open = len(to_reveal)
        self.status_var.set(
            f"🐐  Monty opened {n_open} goat door{'s' if n_open > 1 else ''}! "
            f"Do you want to SWITCH or STAY?"
        )
        self._set_buttons(choice=True)
        self.phase = "switch_choice"

    def _make_choice(self, decision):
        if self.phase != "switch_choice":
            return
        self.phase = "result"
        self._set_buttons(next_=True)

        if decision == "switch":
            # Pick a random remaining un-revealed, non-chosen door
            remaining = [i for i in range(self.num_doors)
                         if i != self.chosen_door and i not in self.revealed]
            new_door = random.choice(remaining)
            self.door_widgets[self.chosen_door].set_unchosen()
            self.chosen_door = new_door
            self.door_widgets[new_door].set_chosen()

        won = (self.chosen_door == self.prize_door)

        # Reveal all doors
        for i, dw in enumerate(self.door_widgets):
            if i == self.chosen_door:
                dw.reveal_final(is_car=won, chosen=True)
            elif i not in self.revealed:
                dw.reveal_final(is_car=(i == self.prize_door), chosen=False)

        # Update stats
        if decision == "stay":
            self.stats["stay_total"] += 1
            if won:
                self.stats["stay_wins"] += 1
        else:
            self.stats["switch_total"] += 1
            if won:
                self.stats["switch_wins"] += 1

        self._update_stats()

        emoji = "🎉" if won else "🐐"
        result = "WIN! You got the car!" if won else "LOSS. It was a goat."
        self.status_var.set(f"{emoji}  {result}  (You chose to {decision.upper()})")
        self.status_lbl.config(fg=ACCENT if won else ACCENT2)

        if self.auto_var.get():
            self._schedule_auto()

    def _update_stats(self):
        s = self.stats
        stay_pct   = (s["stay_wins"]   / s["stay_total"]   * 100) if s["stay_total"]   else 0
        switch_pct = (s["switch_wins"] / s["switch_total"] * 100) if s["switch_total"] else 0
        total = s["stay_total"] + s["switch_total"]

        self.stat_labels["stay_pct"].config(   text=f"{stay_pct:.1f}%")
        self.stat_labels["stay_wins"].config(  text=str(s["stay_wins"]))
        self.stat_labels["stay_total"].config( text=str(s["stay_total"]))
        self.stat_labels["switch_pct"].config( text=f"{switch_pct:.1f}%")
        self.stat_labels["switch_wins"].config(text=str(s["switch_wins"]))
        self.stat_labels["switch_total"].config(text=str(s["switch_total"]))
        self.stat_labels["total"].config(      text=str(total))

    def _reset_stats(self):
        self.stats = {"stay_wins": 0, "stay_total": 0,
                      "switch_wins": 0, "switch_total": 0}
        self._update_stats()

    def _set_buttons(self, pick=False, choice=False, next_=False):
        state_choice = "normal" if choice else "disabled"
        state_next   = "normal" if next_   else "disabled"
        self.switch_btn.config(state=state_choice,
                               fg=TEXT if choice else MUTED)
        self.stay_btn.config(  state=state_choice,
                               fg=TEXT if choice else MUTED)
        self.next_btn.config(  state=state_next,
                               fg=TEXT if next_ else MUTED,
                               bg=ACCENT if next_ else DOOR_IDLE)

    # ── Auto-simulate ────────────────────────────────────────────────────────
    def _toggle_auto(self):
        if self.auto_var.get():
            self._schedule_auto()
        else:
            self._cancel_auto()

    def _auto_job_id(self):
        return getattr(self, "_auto_id", None)

    def _schedule_auto(self):
        delay = self.speed_var.get()
        self._auto_id = self.after(delay, self._auto_step)

    def _cancel_auto(self):
        if hasattr(self, "_auto_id") and self._auto_id:
            self.after_cancel(self._auto_id)
            self._auto_id = None

    def _auto_step(self):
        if not self.auto_var.get():
            return
        if self.phase == "pick":
            self._player_pick(random.randint(0, self.num_doors - 1))
            self._schedule_auto()
        elif self.phase == "switch_choice":
            self._make_choice(random.choice(["switch", "stay"]))
        elif self.phase == "result":
            self._new_round()


# ─── Door Widget ──────────────────────────────────────────────────────────────
class DoorWidget(tk.Frame):
    W, H = 80, 130

    def __init__(self, parent, idx, click_cb):
        super().__init__(parent, bg=BG)
        self.idx      = idx
        self.click_cb = click_cb
        self._build()

    def _build(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                bg=BG, highlightthickness=0,
                                cursor="hand2")
        self.canvas.pack()
        self.lbl = tk.Label(self, text=f"#{self.idx + 1}",
                            font=FONT_DOOR_S, bg=BG, fg=MUTED)
        self.lbl.pack()
        self.canvas.bind("<Button-1>", lambda e: self.click_cb(self.idx))
        self.canvas.bind("<Enter>", self._hover_in)
        self.canvas.bind("<Leave>", self._hover_out)
        self._draw_door(DOOR_IDLE)

    def _draw_door(self, color, label="?", label_color=TEXT,
                   knob=True, frame_color=None):
        c = self.canvas
        c.delete("all")
        fc = frame_color or self._darken(color)
        # Door body
        c.create_rectangle(6, 10, self.W - 6, self.H - 6,
                            fill=color, outline=fc, width=2)
        # Door panels (decorative)
        c.create_rectangle(12, 16, self.W - 12, self.H // 2 - 4,
                            fill=self._darken(color, 0.08),
                            outline=fc, width=1)
        c.create_rectangle(12, self.H // 2 + 4, self.W - 12, self.H - 16,
                            fill=self._darken(color, 0.08),
                            outline=fc, width=1)
        # Knob
        if knob:
            c.create_oval(self.W - 22, self.H // 2 - 5,
                          self.W - 14, self.H // 2 + 5,
                          fill=ACCENT, outline="")
        # Label
        c.create_text(self.W // 2, self.H // 2,
                      text=label, font=FONT_DOOR,
                      fill=label_color)

    def _darken(self, hex_color, pct=0.25):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - pct)))
        g = max(0, int(g * (1 - pct)))
        b = max(0, int(b * (1 - pct)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def reset(self):
        self._draw_door(DOOR_IDLE)
        self.lbl.config(fg=MUTED)
        self.canvas.config(cursor="hand2")

    def set_chosen(self):
        self._draw_door(DOOR_HL, "?", ACCENT)
        self.lbl.config(fg=ACCENT)

    def set_unchosen(self):
        self._draw_door(DOOR_IDLE)
        self.lbl.config(fg=MUTED)

    def reveal_goat(self):
        self._draw_door(DOOR_OPEN, "🐐", MUTED, knob=False,
                        frame_color="#111")
        self.canvas.config(cursor="")

    def reveal_final(self, is_car, chosen):
        if is_car:
            color = DOOR_GOOD
            label = "🚗"
            lc    = "#4ade80"
        else:
            color = DOOR_BAD
            label = "🐐"
            lc    = ACCENT2
        frame = ACCENT if chosen else None
        self._draw_door(color, label, lc, knob=False, frame_color=frame)
        if chosen:
            # highlight chosen door
            self.canvas.create_rectangle(2, 2, self.W - 2, self.H - 2,
                                         outline=ACCENT, width=3)
        self.canvas.config(cursor="")

    def _hover_in(self, e):
        c = self.canvas
        items = c.find_all()
        if items:
            # just brighten the border
            c.create_rectangle(2, 2, self.W - 2, self.H - 2,
                               outline=ACCENT, width=2, tags="hover")

    def _hover_out(self, e):
        self.canvas.delete("hover")


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MontyHallApp()
    app.mainloop()
