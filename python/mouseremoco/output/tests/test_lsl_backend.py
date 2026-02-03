from unittest.mock import Mock, patch, MagicMock
from mouseremoco.output.backends import LSLBackend
import sys

# Import pylsl early to register it in sys.modules
try:
    import pylsl
except ImportError:
    pylsl = None


class TestLSLAvailability:
    """Test LSL library availability detection"""

    @classmethod
    def setup_class(cls):
        """Print LSL availability at the start of tests"""
        lsl_available = "pylsl" in sys.modules and sys.modules["pylsl"] is not None
        print(f"\n{'='*60}")
        print(f"LSL: {'✓ INSTALLED' if lsl_available else '✗ NOT INSTALLED (mocks)'}")
        print(f"{'='*60}\n")

    def test_lsl_available_initialization(self):
        """When LSL is available, backend initializes with outlets"""
        if pylsl is None:
            # Fall back to mocks if LSL not available
            mock_lsl = MagicMock()
            mock_stream_info = MagicMock()
            mock_stream_info.desc.return_value.append_child.return_value = MagicMock()
            mock_lsl.StreamInfo.return_value = mock_stream_info
            mock_lsl.IRREGULAR_RATE = 0
            mock_lsl.cf_float32 = 0
            mock_lsl.cf_string = 1
            mock_lsl.cf_int32 = 2

            with patch.dict("sys.modules", {"pylsl": mock_lsl}):
                with patch("mouseremoco.output.backends.pylsl", mock_lsl, create=True):
                    backend = LSLBackend(config=Mock())
                    assert backend.lsl is not None
                    assert backend.lsl == mock_lsl
        else:
            # Use real LSL when available
            backend = LSLBackend(config=Mock())
            assert backend.lsl is not None
            assert backend.data_outlet is not None
            assert backend.marker_outlet is not None
            assert backend.numeric_marker_outlet is not None
            backend.close()

    def test_lsl_unavailable_graceful_degradation(self):
        """When LSL is unavailable, backend gracefully disables itself"""
        with patch.dict("sys.modules", {"pylsl": None}):
            backend = LSLBackend(config=Mock())

            # Assertions
            assert backend.lsl is None
            assert backend.data_outlet is None
            assert backend.marker_outlet is None
            assert backend.numeric_marker_outlet is None

    def test_lsl_stream_names_correct(self):
        """Verify stream names and metadata are correct"""
        if pylsl is None:
            # Fall back to mocks if LSL not available
            mock_lsl = MagicMock()
            mock_stream_info = MagicMock()
            mock_stream_info.desc.return_value.append_child.return_value = MagicMock()
            mock_lsl.StreamInfo.return_value = mock_stream_info
            mock_lsl.IRREGULAR_RATE = 0
            mock_lsl.cf_float32 = 0
            mock_lsl.cf_string = 1
            mock_lsl.cf_int32 = 2

            with patch.dict("sys.modules", {"pylsl": mock_lsl}):
                with patch("mouseremoco.output.backends.pylsl", mock_lsl, create=True):
                    LSLBackend(config=Mock())
                    calls = mock_lsl.StreamInfo.call_args_list
                    assert calls[0][1]["name"] == "MouseData"
                    assert calls[1][1]["name"] == "MouseMarkers"
                    assert calls[2][1]["name"] == "MouseMarkersNumeric"
        else:
            # Use real LSL when available
            backend = LSLBackend(config=Mock())
            assert backend.lsl is not None
            assert backend.data_outlet is not None
            backend.close()
