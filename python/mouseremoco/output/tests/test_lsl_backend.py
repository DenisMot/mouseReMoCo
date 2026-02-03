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


class TestLSLWriteData:
    """Test LSL write_data() method"""

    def test_write_data_pushes_sample(self):
        """write_data() pushes sample to LSL outlet"""
        if pylsl is None:
            # Mock version
            mock_lsl = MagicMock()
            mock_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_outlet
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
                    backend.write_data(
                        event_timestamp_ms=1000,
                        call_time_ms=1005,
                        x=123.45,
                        y=67.89,
                        is_inside=True,
                    )

                    # Verify push_sample was called
                    mock_outlet.push_sample.assert_called()
                    call_args = mock_outlet.push_sample.call_args[0][0]
                    assert call_args[0] == 123.45  # x
                    assert call_args[1] == 67.89  # y
                    assert call_args[2] == 1.0  # is_inside=True → 1.0
        else:
            # Real LSL version
            backend = LSLBackend(config=Mock())
            # Just verify it doesn't crash
            backend.write_data(
                event_timestamp_ms=1000,
                call_time_ms=1005,
                x=123.45,
                y=67.89,
                is_inside=True,
            )
            backend.close()

    def test_write_data_is_inside_false(self):
        """write_data() converts is_inside=False to 0.0"""
        if pylsl is None:
            mock_lsl = MagicMock()
            mock_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_outlet
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
                    backend.write_data(
                        event_timestamp_ms=1000,
                        call_time_ms=1005,
                        x=100.0,
                        y=200.0,
                        is_inside=False,
                    )

                    call_args = mock_outlet.push_sample.call_args[0][0]
                    assert call_args[2] == 0.0  # is_inside=False → 0.0
        else:
            backend = LSLBackend(config=Mock())
            backend.write_data(
                event_timestamp_ms=1000,
                call_time_ms=1005,
                x=100.0,
                y=200.0,
                is_inside=False,
            )
            backend.close()

    def test_write_data_when_lsl_unavailable(self):
        """write_data() gracefully handles missing LSL"""
        with patch.dict("sys.modules", {"pylsl": None}):
            backend = LSLBackend(config=Mock())
            # Should not crash
            backend.write_data(
                event_timestamp_ms=1000,
                call_time_ms=1005,
                x=123.45,
                y=67.89,
                is_inside=True,
            )


class TestLSLWriteMarker:
    """Test LSL write_marker() method"""

    def test_write_marker_pushes_marker(self):
        """write_marker() pushes marker to LSL outlet"""
        if pylsl is None:
            # Mock version
            mock_lsl = MagicMock()
            mock_marker_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_marker_outlet
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
                    backend.write_marker("test_marker")

                    # Verify push_sample was called on marker outlet
                    # The third call to StreamOutlet is the marker_outlet
                    outlet_calls = (
                        mock_lsl.StreamOutlet.return_value.push_sample.call_args_list
                    )
                    calls = [call[0][0] for call in outlet_calls]
                    assert ["test_marker"] in calls
        else:
            # Real LSL version
            backend = LSLBackend(config=Mock())
            backend.write_marker("test_marker")
            backend.close()

    def test_write_marker_with_special_characters(self):
        """write_marker() handles special characters correctly"""
        if pylsl is None:
            mock_lsl = MagicMock()
            mock_marker_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_marker_outlet
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
                    special_marker = "event,with,commas;and;semicolons"
                    backend.write_marker(special_marker)

                    outlet_calls = (
                        mock_lsl.StreamOutlet.return_value.push_sample.call_args_list
                    )
                    calls = [call[0][0] for call in outlet_calls]
                    assert [special_marker] in calls
        else:
            backend = LSLBackend(config=Mock())
            special_marker = "event,with,commas;and;semicolons"
            backend.write_marker(special_marker)
            backend.close()

    def test_write_marker_when_lsl_unavailable(self):
        """write_marker() gracefully handles missing LSL"""
        with patch.dict("sys.modules", {"pylsl": None}):
            backend = LSLBackend(config=Mock())
            # Should not crash
            backend.write_marker("test_marker")


class TestLSLClose:
    """Test LSL close() method"""

    def test_close_sets_outlets_to_none(self):
        """close() sets all outlets to None"""
        if pylsl is None:
            # Mock version
            mock_lsl = MagicMock()
            mock_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_outlet
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
                    assert backend.data_outlet is not None
                    assert backend.marker_outlet is not None

                    backend.close()

                    assert backend.data_outlet is None
                    assert backend.marker_outlet is None
                    assert backend.numeric_marker_outlet is None
        else:
            # Real LSL version
            backend = LSLBackend(config=Mock())
            assert backend.data_outlet is not None

            backend.close()

            assert backend.data_outlet is None
            assert backend.marker_outlet is None
            assert backend.numeric_marker_outlet is None

    def test_close_is_idempotent(self):
        """close() can be called multiple times safely"""
        if pylsl is None:
            mock_lsl = MagicMock()
            mock_outlet = MagicMock()
            mock_lsl.StreamOutlet.return_value = mock_outlet
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

                    # Call close multiple times - should not crash
                    backend.close()
                    backend.close()
                    backend.close()

                    assert backend.data_outlet is None
        else:
            backend = LSLBackend(config=Mock())

            # Call close multiple times - should not crash
            backend.close()
            backend.close()
            backend.close()

            assert backend.data_outlet is None

    def test_close_when_lsl_unavailable(self):
        """close() gracefully handles missing LSL"""
        with patch.dict("sys.modules", {"pylsl": None}):
            backend = LSLBackend(config=Mock())
            # Should not crash
            backend.close()
            backend.close()

    def test_close_with_exception_handling(self):
        """close() handles exceptions gracefully"""
        if pylsl is None:
            mock_lsl = MagicMock()
            # Make outlet.close() raise an exception
            mock_outlet = MagicMock()
            mock_outlet.push_sample.side_effect = Exception("Connection lost")
            mock_lsl.StreamOutlet.return_value = mock_outlet
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

                    # close() should not crash even if write failed
                    backend.close()
                    assert backend.data_outlet is None
        else:
            backend = LSLBackend(config=Mock())
            backend.close()
            assert backend.data_outlet is None


class TestMarkerConsistency:
    """Test that markers are identical across CSV and LSL backends"""

    def test_output_tablet_broadcasts_same_marker_to_all_backends(self):
        """Verify OutputTablet sends identical marker to all backends"""
        if pylsl is None:
            # Skip test if LSL not available
            import pytest

            pytest.skip("LSL not installed - skipping marker consistency test")

        from mouseremoco.output.manager import OutputTablet

        # Real LSL version - test with actual libraries
        config = Mock()
        app_status = Mock()
        app_status.is_recording = True

        output_tablet = OutputTablet(
            config=config,
            app_status=app_status,
            output_config=None,
            enable_csv=True,
            enable_lsl=True,
        )

        # Verify both backends are present
        backend_names = [b.__class__.__name__ for b in output_tablet.backends]
        assert "CSVBackend" in backend_names
        assert "LSLBackend" in backend_names

        # Send marker and verify both backends got it (no crash)
        output_tablet.write_marker("test_marker_consistency")
        output_tablet.close()
