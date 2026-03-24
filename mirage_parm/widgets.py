"""Parameter card and compact parameter row widgets."""

from __future__ import annotations

import sys
import threading
from typing import Literal
import time
import traceback

import mido
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mirage_parm.parameters import CardSpec, ParmSpec
from shared.sysex import send_mirage_parameter

# SAMPLING / PROGRAM note-only headers: fixed column width in the main grid.
NARROW_CARD_COLUMN_MAX_WIDTH_PX = 220
# Yellow WAVESAMPLE (program): single-column card beside ENVELOPE — keep readable but slim.
WAVESAMPLE_PROGRAM_CARD_MAX_WIDTH_PX = 400


class ParmRow(QWidget):
    """Single parameter: label + param # / hex + min … slider … max + value."""

    def __init__(
        self,
        midi_port,
        spec: ParmSpec,
        *,
        display_label: str | None = None,
        compact: bool = False,
        narrow: bool = False,
        narrow_columns: int = 2,
        parent=None,
    ):
        super().__init__(parent)
        self._midi_port = midi_port
        self._spec = spec
        text = display_label if display_label is not None else spec.label

        if compact:
            # Fill envelope column width so sliders use space (avoids a blank band around the center rule).
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif narrow:
            # 2–3 column reference-card layouts: tight label + slider.
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 6, 2)

        self._label = QLabel(
            f"<b>{spec.command_id}</b>&nbsp;{text} "
            f"<span style='color:#666;'>0x{spec.command_id:02X}</span>"
        )
        self._label.setTextFormat(Qt.TextFormat.RichText)
        if compact:
            # Fixed width + right-align so sliders line up in the two ENVELOPE columns.
            self._label.setFixedWidth(118)
            self._label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        elif narrow:
            lw = 88 if narrow_columns >= 3 else 108
            self._label.setFixedWidth(lw)
            self._label.setStyleSheet("font-size: 10px;")
            self._label.setWordWrap(True)
            self._label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
        else:
            # Tighter than 220px so three-column rows fit ~880px laptop windows.
            self._label.setMinimumWidth(148)
        if spec.range_note:
            self._label.setToolTip(spec.range_note)

        dec = QPushButton("<")
        dec.setFixedSize(20, 20)
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(spec.min_value, spec.max_value)
        self._slider.setValue(spec.min_value)
        self._slider.setMinimumWidth(
            36 if compact else (30 if narrow else 52)
        )
        self._slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._slider.setTracking(True)
        self._slider.valueChanged.connect(self._on_slider_value)
        if spec.range_note:
            self._slider.setToolTip(spec.range_note)

        inc = QPushButton(">")
        inc.setFixedSize(20, 20)
        dec.clicked.connect(self._dec)
        inc.clicked.connect(self._inc)

        self._min_lbl = QLabel(str(spec.min_value))
        self._min_lbl.setMinimumWidth(18)
        self._min_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._value_spin = QSpinBox()
        self._value_spin.setRange(spec.min_value, spec.max_value)
        self._value_spin.setValue(spec.min_value)
        self._value_spin.setFixedWidth(46 if not compact else 40)
        self._value_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._value_spin.valueChanged.connect(self._on_spin_value)

        self._max_lbl = QLabel(str(spec.max_value))
        self._max_lbl.setMinimumWidth(20)
        self._max_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._label)
        layout.addWidget(self._min_lbl)
        layout.addWidget(dec)
        layout.addWidget(self._slider, stretch=1)
        layout.addWidget(inc)
        layout.addWidget(self._max_lbl)
        layout.addWidget(self._value_spin)
        self.setLayout(layout)
        self.setObjectName("ParameterRow")

    def _on_slider_value(self, value: int) -> None:
        self._value_spin.blockSignals(True)
        self._value_spin.setValue(value)
        self._value_spin.blockSignals(False)
        print(f"{self._spec.label} 0x{self._spec.command_id:02X} = {value}")
        send_mirage_parameter(self._midi_port, self._spec.command_id, value)

    def _on_spin_value(self, value: int) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)
        print(f"{self._spec.label} 0x{self._spec.command_id:02X} = {value}")
        send_mirage_parameter(self._midi_port, self._spec.command_id, value)

    def _dec(self, checked: bool = False) -> None:
        v = self._slider.value()
        if v > self._slider.minimum():
            self._slider.setValue(v - 1)

    def _inc(self, checked: bool = False) -> None:
        v = self._slider.value()
        if v < self._slider.maximum():
            self._slider.setValue(v + 1)


