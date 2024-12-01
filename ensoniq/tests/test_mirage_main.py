import pytest
from unittest.mock import MagicMock, patch

from ensoniq.mirage_main import MirageMain, MainWindow
from ensoniq.config import MIDI_PORT_NAME, TITLE

@pytest.fixture
def mock_midi_port():
    """Mock MIDI port for testing."""
    return MagicMock()

@pytest.fixture
def mock_slider():
    """Mock slider for testing."""
    return MagicMock()

def test_main_initialization(qapp, mock_midi_port, mock_slider):
    """Test main initialization."""
    with patch('ensoniq.mirage_main.MirageSlider', return_value=mock_slider):
        main = MirageMain(mock_midi_port)
        assert main.midi_port == mock_midi_port
        assert main.slider == mock_slider

def test_main_start(qapp, mock_midi_port, mock_slider):
    """Test starting the main application."""
    with patch('ensoniq.mirage_main.MirageSlider', return_value=mock_slider):
        main = MirageMain(mock_midi_port)
        main.start()
        assert mock_slider.show.called

def test_main_stop(qapp, mock_midi_port, mock_slider):
    """Test stopping the main application."""
    with patch('ensoniq.mirage_main.MirageSlider', return_value=mock_slider):
        main = MirageMain(mock_midi_port)
        main.start()
        main.stop()
        assert mock_slider.hide.called

def test_main_window_initialization(qapp):
    """Test main window initialization."""
    window = MainWindow()
    window.show()  # Ensure the window is shown
    assert window.windowTitle() == TITLE
    assert window.midi_port_name == MIDI_PORT_NAME