"""
House Flipper · Copiloto Platina
Executável desktop com CustomTkinter + SQLite
"""

import customtkinter as ctk
import sqlite3
import sys
from pathlib import Path

# ─── Persistência ───────────────────────────────────────────────────────────
def get_db_path():
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / "progresso.db"

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        done INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS counters (
        key TEXT PRIMARY KEY,
        value INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def load_tasks():
    conn = sqlite3.connect(get_db_path())
    rows = conn.execute("SELECT id, done FROM tasks").fetchall()
    conn.close()
    return {r[0]: bool(r[1]) for r in rows}

def save_task(task_id, done):
    conn = sqlite3.connect(get_db_path())
    conn.execute("INSERT OR REPLACE INTO tasks (id, done) VALUES (?, ?)",
                 (task_id, int(done)))
    conn.commit()
    conn.close()

def load_counter(key):
    conn = sqlite3.connect(get_db_path())
    row = conn.execute("SELECT value FROM counters WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else 0

def save_counter(key, value):
    conn = sqlite3.connect(get_db_path())
    conn.execute("INSERT OR REPLACE INTO counters (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def reset_db():
    conn = sqlite3.connect(get_db_path())
    conn.execute("DELETE FROM tasks")
    conn.execute("DELETE FROM counters")
    conn.commit()
    conn.close()

# ─── Dados ──────────────────────────────────────────────────────────────────
PHASES = [
    {
        "id": "prep", "icon": "⚡", "title": "Fase 0 · Preparação",
        "color": "#4f8dff",
        "tasks": [
            {"id": "p1", "label": "Alterar moeda para EURO (€)",
             "tip": "Evita bugs no troféu Negotiator."},
            {"id": "p2", "label": "Desativar / Remover DLCs",
             "tip": "Garante Perfectionist e Game Over sem jobs extras das expansões."},
            {"id": "p3", "label": "Priorizar Perks essenciais",
             "tip": "Focar em: Visão Penetrante, Longo Alcance, Pintura Básica, Azulejista e Pagamento Superior."},
        ]
    },
    {
        "id": "orders", "icon": "💼", "title": "Fase 1 · Ordens (100%)",
        "color": "#34d399",
        "tasks": [
            {"id": "o1", "label": "Completar 1º Job (First Money)",
             "trophy": "First Money"},
            {"id": "o2", "label": "Levantar carro no job 'Cleaning the Garage'",
             "trophy": "Strongman"},
            {"id": "o3", "label": "Bater no carro com martelo no job 'Bathroom & Workshop'",
             "trophy": "Car Mechanic"},
            {"id": "o4", "label": "Fechar TODAS as ordens em 100%",
             "trophy": "Perfectionist",
             "tip": "Verifique o Mail Archive. Não saia de jobs antigos com menos de 100%."},
            {"id": "o5", "label": "Repetir 'Cleaning the Garage' em menos de 30 segundos",
             "trophy": "Do it ASAP",
             "tip": "Faça após maximizar perks de limpeza."},
        ]
    },
    {
        "id": "buyers", "icon": "🏡", "title": "Fase 2 · Compradores Alvo",
        "color": "#a855f7",
        "tasks": [
            {"id": "b1",  "label": "Family House  →  Smoth Family",
             "trophy": "Pro-creative",      "tip": "Comprar e vender imediatamente."},
            {"id": "b2",  "label": "Turtle House  →  Raphael Erko",
             "trophy": "Alpha Male",        "tip": "Comprar e vender imediatamente."},
            {"id": "b3",  "label": "Man Cave  →  Jonson Family",
             "trophy": "Family Man",        "tip": "Comprar e vender imediatamente."},
            {"id": "b4",  "label": "Alleyway of Lights  →  Veronica Liptson",
             "trophy": "Artistic Soul",     "tip": "Comprar e vender imediatamente."},
            {"id": "b5",  "label": "House with Uninvited Guests  →  Jantart Family",
             "trophy": "Just Enough",       "tip": "Venda a cama e venda a casa."},
            {"id": "b6",  "label": "Burned House  →  Dolan Trusk",
             "trophy": "Worth Every Penny", "tip": "Lixo fora, limpar tudo, 2 tomadas, vender cama e sofá."},
            {"id": "b7",  "label": "Home Admin-Legends  →  Jimmy Traitor",
             "trophy": "Mr. Mystery",       "tip": "NAO LIMPAR. Adicionar 1 coffee table barata."},
            {"id": "b8",  "label": "Just Married's House  →  Gorgio Shanua",
             "trophy": "I'm a Belieber",    "tip": "Remover cozinha, adicionar 1 wardrobe."},
            {"id": "b9",  "label": "Sellers / Huckster's House  →  Jack Tarinton",
             "trophy": "Wall Street Shark", "tip": "Bater na porta (Knock Knock), tirar pia cozinha, sofa Henry, TV na parede, pia Pryzmat, 2 vasos sanitarios."},
            {"id": "b10", "label": "Abandoned House  →  Chang Choi",
             "trophy": "Geek",              "tip": "Ver aba 'Chang Choi Guide' para o guia completo."},
        ]
    },
    {
        "id": "gameover", "icon": "🏠", "title": "Fase 3 · Game Over",
        "color": "#f87171",
        "tasks": [
            {"id": "g1", "label": "Mudar escritório para outra casa",
             "tip": "Necessário para conseguir vender o First Office."},
            {"id": "g2", "label": "Vender First Office (venda 'crua', sem reformar)",
             "tip": "Estado da casa não importa."},
            {"id": "g3", "label": "Vender TODAS as casas restantes (1 vez cada)",
             "trophy": "Game Over",
             "tip": "Estado da casa não importa. Venda tudo o mais rápido possível."},
        ]
    },
    {
        "id": "grind", "icon": "🏆", "title": "Fase 4 · Grind Final",
        "color": "#f59e0b",
        "tasks": [
            {"id": "f1", "label": "Negociar lucro máximo na 'Alone Home'",
             "trophy": "Negotiator",
             "tip": "Use Price Negotiation no máximo. Precisa de lucro real na negociação."},
            {"id": "f2", "label": "Acumular 1 milhão em 'House hiding something'",
             "trophy": "Millionaire",
             "tip": "Sala secreta atrás do quadro de energia. Venda os itens raros de lá."},
            {"id": "f3", "label": "Completar 50 vendas de imóveis no total",
             "trophy": "Senior Estate Agent",
             "tip": "Repita a compra e venda do First Office ou da Turtle House para farmar rápido."},
        ]
    },
]

CHANG_STEPS = [
    {"id": "c1",  "text": "Comprar a Abandoned House"},
    {"id": "c2",  "text": "Remover todo o lixo e matar as baratas"},
    {"id": "c3",  "text": "Derrubar as paredes internas permitidas"},
    {"id": "c4",  "text": "Vender todos os móveis e itens (EXCETO a Green Mantis Bed)"},
    {"id": "c5",  "text": "Limpar paredes, chão e teto completamente"},
    {"id": "c6",  "text": "Adicionar: 1x Corner Desk"},
    {"id": "c7",  "text": "Adicionar: 1x Venne Horizontal Bookcase"},
    {"id": "c8",  "text": "Adicionar: 1x Bookcase Lim"},
    {"id": "c9",  "text": "Adicionar: 1x Shaped Foam for Children Cube"},
    {"id": "c10", "text": "Adicionar: 1x Foam Bridge Mold for Children"},
    {"id": "c11", "text": "Colocar à venda — esperar Chang Choi aparecer em 1º lugar na lista"},
]

# ─── Cores ───────────────────────────────────────────────────────────────────
BG      = "#0a0c12"
SURFACE = "#11141f"
CARD    = "#181c2a"
BORDER  = "#232840"
ACCENT  = "#4f8dff"
ACCENT2 = "#a855f7"
GOLD    = "#f59e0b"
GREEN   = "#34d399"
RED     = "#f87171"
MUTED   = "#6b7280"
TEXT    = "#e2e8f0"
DONE_BG = "#0f1e38"
TASK_BG = "#1e2235"   # substitui "#ffffff08" — alpha hex não é suportado pelo Tkinter

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def make_scrollable(parent):
    return ctk.CTkScrollableFrame(
        parent, fg_color=BG,
        scrollbar_button_color=BORDER,
        scrollbar_button_hover_color=ACCENT
    )

# ─── App ─────────────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("House Flipper")
        self.geometry("1040x740")
        self.minsize(820, 600)
        self.configure(fg_color=BG)

        init_db()
        # CORRIGIDO: renomeado self.state → self.task_state
        # (self.state conflitava com método interno do Tkinter)
        self.task_state   = load_tasks()
        self.sales        = load_counter("sales")
        self.task_widgets = {}

        self._build_ui()
        self._refresh_ring()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, width=215)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.main_area = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self._build_page_fases()
        self._build_page_chang()
        self._build_page_tracker()
        self.show_page("fases")

    # ── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="🏠", font=("Helvetica", 36)).pack(pady=(30, 4))
        ctk.CTkLabel(self.sidebar, text="House Flipper",
                      font=("Helvetica", 15, "bold"), text_color="#fff").pack(padx=20)

        # Anel de progresso — bg precisa ser cor sólida (sem alpha)
        self.ring_canvas = ctk.CTkCanvas(self.sidebar, width=110, height=110,
                                          bg=SURFACE, highlightthickness=0)
        self.ring_canvas.pack(pady=20)
        self.ring_pct_var = ctk.StringVar(value="0%")
        ctk.CTkLabel(self.sidebar, textvariable=self.ring_pct_var,
                      font=("Helvetica", 13, "bold"), text_color=ACCENT).pack()
        ctk.CTkLabel(self.sidebar, text="progresso total",
                      font=("Helvetica", 10), text_color=MUTED).pack(pady=(0, 20))

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=4)

        nav_items = [
            ("📋  Fases & Tarefas",    "fases"),
            ("🎮  Chang Choi Guide",   "chang"),
            ("📊  Contador de Vendas", "tracker"),
        ]
        self.nav_btns = {}
        for text, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w",
                font=("Helvetica", 13), height=42,
                fg_color="transparent", hover_color=BORDER,
                text_color=MUTED, corner_radius=8,
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_btns[key] = btn

        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True, fill="both")
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=4)
        ctk.CTkButton(
            self.sidebar, text="🗑  Resetar Progresso",
            font=("Helvetica", 11), fg_color="transparent",
            hover_color="#2a1010", text_color=MUTED, height=36,
            command=self._reset
        ).pack(padx=12, pady=(0, 20))

    def _draw_ring(self, pct):
        c = self.ring_canvas
        c.delete("all")
        x, y, r = 55, 55, 42
        c.create_oval(x-r, y-r, x+r, y+r, outline="#1e2540", width=8)
        if pct > 0:
            extent = 359.9 * pct / 100
            c.create_arc(x-r, y-r, x+r, y+r, start=90, extent=-extent,
                          outline=ACCENT, width=8, style="arc")

    def _refresh_ring(self):
        all_ids = ([t["id"] for p in PHASES for t in p["tasks"]]
                   + [s["id"] for s in CHANG_STEPS])
        done = sum(1 for i in all_ids if self.task_state.get(i))
        pct  = round(done / len(all_ids) * 100) if all_ids else 0
        self._draw_ring(pct)
        self.ring_pct_var.set(f"{pct}%")

    # ── Navegação ────────────────────────────────────────────────────────────
    def show_page(self, key):
        for frame in self.pages.values():
            frame.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        for k, btn in self.nav_btns.items():
            btn.configure(
                text_color=TEXT   if k == key else MUTED,
                fg_color  =BORDER if k == key else "transparent"
            )

    # ── Página: Fases ─────────────────────────────────────────────────────────
    def _build_page_fases(self):
        page = make_scrollable(self.main_area)
        self.pages["fases"] = page

        ctk.CTkLabel(page, text="Fases & Tarefas",
                      font=("Helvetica", 22, "bold"), text_color="#fff"
                      ).pack(anchor="w", padx=28, pady=(28, 8))

        # Alertas
        alerts = ctk.CTkFrame(page, fg_color="transparent")
        alerts.pack(fill="x", padx=28, pady=(0, 16))
        alerts.columnconfigure(0, weight=1)
        alerts.columnconfigure(1, weight=1)

        def alert_card(col, icon, title, body, border_color):
            f = ctk.CTkFrame(alerts, fg_color=CARD, corner_radius=12,
                              border_width=1, border_color=border_color)
            f.grid(row=0, column=col,
                   padx=(0, 6) if col == 0 else (6, 0),
                   pady=4, sticky="nsew")
            ctk.CTkLabel(f, text=f"{icon}  {title}",
                          font=("Helvetica", 12, "bold"),
                          text_color="#fff", anchor="w"
                          ).pack(anchor="w", padx=14, pady=(12, 3))
            ctk.CTkLabel(f, text=body,
                          font=("Helvetica", 11), text_color=MUTED,
                          anchor="w", wraplength=340, justify="left"
                          ).pack(anchor="w", padx=14, pady=(0, 12))

        alert_card(0, "⚠️", "Regra de Ouro",
                   "Não limpe janelas nem se preocupe com decoração. "
                   "Largue os objetos pedidos no chão.", "#fb923c")
        alert_card(1, "🎨", "Dica de Cor",
                   "Em ordens com várias cores, use apenas 1 cor. "
                   "O jogo aceita para fechar os 100%.", ACCENT)

        for phase in PHASES:
            self._build_phase_block(page, phase)

    def _build_phase_block(self, parent, phase):
        color = phase["color"]

        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14,
                             border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=28, pady=8)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=18, pady=14)

        ctk.CTkLabel(hdr, text=phase["icon"],
                      font=("Helvetica", 18)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(hdr, text=phase["title"],
                      font=("Helvetica", 14, "bold"), text_color="#fff").pack(side="left")

        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right")

        pct_var = ctk.StringVar(value="0%")
        ctk.CTkLabel(right, textvariable=pct_var,
                      font=("Helvetica", 11, "bold"), text_color=color, width=36
                      ).pack(side="right", padx=(6, 0))
        prog_bar = ctk.CTkProgressBar(right, width=100, height=6,
                                       progress_color=color, fg_color="#1e2540")
        prog_bar.pack(side="right")
        prog_bar.set(0)

        ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(fill="x", padx=18)

        task_body = ctk.CTkFrame(card, fg_color="transparent")
        task_body.pack(fill="x", padx=14, pady=10)

        phase_ids = [t["id"] for t in phase["tasks"]]

        def refresh_phase():
            n_done = sum(1 for tid in phase_ids if self.task_state.get(tid))
            pct    = n_done / len(phase_ids) if phase_ids else 0
            prog_bar.set(pct)
            pct_var.set(f"{int(pct * 100)}%")

        for task in phase["tasks"]:
            self._build_task_row(
                task_body, task, color,
                on_change=lambda: (refresh_phase(), self._refresh_ring())
            )
        refresh_phase()

    def _build_task_row(self, parent, task, accent_color, on_change=None):
        done = self.task_state.get(task["id"], False)
        var  = ctk.BooleanVar(value=done)

        # CORRIGIDO: "#ffffff08" → TASK_BG (Tkinter não suporta alpha em hex)
        row = ctk.CTkFrame(parent,
                            fg_color    =DONE_BG  if done else TASK_BG,
                            corner_radius=10,
                            border_width=1,
                            border_color="#1d3d70" if done else BORDER)
        row.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        cb = ctk.CTkCheckBox(
            inner, text="", variable=var,
            width=20, height=20,
            checkbox_width=20, checkbox_height=20, corner_radius=10,
            checkmark_color="#fff", fg_color=accent_color,
            hover_color=accent_color, border_color=MUTED, border_width=2,
            command=lambda: self._toggle(task["id"], var, row, label_w, on_change)
        )
        cb.pack(side="left", padx=(0, 12))

        txt_col = ctk.CTkFrame(inner, fg_color="transparent")
        txt_col.pack(side="left", fill="both", expand=True)

        label_row = ctk.CTkFrame(txt_col, fg_color="transparent")
        label_row.pack(fill="x")

        label_w = ctk.CTkLabel(
            label_row, text=task["label"],
            font=("Helvetica", 13),
            text_color=MUTED if done else TEXT,
            anchor="w", wraplength=560
        )
        label_w.pack(side="left")

        if task.get("trophy"):
            ctk.CTkLabel(
                label_row, text=f"🏆 {task['trophy']}",
                font=("Helvetica", 10, "bold"),
                text_color=GOLD, fg_color="#2a1c00", corner_radius=10
            ).pack(side="left", padx=(8, 0))

        if task.get("tip") and not done:
            ctk.CTkLabel(
                txt_col, text=f"ℹ  {task['tip']}",
                font=("Helvetica", 11, "italic"),
                text_color="#60a5fa", anchor="w", wraplength=540
            ).pack(fill="x", pady=(3, 0))

        self.task_widgets[task["id"]] = (var, row, label_w)

    def _toggle(self, task_id, var, row, label_w, on_change=None):
        done = var.get()
        self.task_state[task_id] = done
        save_task(task_id, done)
        # CORRIGIDO: "#ffffff08" → TASK_BG
        row.configure(
            fg_color    =DONE_BG  if done else TASK_BG,
            border_color="#1d3d70" if done else BORDER
        )
        label_w.configure(text_color=MUTED if done else TEXT)
        if on_change:
            on_change()

    # ── Página: Chang Choi ───────────────────────────────────────────────────
    def _build_page_chang(self):
        page = make_scrollable(self.main_area)
        self.pages["chang"] = page

        ctk.CTkLabel(page, text="Guia: Chang Choi — O Geek",
                      font=("Helvetica", 22, "bold"), text_color="#fff"
                      ).pack(anchor="w", padx=28, pady=(28, 16))

        # CORRIGIDO: "#a855f750" → "#a855f7" (alpha hex inválido)
        info = ctk.CTkFrame(page, fg_color="#1a0a30", corner_radius=14,
                             border_width=1, border_color="#a855f7")
        info.pack(fill="x", padx=28, pady=(0, 16))
        ctk.CTkLabel(info, text="🎮  Sobre Chang Choi",
                      font=("Helvetica", 14, "bold"), text_color="#c084fc"
                      ).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            info,
            text=("Este é o comprador mais instável do jogo. Use a Abandoned House.\n"
                  "Ele adora cores verdes, móveis infantis e itens de escritório.\n"
                  "Não precisa ganhar o leilão — basta ele aparecer em 1º na lista lateral ao vender."),
            font=("Helvetica", 12), text_color="#d8b4fe",
            wraplength=700, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 16))

        badge_row = ctk.CTkFrame(page, fg_color="transparent")
        badge_row.pack(fill="x", padx=28, pady=(0, 12))
        ctk.CTkLabel(badge_row, text="🏆  Troféu desbloqueado: Geek",
                      font=("Helvetica", 13, "bold"),
                      text_color=GOLD, fg_color="#2a1c00", corner_radius=20
                      ).pack(side="left")

        card = ctk.CTkFrame(page, fg_color=CARD, corner_radius=14,
                             border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=28, pady=(0, 28))

        for i, step in enumerate(CHANG_STEPS, 1):
            done = self.task_state.get(step["id"], False)
            var  = ctk.BooleanVar(value=done)

            row = ctk.CTkFrame(card,
                                fg_color=DONE_BG if done else "transparent",
                                corner_radius=10)
            row.pack(fill="x", padx=14, pady=4)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            ctk.CTkLabel(inner, text=f"{i:02d}",
                          font=("Helvetica", 12, "bold"),
                          text_color=ACCENT2, width=28).pack(side="left")

            cb = ctk.CTkCheckBox(
                inner, text="", variable=var,
                width=20, height=20,
                checkbox_width=20, checkbox_height=20, corner_radius=10,
                checkmark_color="#fff", fg_color=ACCENT2,
                hover_color=ACCENT2, border_color=MUTED, border_width=2
            )
            cb.pack(side="left", padx=(4, 12))

            lbl = ctk.CTkLabel(inner, text=step["text"],
                                font=("Helvetica", 13),
                                text_color=MUTED if done else TEXT, anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            def make_cmd(sid, v, r, l):
                def cmd():
                    d = v.get()
                    self.task_state[sid] = d
                    save_task(sid, d)
                    r.configure(fg_color=DONE_BG if d else "transparent")
                    l.configure(text_color=MUTED if d else TEXT)
                    self._refresh_ring()
                return cmd

            cb.configure(command=make_cmd(step["id"], var, row, lbl))

    # ── Página: Tracker ──────────────────────────────────────────────────────
    def _build_page_tracker(self):
        page = make_scrollable(self.main_area)
        self.pages["tracker"] = page

        ctk.CTkLabel(page, text="Contador de Vendas",
                      font=("Helvetica", 22, "bold"), text_color="#fff"
                      ).pack(anchor="w", padx=28, pady=(28, 4))
        ctk.CTkLabel(page,
                      text="Objetivo: 50 vendas  →  Troféu: Senior Estate Agent",
                      font=("Helvetica", 12), text_color=MUTED
                      ).pack(anchor="w", padx=28, pady=(0, 20))

        card = ctk.CTkFrame(page, fg_color=CARD, corner_radius=16,
                             border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=28, pady=(0, 20))

        counter_row = ctk.CTkFrame(card, fg_color="transparent")
        counter_row.pack(pady=36)

        ctk.CTkButton(
            counter_row, text="−", width=52, height=52, corner_radius=26,
            font=("Helvetica", 22, "bold"),
            fg_color=SURFACE, hover_color=BORDER,
            text_color=TEXT, border_width=1, border_color=BORDER,
            command=self._dec_sales
        ).pack(side="left", padx=16)

        self.sales_var = ctk.StringVar(value=str(self.sales).zfill(2))
        ctk.CTkLabel(counter_row, textvariable=self.sales_var,
                      font=("Helvetica", 72, "bold"),
                      text_color=ACCENT, width=160).pack(side="left")

        ctk.CTkButton(
            counter_row, text="+", width=52, height=52, corner_radius=26,
            font=("Helvetica", 22, "bold"),
            fg_color=ACCENT, hover_color="#3a72e0", text_color="#fff",
            command=self._inc_sales
        ).pack(side="left", padx=16)

        bar_frame = ctk.CTkFrame(card, fg_color="transparent")
        bar_frame.pack(pady=(0, 28), padx=40, fill="x")

        self.sales_prog = ctk.CTkProgressBar(bar_frame, height=8,
                                              progress_color=ACCENT, fg_color="#1e2540")
        self.sales_prog.pack(fill="x", pady=(0, 8))
        self.sales_prog.set(min(1.0, self.sales / 50))

        self.sales_prog_label = ctk.CTkLabel(
            bar_frame, text=f"{self.sales} / 50 vendas",
            font=("Helvetica", 12), text_color=MUTED
        )
        self.sales_prog_label.pack()

        # Cards de dicas
        # CORRIGIDO: assinatura tip_card(col, icon, title, bullets, color)
        # e chamadas com argumentos na ordem certa
        tips_frame = ctk.CTkFrame(page, fg_color="transparent")
        tips_frame.pack(fill="x", padx=28, pady=(0, 28))
        tips_frame.columnconfigure(0, weight=1)
        tips_frame.columnconfigure(1, weight=1)

        def tip_card(col, icon, title, bullets, color):
            f = ctk.CTkFrame(tips_frame, fg_color=CARD, corner_radius=14,
                              border_width=1, border_color=BORDER)
            f.grid(row=0, column=col,
                   padx=(0, 6) if col == 0 else (6, 0),
                   sticky="nsew")
            ctk.CTkLabel(f, text=f"{icon}  {title}",
                          font=("Helvetica", 13, "bold"), text_color=color
                          ).pack(anchor="w", padx=16, pady=(14, 6))
            for b in bullets:
                ctk.CTkLabel(f, text=f"→  {b}",
                              font=("Helvetica", 11), text_color=MUTED,
                              anchor="w", wraplength=320, justify="left"
                              ).pack(anchor="w", padx=16, pady=2)
            ctk.CTkFrame(f, fg_color="transparent", height=10).pack()

        tip_card(
            0, "💰", "Dicas de Dinheiro",
            [
                "Vender itens pedidos aumenta bastante o lucro.",
                "House hiding something tem itens valiosos na sala secreta (atrás do quadro de energia).",
                "Alone Home é o melhor custo-benefício para lucro rápido.",
            ],
            GREEN
        )
        tip_card(
            1, "⏱", "Dicas de Tempo",
            [
                "Pinte apenas o necessário — ignore caixilhos de janela.",
                "Use a ferramenta de venda (scanner) para limpar lixo rapidamente.",
                "Para o troféu Game Over, venda as casas no estado em que comprou.",
            ],
            ACCENT
        )

    def _inc_sales(self):
        self.sales += 1
        save_counter("sales", self.sales)
        self._update_sales_ui()

    def _dec_sales(self):
        if self.sales > 0:
            self.sales -= 1
            save_counter("sales", self.sales)
            self._update_sales_ui()

    def _update_sales_ui(self):
        self.sales_var.set(str(self.sales).zfill(2))
        self.sales_prog.set(min(1.0, self.sales / 50))
        self.sales_prog_label.configure(text=f"{self.sales} / 50 vendas")

    # ── Reset ────────────────────────────────────────────────────────────────
    def _reset(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirmar reset")
        dlg.geometry("360x170")
        dlg.configure(fg_color=CARD)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Resetar todo o progresso?",
                      font=("Helvetica", 15, "bold"), text_color="#fff"
                      ).pack(pady=(28, 6))
        ctk.CTkLabel(dlg, text="Esta ação não pode ser desfeita.",
                      font=("Helvetica", 12), text_color=MUTED).pack()

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(pady=22)

        ctk.CTkButton(btns, text="Cancelar", width=120,
                       fg_color=SURFACE, hover_color=BORDER,
                       command=dlg.destroy).pack(side="left", padx=8)

        def do_reset():
            reset_db()
            self.task_state.clear()
            self.sales = 0
            dlg.destroy()
            self.destroy()
            main()

        ctk.CTkButton(btns, text="Resetar", width=120,
                       fg_color=RED, hover_color="#c0392b",
                       command=do_reset).pack(side="left", padx=8)


# ─── Entrypoint ──────────────────────────────────────────────────────────────
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
