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
        # Create mock LSL module
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

                # Assertions
                assert backend.lsl is not None
                assert backend.lsl == mock_lsl
                assert backend.data_outlet is not None
                assert backend.marker_outlet is not None
                assert backend.numeric_marker_outlet is not None
                assert mock_lsl.StreamInfo.call_count == 3

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

                # Verify StreamInfo was called with correct parameters
                calls = mock_lsl.StreamInfo.call_args_list

                # First call: data stream
                assert calls[0][1]["name"] == "MouseData"
                assert calls[0][1]["type"] == "MoCap"
                assert calls[0][1]["channel_count"] == 3
                assert calls[0][1]["source_id"] == "mouseReMoCo"

                # Second call: marker stream
                assert calls[1][1]["name"] == "MouseMarkers"
                assert calls[1][1]["type"] == "Markers"
                assert calls[1][1]["channel_count"] == 1

                # Third call: numeric marker stream
                assert calls[2][1]["name"] == "MouseMarkersNumeric"
                assert calls[2][1]["type"] == "Markers"