def _play_gm_test(midi_port) -> None:
    """Short GM chord for card-level MIDI sanity check (same idea as MirageSlider)."""
    ch = 0
    try:
        midi_port.send(mido.Message("program_change", channel=ch, program=0))
        time.sleep(0.05)
        for note, vel in ((60, 110), (64, 95), (67, 95)):
            midi_port.send(mido.Message("note_on", channel=ch, note=note, velocity=vel))
            time.sleep(0.15)
        time.sleep(0.35)
        for note in (60, 64, 67):
            midi_port.send(mido.Message("note_off", channel=ch, note=note, velocity=64))
    except Exception:
        print("Card preview MIDI failed:", file=sys.stderr)
        traceback.print_exc()


PanelKind = Literal["default", "red", "yellow"]


def _panel_inner_grid_color(panel: PanelKind) -> str:
    """Same hue as thick QGroupBox border, for 1px inner grid lines."""
    if panel == "red":
        return "#b71c1c"
    if panel == "yellow":
        return "#d4a017"
    return "#888888"


def _thin_grid_vline(hex_color: str) -> QFrame:
    """1px vertical rule between parameter columns (matches panel accent)."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFrameShadow(QFrame.Shadow.Plain)
    line.setFixedWidth(1)
    line.setStyleSheet(
        f"QFrame {{ background-color: {hex_color}; border: none; max-width: 1px; }}"
    )
    line.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
    return line


def _section_horizontal_rule(grid_color: str) -> QFrame:
    """Full-width rule between stacked sections inside one group box."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Plain)
    line.setFixedHeight(1)
    line.setStyleSheet(
        f"background-color: {grid_color}; border: none; min-height: 1px; max-height: 1px;"
    )
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return line


def _envelope_modulation_marker(grid_color: str, align: Qt.AlignmentFlag) -> QWidget:
    """Narrow rule + 'MODULATION' between env. stages (40–44 / 50–54) and mod. (45–49 / 55–59)."""
    wrap = QWidget()
    wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    v = QVBoxLayout(wrap)
    v.setContentsMargins(0, 2, 0, 2)
    v.setSpacing(2)
    lab = QLabel("MODULATION")
    lab.setStyleSheet(
        "font-weight: bold; font-size: 9px; color: #8a6d00; letter-spacing: 0.5px;"
    )
    lab.setAlignment(align)
    v.addWidget(lab)
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Plain)
    line.setFixedHeight(1)
    line.setStyleSheet(
        f"background-color: {grid_color}; border: none; min-height: 1px; max-height: 1px;"
    )
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    v.addWidget(line)
    return wrap


def _panel_section_heading_color(panel: PanelKind) -> str:
    """Match QGroupBox title tint for in-card section subtitles."""
    if panel == "red":
        return "#8b0000"
    if panel == "yellow":
        return "#8a6d00"
    return "#555555"


# Laminated card column counts (params split top-to-bottom within each column, left-to-right).
_REFERENCE_CARD_COLUMN_COUNTS: dict[str, int] = {
    "sampling_config": 2,
    "command": 2,
    "configuration": 2,
    "wavesample_sampling": 3,
    "keyboard_program": 2,
    "general_keyboard": 2,
}


def _split_params_evenly(
    params: tuple[ParmSpec, ...], ncols: int
) -> list[tuple[ParmSpec, ...]]:
    """Split ``params`` into ``ncols`` sequential groups (extra items go to left columns)."""
    n = len(params)
    if ncols < 2 or n == 0:
        return [params]
    base, extra = divmod(n, ncols)
    out: list[tuple[ParmSpec, ...]] = []
    i = 0
    for c in range(ncols):
        sz = base + (1 if c < extra else 0)
        out.append(params[i : i + sz])
        i += sz
    return out


