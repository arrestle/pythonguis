"""Parameter-card Mirage UI entrypoint."""

import sys

from PySide6.QtCore import QEvent, QMargins, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMenuBar,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mirage_parm.diagnostics import show_diagnostics_dialog
from mirage_parm.parameters import CARDS, CardSpec
from mirage_parm.widgets import PanelKind, ParameterCard
from shared.config import MIDI_PORT_NAME
from shared.midi import open_midi_output_port

# Window title (parameter-card layout)
WINDOW_TITLE = "Ensoniq Mirage — Parameter cards"

# Red panel: row1 three boxes; row2 configuration + WAVESAMPLE (26–28 + 60–72).
_RED_PANEL_ROW1 = ("sampling", "sampling_config", "command")
_RED_PANEL_ROW2 = ("configuration", "wavesample_sampling")
_RED_PANEL_IDS = frozenset(_RED_PANEL_ROW1 + _RED_PANEL_ROW2)

# Yellow panel: row1 three boxes, row2 three boxes.
_YELLOW_PANEL_ROW1 = ("program", "keyboard_program", "general_keyboard")
_YELLOW_PANEL_ROW2 = ("wavesample_program", "envelope")
_YELLOW_PANEL_IDS = frozenset(_YELLOW_PANEL_ROW1 + _YELLOW_PANEL_ROW2)

