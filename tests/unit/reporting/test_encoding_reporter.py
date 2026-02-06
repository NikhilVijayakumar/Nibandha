import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from nibandha.reporting.quality.domain.encoding_reporter import EncodingReporter

class TestEncodingReporter:
    @pytest.fixture
    def reporter(self, tmp_path):
        return EncodingReporter(source_root=str(tmp_path))
        
    def test_pass_on_valid_utf8(self, reporter, tmp_path):
        # Create valid utf-8 file
        f = tmp_path / "valid.py"
        f.write_text("print('Hello 🌍')", encoding='utf-8')
        
        result = reporter.run()
        
        assert result["status"] == "PASS"
        assert result["violation_count"] == 0
        assert result["details"]["non_utf8"] == []
        assert result["details"]["bom_present"] == []
        
    def test_fail_on_bom(self, reporter, tmp_path):
        # Create file with BOM
        f = tmp_path / "bom.py"
        # UTF-8 BOM is \xef\xbb\xbf
        with open(f, 'wb') as fb:
            fb.write(b'\xef\xbb\xbfprint("Hello")')
            
        result = reporter.run()
        
        # We flag BOM as violation
        assert result["status"] == "FAIL"
        assert result["violation_count"] == 1
        assert len(result["details"]["bom_present"]) == 1
        assert "bom.py" in result["details"]["bom_present"][0]["file"]

    def test_fail_on_latin1(self, reporter, tmp_path):
        # Create invalid utf-8 file (latin-1 with special char)
        f = tmp_path / "latin.py"
        # \xe9 is 'é' in latin-1, but invalid start byte in utf-8
        with open(f, 'wb') as fb:
             fb.write(b'print("\xe9")')
             
        result = reporter.run()
        
        assert result["status"] == "FAIL"
        assert result["violation_count"] == 1
        assert len(result["details"]["non_utf8"]) == 1
        assert "latin.py" in result["details"]["non_utf8"][0]["file"]

    def test_ignore_excluded_extensions(self, reporter, tmp_path):
        # Create binary file with unknown extension
        f = tmp_path / "image.png"
        f.write_bytes(b'\xff\xd8\xff')
        
        result = reporter.run()
        
        assert result["status"] == "PASS"
        assert result["violation_count"] == 0
