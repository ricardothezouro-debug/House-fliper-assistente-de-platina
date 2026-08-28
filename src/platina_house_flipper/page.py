"""Página do guia: as 10 abas, com progresso, busca global e imagens."""
from __future__ import annotations

import html
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)

from . import guide_data
from . import progress as keys
from .image_loader import ImageLoader
from .storage import load_progress, save_progress

_IMG_MAX_W = 620
_IMG_MAX_H = 420
_PORTRAIT = 116
_ICON = 56
_IMG_TIMEOUT_MS = 26000
_SEARCH_LIMIT = 18
_SALES_PER_ROW = 10

_TIER_COLORS = {
    "bronze": "#C77B3B",
    "prata": "#B8C0CC",
    "ouro": "#E7C64A",
    "platina": "#7FE7FF",
}

_PROGRESS_QSS = (
    "QProgressBar{background:#0B111A;border:1px solid #273140;border-radius:9px;"
    "min-height:18px;text-align:center;color:#F3F6FF;font-weight:600}"
    "QProgressBar::chunk{border-radius:8px;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
    "stop:0 #37F2FF,stop:0.5 #B9FF43,stop:1 #FF4FD8)}"
)

_NAV_QSS = (
    "QPushButton#NavButton{background:#0D121B;border:1px solid #273140;border-radius:8px;"
    "padding:7px 10px;color:#A8B0BC;text-align:left}"
    "QPushButton#NavButton:hover{border-color:#3C4A5C;color:#F3F6FF}"
    "QPushButton#NavButton:checked{background:#101922;border-color:%s;color:#F3F6FF;font-weight:600}"
    % guide_data.ACCENT
)

_PHASE_QSS = (
    "QPushButton#PhaseHead{background:#101922;border:1px solid #273140;border-radius:9px;"
    "padding:10px 12px;color:#F3F6FF;text-align:left;font-weight:600}"
    "QPushButton#PhaseHead:hover{border-color:%s}" % guide_data.ACCENT
)


def _norm(text) -> str:
    """Minúsculas sem acento, para busca tolerante."""
    stripped = unicodedata.normalize("NFD", str(text or ""))
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


def _esc(text) -> str:
    """Escapa o texto do guia antes de entrar em um QLabel com rich text."""
    return html.escape(str(text or ""))