# Note-only cards: narrow column + top-aligned in row (don’t match full height of neighbors).
_COMPACT_HEADER_IDS = frozenset({"sampling", "program"})
# In rows that include WAVESAMPLE, give it less horizontal stretch than neighbors (sliders still usable).
_WAVESAMPLE_IDS = frozenset({"wavesample_sampling", "wavesample_program"})
_WAVESAMPLE_STRETCH = 2
_WAVESAMPLE_NEIGHBOR_STRETCH = 5  # WAVESAMPLE ~2/7 of row slack; ENVELOPE a bit narrower on laptop

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)

        self._midi_port, self.midi_port_name = open_midi_output_port(MIDI_PORT_NAME)

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        act_quit = QAction("&Quit", self)
        act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        act_quit.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(act_quit)

        view_menu = menu_bar.addMenu("&View")
        self._act_exit_full_screen = QAction("E&xit Full Screen", self)
        self._act_exit_full_screen.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self._act_exit_full_screen.triggered.connect(self._leave_full_screen)
        view_menu.addAction(self._act_exit_full_screen)

        self._act_enter_full_screen = QAction("&Enter Full Screen", self)
        self._act_enter_full_screen.triggered.connect(self.showFullScreen)
        view_menu.addAction(self._act_enter_full_screen)

        menu_bar.addMenu(QMenu("Param", self))
        menu_bar.addMenu(QMenu("Wave", self))

        help_menu = menu_bar.addMenu("&Help")
        act_diagnostics = QAction("&Diagnostics…", self)
        act_diagnostics.triggered.connect(
            lambda: show_diagnostics_dialog(self, opened_output_name=self.midi_port_name)
        )
        help_menu.addAction(act_diagnostics)

        self._full_screen_close_button = QPushButton("\u00d7")
        self._full_screen_close_button.setObjectName("fullScreenCloseButton")
        self._full_screen_close_button.setFixedSize(40, 32)
        self._full_screen_close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._full_screen_close_button.setToolTip("Close")
        self._full_screen_close_button.clicked.connect(QApplication.instance().quit)
        self._full_screen_close_wrap = QWidget()
        close_wrap_layout = QHBoxLayout(self._full_screen_close_wrap)
        close_wrap_layout.setContentsMargins(0, 0, 14, 0)
        close_wrap_layout.setSpacing(0)
        close_wrap_layout.addWidget(self._full_screen_close_button)
        menu_bar.setCornerWidget(self._full_screen_close_wrap, Qt.Corner.TopRightCorner)

        shortcut_quit = QShortcut(QKeySequence.StandardKey.Quit, self)
        shortcut_quit.activated.connect(QApplication.instance().quit)

        scroll = QScrollArea()
        scroll.setObjectName("mirageParmScroll")
        scroll.setWidgetResizable(True)
        # Inset content from the viewport edge so group box borders aren’t clipped; avoid H-scroll gap.
        scroll.setViewportMargins(QMargins(0, 0, 14, 0))
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setObjectName("mirageParmScrollInner")
        inner.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.MinimumExpanding,
        )
        v = QVBoxLayout()
        v.setContentsMargins(6, 4, 6, 6)
        v.setSpacing(9)

        by_id: dict[str, CardSpec] = {c.card_id: c for c in CARDS if c.card_id}

        def add_card_row(card_ids: tuple[str, ...], panel: PanelKind) -> None:
            row = QHBoxLayout()
            row.setSpacing(4)
            row_has_wavesample = bool(_WAVESAMPLE_IDS.intersection(card_ids))
            for cid in card_ids:
                spec = by_id.get(cid)
                if spec is None:
                    continue
                card = ParameterCard(
                    self._midi_port,
                    spec,
                    panel=panel,
                    show_play_preview=spec.card_id in ("sampling", "program"),
                    midi_port_name=self.midi_port_name,
                )
                if cid in _COMPACT_HEADER_IDS:
                    wrap = QWidget()
                    wrap.setSizePolicy(
                        QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.MinimumExpanding,
                    )
                    wl = QVBoxLayout(wrap)
                    wl.setContentsMargins(0, 0, 0, 0)
                    wl.setSpacing(0)
                    wl.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
                    wl.addStretch(1)
                    row.addWidget(wrap, stretch=0)
                elif row_has_wavesample and cid in _WAVESAMPLE_IDS:
                    row.addWidget(card, stretch=_WAVESAMPLE_STRETCH)
                elif row_has_wavesample:
                    row.addWidget(card, stretch=_WAVESAMPLE_NEIGHBOR_STRETCH)
                else:
                    row.addWidget(card, stretch=1)
            v.addLayout(row)

        add_card_row(_RED_PANEL_ROW1, "red")
        add_card_row(_RED_PANEL_ROW2, "red")
        add_card_row(_YELLOW_PANEL_ROW1, "yellow")
        add_card_row(_YELLOW_PANEL_ROW2, "yellow")

        for card in CARDS:
            if card.card_id in _RED_PANEL_IDS or card.card_id in _YELLOW_PANEL_IDS:
                continue
            v.addWidget(
                ParameterCard(
                    self._midi_port,
                    card,
                    panel="default",
                    show_play_preview=card.card_id in ("sampling", "program"),
                    midi_port_name=self.midi_port_name,
                )
            )

        v.addStretch(1)
        inner.setLayout(v)
        scroll.setWidget(inner)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.setCentralWidget(scroll)

        self._apply_card_style()
        self._update_full_screen_menu_actions()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._update_full_screen_menu_actions()

    def _leave_full_screen(self) -> None:
        if self.isFullScreen():
            self.showMaximized()

    def _update_full_screen_menu_actions(self) -> None:
        fs = self.isFullScreen()
        self._act_exit_full_screen.setVisible(fs)
        self._act_enter_full_screen.setVisible(not fs)
        self._full_screen_close_wrap.setVisible(fs)

    def _apply_card_style(self) -> None:
        self.setStyleSheet(
            """
            QGroupBox#RedParameterCard {
                font-weight: bold;
                border: 3px solid #b71c1c;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 2px;
                background-color: palette(base);
            }
            QGroupBox#RedParameterCard::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #8b0000;
            }
            QGroupBox#RedParameterCard QWidget#ParameterRow {
                border-bottom: 1px solid #b71c1c;
                padding-bottom: 2px;
                margin-bottom: 1px;
            }
            QGroupBox#YellowParameterCard,
            QGroupBox#YellowWavesampleProgramCard {
                font-weight: bold;
                border: 3px solid #d4a017;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 2px;
                padding-right: 6px;
                background-color: palette(base);
            }
            QGroupBox#YellowParameterCard::title,
            QGroupBox#YellowWavesampleProgramCard::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #8a6d00;
            }
            QGroupBox#YellowParameterCard QWidget#ParameterRow,
            QGroupBox#YellowWavesampleProgramCard QWidget#ParameterRow {
                border-bottom: 1px solid #d4a017;
                padding-bottom: 2px;
                margin-bottom: 1px;
            }
            QGroupBox#ParameterCard {
                font-weight: bold;
                border: 2px solid palette(mid);
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 2px;
                padding-right: 6px;
            }
            QScrollArea#mirageParmScroll {
                background-color: palette(window);
            }
            QGroupBox#ParameterCard::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#fullScreenCloseButton {
                font-size: 22px;
                font-weight: bold;
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(button);
                padding: 0;
            }
            QPushButton#fullScreenCloseButton:hover {
                background-color: palette(midlight);
            }
            QPushButton#fullScreenCloseButton:pressed {
                background-color: palette(mid);
            }
            """
        )


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