def _add_reference_card_columns(
    outer: QVBoxLayout,
    midi_port,
    params: tuple[ParmSpec, ...],
    ncols: int,
    grid_color: str,
) -> None:
    """SAMPLING CONFIG, COMMAND, CONFIGURATION (2 cols); WAVESAMPLE sampling (3 cols); etc."""
    if ncols < 2:
        for p in params:
            outer.addWidget(ParmRow(midi_port, p))
        return
    chunks = _split_params_evenly(params, ncols)
    row = QHBoxLayout()
    row.setSpacing(0)
    for i, chunk in enumerate(chunks):
        if i > 0:
            row.addWidget(_thin_grid_vline(grid_color))
        col = QVBoxLayout()
        col.setSpacing(3)
        for p in chunk:
            col.addWidget(
                ParmRow(midi_port, p, narrow=True, narrow_columns=ncols),
            )
        col.addStretch(1)
        row.addLayout(col, stretch=1)
    outer.addLayout(row)


def _strip_column_prefix(label: str, prefix: str) -> str:
    """e.g. 'FILTER — ATTACK' + prefix 'FILTER — ' -> 'ATTACK'."""
    if label.startswith(prefix):
        return label[len(prefix) :].strip()
    return label


def _add_envelope_filter_amplitude_columns(
    outer: QVBoxLayout,
    midi_port,
    params: tuple[ParmSpec, ...],
    grid_color: str,
) -> None:
    """Two columns: first half of ``params`` FILTER (strip 'FILTER — '), second half AMPLITUDE."""
    n = len(params)
    mid = n // 2
    if mid < 1 or n != mid * 2:
        for p in params:
            outer.addWidget(ParmRow(midi_port, p))
        return

    filter_params = params[:mid]
    amp_params = params[mid:]
    row = QHBoxLayout()
    row.setSpacing(0)

    def build_column(
        header: str,
        plist: tuple[ParmSpec, ...],
        col_prefix: str,
        align: Qt.AlignmentFlag,
    ) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(3)
        hdr = QLabel(header)
        hdr.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #8a6d00; "
            "padding-bottom: 3px; margin-bottom: 1px; "
            f"border-bottom: 1px solid {grid_color};"
        )
        hdr.setAlignment(align)
        # AlignTop only: AlignLeft/AlignRight here keeps children at min width → huge gap
        # around the center vline. Text alignment stays via QLabel.setAlignment above.
        col.addWidget(hdr, 0, Qt.AlignmentFlag.AlignTop)
        n_plist = len(plist)
        half = n_plist // 2
        show_mod_marker = n_plist == 10 and half == 5
        for i, p in enumerate(plist):
            if show_mod_marker and i == half:
                col.addWidget(
                    _envelope_modulation_marker(grid_color, align),
                    0,
                    Qt.AlignmentFlag.AlignTop,
                )
            short = _strip_column_prefix(p.label, col_prefix)
            col.addWidget(
                ParmRow(midi_port, p, display_label=short, compact=True),
                0,
                Qt.AlignmentFlag.AlignTop,
            )
        col.addStretch(1)
        return col

    row.addLayout(
        build_column("FILTER", filter_params, "FILTER — ", Qt.AlignmentFlag.AlignLeft),
        stretch=1,
    )
    row.addWidget(_thin_grid_vline(grid_color))
    row.addLayout(
        build_column("AMPLITUDE", amp_params, "AMPLITUDE — ", Qt.AlignmentFlag.AlignRight),
        stretch=1,
    )
    outer.addLayout(row)