def _flat(value) -> str:
    """Junta dict/list/str num texto único, para alimentar a busca."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_flat(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return " ".join(_flat(v) for v in value)
    return str(value)


def _label(text: str, object_name: str = "", wrap: bool = True) -> QLabel:
    label = QLabel(str(text or ""))
    if object_name:
        label.setObjectName(object_name)
    label.setWordWrap(wrap)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    return label


def _link(text: str, url: str) -> QLabel:
    label = QLabel(
        f'<a href="{_esc(url)}" style="color:{guide_data.ACCENT}">{_esc(text)}</a>'
    )
    label.setOpenExternalLinks(True)
    label.setWordWrap(True)
    return label


def _card() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("NeonPanel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(6)
    return frame, layout


def _notice(text: str, tone: str = "info") -> QFrame:
    frame = QFrame()
    frame.setObjectName("NeonPanel")
    color = "#F87171" if tone == "red" else guide_data.ACCENT
    frame.setStyleSheet(
        "QFrame{background:#0D121B;border:1px solid #273140;"
        "border-left:3px solid %s;border-radius:10px}" % color
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 11, 14, 11)
    layout.addWidget(_label(text, "Muted"))
    return frame


def _pill(text: str) -> QLabel:
    label = QLabel(str(text or ""))
    label.setObjectName("StatusPill")
    label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return label


def _tier(tier: str) -> QLabel:
    label = QLabel(str(tier or "").upper())
    label.setStyleSheet(
        "color:%s;font-weight:700;font-size:11px;" % _TIER_COLORS.get(tier, "#A8B0BC")
    )
    label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return label


def _detail(layout: QVBoxLayout, title: str, value: str) -> None:
    """Linha “rótulo → valor”."""
    if not value:
        return
    row = QLabel(f"<b>{_esc(title)}:</b> {_esc(value)}")
    row.setObjectName("Muted")
    row.setWordWrap(True)
    row.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    layout.addWidget(row)


def _scroll_page(build_content) -> QWidget:
    """Wrapper de aba: um QScrollArea vertical com o conteúdo dentro."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 10, 0)
    layout.setSpacing(12)
    build_content(layout)
    layout.addStretch(1)

    scroll = QScrollArea()
    scroll.setObjectName("PageScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(container)
    return scroll


class GuidePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._done = load_progress()
        self._image_loader = ImageLoader(self)
        self._boxes: dict[str, list[QCheckBox]] = {}
        self._built: set[int] = set()
        self._phase_pills: list[tuple[QLabel, list[str]]] = []
        self._trophy_rows: list[tuple[QWidget, str, str]] = []
        self._house_rows: list[tuple[QWidget, str, int]] = []
        self._buyer_rows: list[tuple[QWidget, str]] = []
        self._sales_label: QLabel | None = None
        self._section_index = {s["key"]: i for i, s in enumerate(guide_data.SECTIONS)}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 22, 0)
        outer.setSpacing(12)
        self._build_header(outer)
        self._build_search(outer)
        self._build_progress(outer)
        self._build_toolbar(outer)
        self._build_nav(outer)

        self.stack = QStackedWidget()
        self._holders: list[QVBoxLayout] = []
        for _section in guide_data.SECTIONS:
            placeholder = QWidget()
            holder = QVBoxLayout(placeholder)
            holder.setContentsMargins(0, 0, 0, 0)
            holder.addWidget(_label("Carregando…", "Muted"))
            holder.addStretch(1)
            self._holders.append(holder)
            self.stack.addWidget(placeholder)
        self.stack.currentChanged.connect(self._ensure_built)
        outer.addWidget(self.stack, 1)

        outer.addWidget(_label(guide_data.FOOTER, "Muted"))

        self._update_progress()
        # Constrói a primeira aba só depois que o event loop girar, para que
        # build_page() retorne instantaneamente (regra 2 do padrão de plugins).
        QTimer.singleShot(0, lambda: self._ensure_built(0))

        # Downloads em andamento precisam ser encerrados antes que o Qt destrua
        # a página (fechar o app ou atualizar o plugin), senão o processo aborta.
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._image_loader.shutdown)

    def closeEvent(self, event):  # noqa: N802 (assinatura do Qt)
        self._image_loader.shutdown()
        super().closeEvent(event)

    def hideEvent(self, event):  # noqa: N802 (assinatura do Qt)
        if self.window() is not None and self.window().isHidden():
            self._image_loader.shutdown()
        super().hideEvent(event)

    # ------------------------------------------------------------------ topo
    def _build_header(self, outer: QVBoxLayout) -> None:
        outer.addWidget(_label(guide_data.GAME_NAME, "PageTitle", wrap=False))
        outer.addWidget(_label(guide_data.INTRO, "Muted"))
        stats = QHBoxLayout()
        stats.setSpacing(8)
        for stat in guide_data.HERO_STATS:
            stats.addWidget(_pill(f"{stat['value']}  {stat['label']}"))
        stats.addStretch(1)
        outer.addLayout(stats)

    def _build_search(self, outer: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(8)
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText(
            "Buscar... Ex.: Chang Choi, Perfectionist, Alone Home, sauna, barata, Negotiator"
        )
        self.global_search.textChanged.connect(self._global_search)
        clear = QPushButton("Limpar")
        clear.clicked.connect(lambda: self.global_search.setText(""))
        row.addWidget(self.global_search, 1)
        row.addWidget(clear, 0)
        outer.addLayout(row)

        self.results_box = QWidget()
        self.results_layout = QVBoxLayout(self.results_box)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(6)
        self.results_box.hide()
        outer.addWidget(self.results_box)

    def _build_progress(self, outer: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(8)
        self.progress = QProgressBar()
        self.progress.setStyleSheet(_PROGRESS_QSS)
        self.progress.setRange(0, max(1, len(keys.all_keys())))
        self.progress_label = _pill("")
        self.trophy_label = _pill("")
        self.sales_pill = _pill("")
        row.addWidget(self.progress, 1)
        row.addWidget(self.progress_label, 0)
        row.addWidget(self.trophy_label, 0)
        row.addWidget(self.sales_pill, 0)
        outer.addLayout(row)

    def _build_toolbar(self, outer: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(8)
        export = QPushButton("Exportar progresso")
        export.clicked.connect(self._export)
        importer = QPushButton("Importar progresso")
        importer.clicked.connect(self._import)
        reset = QPushButton("Resetar marcações")
        reset.clicked.connect(self._reset)
        for button in (export, importer, reset):
            row.addWidget(button)
        row.addStretch(1)
        outer.addLayout(row)

    def _build_nav(self, outer: QVBoxLayout) -> None:
        holder = QWidget()
        holder.setStyleSheet(_NAV_QSS)
        grid = QGridLayout(holder)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        self._nav_buttons: list[QPushButton] = []
        for i, section in enumerate(guide_data.SECTIONS):
            button = QPushButton(f"{section['num']}  {section['nav']}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setChecked(i == 0)
            button.clicked.connect(lambda _=False, index=i: self.show_section(index))
            grid.addWidget(button, i // 5, i % 5)
            self._nav_buttons.append(button)
        for column in range(5):
            grid.setColumnStretch(column, 1)
        outer.addWidget(holder)

    def show_section(self, index: int) -> None:
        for i, button in enumerate(self._nav_buttons):
            button.setChecked(i == index)
        self.stack.setCurrentIndex(index)

    # -------------------------------------------------------------- progresso
    def _checkbox(self, key: str, text: str = "") -> QCheckBox:
        box = QCheckBox(text)
        box.setChecked(key in self._done)
        box.toggled.connect(lambda checked, k=key: self._on_toggle(k, checked))
        self._boxes.setdefault(key, []).append(box)
        return box

    def _on_toggle(self, key: str, checked: bool) -> None:
        if checked:
            self._done.add(key)
        else:
            self._done.discard(key)
        for box in self._boxes.get(key, []):
            if box.isChecked() != checked:
                box.blockSignals(True)
                box.setChecked(checked)
                box.blockSignals(False)
        save_progress(self._done)
        self._update_progress()

    def _update_progress(self) -> None:
        all_keys = keys.all_keys()
        done = sum(1 for key in all_keys if key in self._done)
        percent = round(done / len(all_keys) * 100) if all_keys else 0
        self.progress.setValue(done)
        self.progress_label.setText(f"{done} / {len(all_keys)}  •  {percent}%")
        trophies = keys.trophy_keys()
        got = sum(1 for key in trophies if key in self._done)
        self.trophy_label.setText(f"{got}/{len(trophies)} troféus")
        sold = keys.sales_done(self._done)
        self.sales_pill.setText(f"{sold}/{guide_data.SALES_TOTAL} vendas")
        if self._sales_label is not None:
            self._sales_label.setText(self._sales_text(sold))
        for pill, phase_keys in self._phase_pills:
            phase_done = sum(1 for key in phase_keys if key in self._done)
            pill.setText(f"{phase_done}/{len(phase_keys)}")

    def _sales_text(self, sold: int) -> str:
        parts = []
        for milestone, name in sorted(guide_data.SALES_MILESTONES.items()):
            mark = "✔" if sold >= milestone else "○"
            parts.append(f"{mark} {milestone} — {name}")
        return "     ".join(parts)

    def _refresh_boxes(self) -> None:
        for key, boxes in self._boxes.items():
            checked = key in self._done
            for box in boxes:
                box.blockSignals(True)
                box.setChecked(checked)
                box.blockSignals(False)
        self._update_progress()
        if self._trophy_rows:
            self._filter_trophies()
        if self._house_rows:
            self._filter_houses()

    # ------------------------------------------------------ exportar/importar
    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar progresso", "house-flipper-platina-progresso.json",
            "JSON (*.json)",
        )
        if not path:
            return
        payload = {
            "guide": guide_data.GUIDE_ID,
            "version": 1,
            "exportedAt": datetime.now(timezone.utc).isoformat(),
            "state": {key: True for key in sorted(self._done)},
        }
        try:
            Path(path).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as error:
            QMessageBox.warning(self, "Exportar", f"Não foi possível salvar: {error}")

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar progresso", "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            QMessageBox.warning(self, "Importar", "Arquivo JSON inválido.")
            return
        state = raw.get("state", raw) if isinstance(raw, dict) else raw
        self._done = keys.normalize_imported(state)
        save_progress(self._done)
        self._refresh_boxes()

    def _reset(self) -> None:
        answer = QMessageBox.question(
            self, "Resetar", "Apagar todas as marcações deste guia?"
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._done = set()
        save_progress(self._done)
        self._refresh_boxes()

    # ------------------------------------------------------------- busca geral
    def _global_search(self) -> None:
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        query = _norm(self.global_search.text()).strip()
        if len(query) < 2:
            self.results_box.hide()
            return

        hits: list[tuple[str, str, str, str, str]] = []
        for step in guide_data.ROUTE:
            if query in _norm(_flat(step)):
                hits.append(
                    (f"PASSO {step['num']}", step["title"], step["place"],
                     step["exact"], "route")
                )
        for buyer in guide_data.BUYERS:
            if query in _norm(_flat(buyer)):
                hits.append(
                    ("COMPRADOR", buyer["name"], f"{buyer['house']} · {buyer['price']}",
                     f"Troféu {buyer['trophy']}. {buyer['profile']}", "buyers")
                )
        for trophy in guide_data.TROPHIES:
            if query in _norm(_flat(trophy)):
                hits.append(
                    ("TROFÉU", trophy["name"], trophy["tier"].upper(),
                     f"{trophy['requirement']} {trophy['shortcut']}", "trophies")
                )
        for house in guide_data.HOUSES:
            if query in _norm(_flat(house)):
                hits.append(
                    ("CASA", house["name"], f"{house['price']} · {house['size']}",
                     house["note"] or "Casa do jogo base — conta para o Game Over.", "houses")
                )
        for secret in guide_data.SECRETS:
            if query in _norm(_flat(secret)):
                hits.append(
                    ("SEGREDO", secret["name"], secret["where"], secret["how"], "secrets")
                )

        if not hits:
            self.results_layout.addWidget(
                _notice("Nada encontrado. Tente o nome de um comprador, troféu, casa ou item.")
            )
            self.results_box.show()
            return

        for kind, name, where, text, page in hits[:_SEARCH_LIMIT]:
            frame, layout = _card()
            head = QHBoxLayout()
            head.setSpacing(8)
            head.addWidget(_label(kind, "Kicker", wrap=False))
            head.addWidget(_label(f"<b>{_esc(name)}</b>", "SectionTitle"), 1)
            if where:
                head.addWidget(_pill(where))
            layout.addLayout(head)
            layout.addWidget(_label(text, "Muted"))
            go = QPushButton(
                f"Ir para “{guide_data.SECTIONS[self._section_index[page]]['nav']}”"
            )
            go.clicked.connect(
                lambda _=False, target=page: self.show_section(self._section_index[target])
            )
            row = QHBoxLayout()
            row.addWidget(go)
            row.addStretch(1)
            layout.addLayout(row)
            self.results_layout.addWidget(frame)
        if len(hits) > _SEARCH_LIMIT:
            self.results_layout.addWidget(
                _label(
                    f"…e mais {len(hits) - _SEARCH_LIMIT} resultado(s). Refine a busca.",
                    "Muted",
                )
            )
        self.results_box.show()

    # ---------------------------------------------------------------- imagens
    def _add_image(self, layout, url: str, max_w: int = _IMG_MAX_W,
                   max_h: int = _IMG_MAX_H) -> QLabel | None:
        if not url:
            return None
        holder = QLabel("Carregando imagem…")
        holder.setObjectName("Muted")
        layout.addWidget(holder)
        state = {"loaded": False}

        def show(pixmap: QPixmap) -> None:
            state["loaded"] = True
            holder.setText("")
            holder.setPixmap(
                pixmap.scaled(
                    max_w, max_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        cached = self._image_loader.load(url, show)
        if cached is not None:
            show(cached)
            return holder

        def timeout() -> None:
            if not state["loaded"]:
                holder.setText(
                    f'Imagem indisponível offline — <a href="{_esc(url)}" '
                    f'style="color:{guide_data.ACCENT}">abrir no navegador</a>'
                )
                holder.setOpenExternalLinks(True)

        QTimer.singleShot(_IMG_TIMEOUT_MS, timeout)
        return holder

    # ------------------------------------------------------- construção lazy
    def _ensure_built(self, index: int) -> None:
        if index in self._built or index < 0:
            return
        self._built.add(index)
        holder = self._holders[index]
        # Troca o "Carregando…" pelo conteúdo real. Esvaziar o layout (em vez de
        # trocar a página do QStackedWidget) evita depender de deleteLater().
        while holder.count():
            item = holder.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        key = guide_data.SECTIONS[index]["key"]
        builder = getattr(self, f"_build_{key}")
        holder.addWidget(
            _scroll_page(lambda layout: self._with_header(layout, index, builder))
        )
        self._update_progress()

    def _with_header(self, layout: QVBoxLayout, index: int, builder) -> None:
        section = guide_data.SECTIONS[index]
        layout.addWidget(_label(section["eyebrow"], "Kicker", wrap=False))
        layout.addWidget(_label(section["title"], "CardTitle"))
        layout.addWidget(_label(section["lead"], "Muted"))
        for notice in section["notices"]:
            layout.addWidget(_notice(notice["text"], notice["tone"]))
        builder(layout)

    # ------------------------------------------------------- 01 Passo a passo
    def _build_route(self, layout: QVBoxLayout) -> None:
        phases: dict[str, list[dict]] = {}
        for step in guide_data.ROUTE:
            phases.setdefault(step["phase"], []).append(step)

        for phase, steps in phases.items():
            phase_keys = [keys.step_key(step["num"]) for step in steps]
            head_holder = QWidget()
            head_holder.setStyleSheet(_PHASE_QSS)
            head_row = QHBoxLayout(head_holder)
            head_row.setContentsMargins(0, 0, 0, 0)
            head_row.setSpacing(8)
            toggle = QPushButton(f"{phase}   ({len(steps)} passos)")
            toggle.setObjectName("PhaseHead")
            pill = _pill("")
            head_row.addWidget(toggle, 1)
            head_row.addWidget(pill, 0)
            layout.addWidget(head_holder)
            self._phase_pills.append((pill, phase_keys))

            body = QWidget()
            body_layout = QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(8)
            for step in steps:
                body_layout.addWidget(self._route_step(step))
            layout.addWidget(body)
            toggle.clicked.connect(
                lambda _=False, target=body: target.setVisible(not target.isVisible())
            )

    def _route_step(self, step: dict) -> QFrame:
        frame, layout = _card()
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(
            self._checkbox(keys.step_key(step["num"])), 0, Qt.AlignmentFlag.AlignTop
        )
        head.addWidget(_label(step["num"], "Kicker", wrap=False), 0, Qt.AlignmentFlag.AlignTop)
        head.addWidget(_label(step["title"], "SectionTitle"), 1)
        head.addWidget(_pill(step["place"]), 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(head)
        _detail(layout, "Quando", step["when"])
        _detail(layout, "Faça exatamente", step["exact"])
        _detail(layout, "Por que agora", step["why"])
        image = step.get("image", "")
        if image:
            # ícone de troféu é pequeno; captura/planta é grande
            small = "/images/" in image and "Blueprint" not in image
            self._add_image(layout, image, _ICON if small else _IMG_MAX_W,
                            _ICON if small else _IMG_MAX_H)
        return frame

    # ------------------------------------------------------- 02 Compradores
    def _build_buyers(self, layout: QVBoxLayout) -> None:
        total = len(guide_data.BUYERS)
        for i, buyer in enumerate(guide_data.BUYERS):
            frame, card = _card()
            head = QHBoxLayout()
            head.setSpacing(10)
            head.addWidget(
                self._checkbox(keys.buyer_key(buyer["key"])), 0, Qt.AlignmentFlag.AlignTop
            )
            portrait = QVBoxLayout()
            self._add_image(portrait, buyer["portrait"], _PORTRAIT, _PORTRAIT)
            portrait.addStretch(1)
            head.addLayout(portrait, 0)

            texts = QVBoxLayout()
            texts.setSpacing(2)
            title_row = QHBoxLayout()
            title_row.setSpacing(8)
            title_row.addWidget(_label(f"{i + 1}/{total}", "Kicker", wrap=False), 0)
            title_row.addWidget(_label(buyer["name"], "SectionTitle"), 1)
            title_row.addWidget(_tier(buyer["tier"]), 0)
            texts.addLayout(title_row)
            texts.addWidget(_pill(f"Troféu: {buyer['trophy']}"))
            head.addLayout(texts, 1)
            card.addLayout(head)

            _detail(card, "Perfil (o que o jogo pontua)", buyer["profile"])
            _detail(card, "Casa recomendada", f"{buyer['house']} — {buyer['price']}")
            card.addWidget(_label("<b>Receita:</b>", "Muted"))
            for n, step in enumerate(buyer["steps"], start=1):
                card.addWidget(_label(f"{n}. {_esc(step)}", "Muted"))
            _detail(card, "Alternativa", buyer["alt"])
            if buyer["note"]:
                card.addWidget(_notice(buyer["note"]))
            layout.addWidget(frame)
            self._buyer_rows.append((frame, _norm(_flat(buyer))))

    # ---------------------------------------------------------- 03 Troféus
    def _build_trophies(self, layout: QVBoxLayout) -> None:
        filters = QHBoxLayout()
        filters.setSpacing(8)
        self.trophy_search = QLineEdit()
        self.trophy_search.setPlaceholderText("Buscar troféu ou requisito...")
        self.trophy_search.textChanged.connect(self._filter_trophies)
        self.trophy_tier = QComboBox()
        self.trophy_tier.addItem("Todos os tiers", "")
        for tier in ("platina", "ouro", "prata", "bronze"):
            self.trophy_tier.addItem(tier.capitalize(), tier)
        self.trophy_tier.currentIndexChanged.connect(self._filter_trophies)
        self.trophy_pending = QCheckBox("só pendentes")
        self.trophy_pending.toggled.connect(self._filter_trophies)
        filters.addWidget(self.trophy_search, 1)
        filters.addWidget(self.trophy_tier, 0)
        filters.addWidget(self.trophy_pending, 0)
        layout.addLayout(filters)

        self.trophy_empty = _label("Nenhum troféu corresponde ao filtro.", "Muted")
        self.trophy_empty.hide()
        layout.addWidget(self.trophy_empty)

        for trophy in guide_data.TROPHIES:
            frame, card = _card()
            head = QHBoxLayout()
            head.setSpacing(10)
            head.addWidget(
                self._checkbox(keys.trophy_key(trophy["id"])), 0, Qt.AlignmentFlag.AlignTop
            )
            if trophy["image"]:
                icon = QVBoxLayout()
                self._add_image(icon, trophy["image"], _ICON, _ICON)
                icon.addStretch(1)
                head.addLayout(icon, 0)
            head.addWidget(_label(trophy["name"], "SectionTitle"), 1)
            head.addWidget(_tier(trophy["tier"]), 0, Qt.AlignmentFlag.AlignTop)
            card.addLayout(head)
            _detail(card, "Requisito", trophy["requirement"])
            _detail(card, "Atalho", trophy["shortcut"])
            layout.addWidget(frame)
            self._trophy_rows.append((frame, _norm(_flat(trophy)), trophy["id"]))

    def _filter_trophies(self) -> None:
        query = _norm(self.trophy_search.text()).strip()
        tier = self.trophy_tier.currentData() or ""
        pending = self.trophy_pending.isChecked()
        visible = 0
        for (frame, haystack, trophy_id), trophy in zip(
            self._trophy_rows, guide_data.TROPHIES
        ):
            got = keys.trophy_key(trophy_id) in self._done
            show = (
                query in haystack
                and (not tier or trophy["tier"] == tier)
                and (not pending or not got)
            )
            frame.setVisible(show)
            visible += int(show)
        self.trophy_empty.setVisible(visible == 0)

    # ------------------------------------------------------------ 04 Casas
    def _build_houses(self, layout: QVBoxLayout) -> None:
        filters = QHBoxLayout()
        filters.setSpacing(8)
        self.house_search = QLineEdit()
        self.house_search.setPlaceholderText("Buscar casa, preço ou troféu...")
        self.house_search.textChanged.connect(self._filter_houses)
        self.house_pending = QCheckBox("só não vendidas")
        self.house_pending.toggled.connect(self._filter_houses)
        filters.addWidget(self.house_search, 1)
        filters.addWidget(self.house_pending, 0)
        layout.addLayout(filters)

        self.house_empty = _label("Nenhuma casa corresponde ao filtro.", "Muted")
        self.house_empty.hide()
        layout.addWidget(self.house_empty)

        for i, house in enumerate(guide_data.HOUSES):
            frame, card = _card()
            head = QHBoxLayout()
            head.setSpacing(8)
            head.addWidget(self._checkbox(keys.house_key(i)), 0, Qt.AlignmentFlag.AlignTop)
            head.addWidget(_label(f"{i + 1:02d}", "Kicker", wrap=False), 0)
            head.addWidget(_label(house["name"], "SectionTitle"), 1)
            head.addWidget(_pill(house["price"]), 0, Qt.AlignmentFlag.AlignTop)
            head.addWidget(_pill(house["size"]), 0, Qt.AlignmentFlag.AlignTop)
            card.addLayout(head)
            if house["note"]:
                card.addWidget(_label(house["note"], "Muted"))
            layout.addWidget(frame)
            self._house_rows.append((frame, _norm(_flat(house)), i))

    def _filter_houses(self) -> None:
        query = _norm(self.house_search.text()).strip()
        pending = self.house_pending.isChecked()
        visible = 0
        for frame, haystack, index in self._house_rows:
            sold = keys.house_key(index) in self._done
            show = query in haystack and (not pending or not sold)
            frame.setVisible(show)
            visible += int(show)
        self.house_empty.setVisible(visible == 0)

    # ----------------------------------------------------------- 05 Vendas
    def _build_sales(self, layout: QVBoxLayout) -> None:
        self._sales_label = _label("", "SectionTitle")
        layout.addWidget(self._sales_label)

        frame, card = _card()
        grid = QGridLayout()
        grid.setSpacing(6)
        for i in range(guide_data.SALES_TOTAL):
            box = self._checkbox(keys.sale_key(i), str(i + 1))
            if (i + 1) in guide_data.SALES_MILESTONES:
                box.setStyleSheet("color:%s;font-weight:700;" % guide_data.ACCENT)
                box.setToolTip(guide_data.SALES_MILESTONES[i + 1])
            grid.addWidget(box, i // _SALES_PER_ROW, i % _SALES_PER_ROW)
        card.addLayout(grid)
        layout.addWidget(frame)

        layout.addWidget(
            _notice(
                "Estratégia: as 37 vendas do Game Over já contam. Depois delas faltam 13 — "
                "compre e revenda o First Office (€ 22.478), que é a casa mais barata e "
                "mais rápida de rodar."
            )
        )
        self._update_progress()

    # ----------------------------------------------------------- 06 Ordens
    def _build_orders(self, layout: QVBoxLayout) -> None:
        for note in guide_data.ORDERS_NOTES:
            frame, card = _card()
            card.addWidget(_label(note["title"], "SectionTitle"))
            card.addWidget(_label(note["text"], "Muted"))
            layout.addWidget(frame)

    # ------------------------------------------------------------ 07 Perks
    def _build_perks(self, layout: QVBoxLayout) -> None:
        for i, perk in enumerate(guide_data.PERKS):
            frame, card = _card()
            head = QHBoxLayout()
            head.setSpacing(8)
            head.addWidget(self._checkbox(keys.perk_key(i)), 0, Qt.AlignmentFlag.AlignTop)
            head.addWidget(_label(f"#{perk['order']}", "Kicker", wrap=False), 0)
            head.addWidget(_label(perk["name"], "SectionTitle"), 1)
            head.addWidget(_pill(perk["when"]), 0, Qt.AlignmentFlag.AlignTop)
            card.addLayout(head)
            _detail(card, "Por quê", perk["why"])
            layout.addWidget(frame)

    # --------------------------------------------------------- 08 Segredos
    def _build_secrets(self, layout: QVBoxLayout) -> None:
        for i, secret in enumerate(guide_data.SECRETS):
            frame, card = _card()
            head = QHBoxLayout()
            head.setSpacing(8)
            head.addWidget(self._checkbox(keys.secret_key(i)), 0, Qt.AlignmentFlag.AlignTop)
            head.addWidget(_label(secret["name"], "SectionTitle"), 1)
            head.addWidget(_pill(secret["where"]), 0, Qt.AlignmentFlag.AlignTop)
            card.addLayout(head)
            _detail(card, "Como fazer", secret["how"])
            _detail(card, "Recompensa", secret["reward"])
            image = secret.get("image", "")
            if image:
                small = "Blueprint" not in image and "Roaches" not in image
                self._add_image(card, image, _ICON if small else _IMG_MAX_W,
                                _ICON if small else _IMG_MAX_H)
            layout.addWidget(frame)

    # ---------------------------------------------------- 09 Mapas / Imagens
    def _build_visuals(self, layout: QVBoxLayout) -> None:
        for visual in guide_data.VISUALS:
            frame, card = _card()
            card.addWidget(_label(visual["title"], "SectionTitle"))
            card.addWidget(_label(visual["caption"], "Muted"))
            self._add_image(card, visual["image"])
            card.addWidget(_label(f"Fonte da imagem: {visual['source']}", "Muted"))
            card.addWidget(_link("Abrir imagem no navegador ↗", visual["image"]))
            layout.addWidget(frame)

    # ------------------------------------------------------------ 10 Fontes
    def _build_sources(self, layout: QVBoxLayout) -> None:
        for source in guide_data.SOURCES:
            frame, card = _card()
            card.addWidget(_label(source["title"], "SectionTitle"))
            card.addWidget(_label(source["note"], "Muted"))
            card.addWidget(_link("Abrir fonte ↗", source["url"]))
            layout.addWidget(frame)
