import pytest
from unittest.mock import MagicMock

from ensoniq.mirage_slider import MirageSlider

@pytest.fixture
def mock_midi_port():
    """Mock MIDI port for testing."""
    return MagicMock()

def test_slider_initialization(qapp, mock_midi_port):
    """Test slider initialization."""
    slider = MirageSlider(mock_midi_port, 100, "Test Slider", 0x42)
    assert slider.title == "Test Slider"
    assert slider.slider.maximum() == 100
    assert slider.slider.value() == 0

def test_slider_value_change(qapp, qtbot, mock_midi_port):
    """Test slider value changes and UI updates."""
    slider = MirageSlider(mock_midi_port, 100, "Test Slider", 0x42)
    qtbot.addWidget(slider)

    slider.slider.setValue(50)
    assert slider.value_label.text() == "50"
    assert slider.group_box.title() == "Test Slider (0x42)"

def test_slider_decrement(qapp, qtbot, mock_midi_port):
    """Test decrementing the slider value."""
    slider = MirageSlider(mock_midi_port, 100, "Test Slider", 0x42)
    qtbot.addWidget(slider)

    slider.slider.setValue(100)
    slider.decrease_value()
    assert slider.slider.value() == 99

def test_send_midi_message(qapp, mock_midi_port):
    """Test sending MIDI messages."""
    slider = MirageSlider(mock_midi_port, 100, "Test Slider", 0x42)
    slider.send_midi_message(50)

    # Check that the MIDI message is sent
    assert mock_midi_port.send.called
    midi_message = mock_midi_port.send.call_args[0][0]
    assert midi_message.type == 'sysex'
    assert list(midi_message.data[1:]) == [0x01, 0x42, 50]