class ParameterCard(QGroupBox):
    """One laminated-card style block; optional GM preview on SAMPLING / PROGRAM only."""

    def __init__(
        self,
        midi_port,
        spec: CardSpec,
        *,
        panel: PanelKind = "default",
        show_play_preview: bool = False,
        parent=None,
    ):
        super().__init__(spec.title, parent)
        object_names: dict[PanelKind, str] = {
            "default": "ParameterCard",
            "red": "RedParameterCard",
            "yellow": "YellowParameterCard",
        }
        # Slim yellow WAVESAMPLE: own object name for tighter QSS (less gap under title).
        if spec.card_id == "wavesample_program":
            self.setObjectName("YellowWavesampleProgramCard")
        else:
            self.setObjectName(object_names[panel])

        outer = QVBoxLayout()
        outer.setSpacing(6)
        outer.setContentsMargins(6, 4, 6, 6)

        if spec.card_id == "wavesample_program":
            # Description is long; tooltip only — saves a big block under the group title.
            if spec.description and spec.description.strip():
                self.setToolTip(spec.description)
            outer.setContentsMargins(8, 14, 8, 6)
            outer.setSpacing(2)
        else:
            desc = QLabel(spec.description)
            desc.setWordWrap(True)
            # Note-only cards (SAMPLING, PROGRAM): compact — don’t dominate the row.
            if spec.params:
                desc.setStyleSheet("color: palette(mid); font-size: 11px;")
            elif spec.card_id in ("sampling", "program"):
                desc.setStyleSheet(
                    "font-size: 10px; padding: 2px 0; color: palette(windowText); line-height: 1.2;"
                )
            else:
                desc.setStyleSheet("font-size: 12px; padding: 4px 0;")
            outer.addWidget(desc)

        if not spec.params:
            if spec.card_id in ("sampling", "program"):
                self.setMaximumWidth(NARROW_CARD_COLUMN_MAX_WIDTH_PX)
                self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
            if not (spec.description and spec.description.strip()):
                placeholder = QLabel(
                    "(No parameters in this card — add rows in parameter_cards.json.)"
                )
                placeholder.setWordWrap(True)
                placeholder.setStyleSheet("font-style: italic; padding: 8px;")
                outer.addWidget(placeholder)
        elif spec.card_id == "envelope":
            _add_envelope_filter_amplitude_columns(
                outer,
                midi_port,
                spec.params,
                _panel_inner_grid_color(panel),
            )
        elif spec.card_id == "wavesample_program":
            # One column, narrow rows — fits the slim yellow column next to ENVELOPE.
            self.setMaximumWidth(WAVESAMPLE_PROGRAM_CARD_MAX_WIDTH_PX)
            for p in spec.params:
                outer.addWidget(
                    ParmRow(midi_port, p, narrow=True, narrow_columns=2),
                )
        elif spec.sections:
            grid = _panel_inner_grid_color(panel)
            heading_color = _panel_section_heading_color(panel)
            for i, sec in enumerate(spec.sections):
                if i > 0:
                    outer.addSpacing(4)
                    outer.addWidget(_section_horizontal_rule(grid))
                    outer.addSpacing(4)
                if sec.subtitle.strip():
                    sub = QLabel(sec.subtitle)
                    sub.setStyleSheet(
                        f"font-weight: bold; font-size: 11px; color: {heading_color}; "
                        "padding-top: 1px; padding-bottom: 2px;"
                    )
                    outer.addWidget(sub)
                _add_envelope_filter_amplitude_columns(
                    outer,
                    midi_port,
                    sec.params,
                    grid,
                )
        elif spec.card_id in _REFERENCE_CARD_COLUMN_COUNTS:
            _add_reference_card_columns(
                outer,
                midi_port,
                spec.params,
                _REFERENCE_CARD_COLUMN_COUNTS[spec.card_id],
                _panel_inner_grid_color(panel),
            )
        else:
            for p in spec.params:
                outer.addWidget(ParmRow(midi_port, p))

        self._midi_port = midi_port
        if show_play_preview:
            preview = QPushButton("Play test MIDI (GM)")
            preview.clicked.connect(self._on_preview_clicked)
            if spec.card_id in ("sampling", "program"):
                preview.setStyleSheet("font-size: 10px; padding: 4px 8px;")
            outer.addWidget(preview)

        pol = self.sizePolicy()
        if pol.verticalPolicy() != QSizePolicy.Policy.Maximum:
            self.setSizePolicy(pol.horizontalPolicy(), QSizePolicy.Policy.MinimumExpanding)

        self.setLayout(outer)

    def _on_preview_clicked(self, checked: bool = False) -> None:
        threading.Thread(target=lambda: _play_gm_test(self._midi_port), daemon=True).start()
