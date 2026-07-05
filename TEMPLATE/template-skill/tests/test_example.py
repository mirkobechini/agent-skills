"""
Unit tests for the example script.

Run tests with:
    pytest tests/test_example.py
    pytest tests/test_example.py -v  # verbose
    pytest tests/test_example.py --cov  # with coverage
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the script functions (adjust import path as needed)
# from scripts.example import validate_input, process_data, save_output


class TestValidateInput:
    """Tests for input validation."""
    
    def test_valid_file(self):
        """Test validation with a valid file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"test": "data"}')
            temp_path = f.name
        
        try:
            # Uncomment when script is imported
            # result = validate_input(temp_path)
            # assert isinstance(result, Path)
            pass
        finally:
            Path(temp_path).unlink()
    
    def test_missing_file(self):
        """Test validation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            # Uncomment when script is imported
            # validate_input("/nonexistent/file.json")
            pass
    
    def test_empty_file(self):
        """Test validation with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                # Uncomment when script is imported
                # validate_input(temp_path)
                pass
        finally:
            Path(temp_path).unlink()


class TestProcessData:
    """Tests for data processing."""
    
    def test_process_valid_json(self):
        """Test processing valid JSON data."""
        test_data = {"key1": "value1", "key2": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            # Uncomment when script is imported
            # result = process_data(Path(temp_path), {"verbose": False})
            # assert result["status"] == "success"
            # assert result["file"] == temp_path
            pass
        finally:
            Path(temp_path).unlink()
    
    def test_process_with_verbose(self):
        """Test processing with verbose flag."""
        test_data = {"key1": "value1"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            # Uncomment when script is imported
            # result = process_data(Path(temp_path), {"verbose": True})
            # assert result["status"] == "success"
            pass
        finally:
            Path(temp_path).unlink()


class TestSaveOutput:
    """Tests for output saving."""
    
    def test_save_to_file(self):
        """Test saving output to file."""
        result = {"status": "success", "data": "test"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"
            
            # Uncomment when script is imported
            # save_output(result, str(output_file))
            # assert output_file.exists()
            
            # Verify content
            # with open(output_file) as f:
            #     saved = json.load(f)
            # assert saved == result
            pass
    
    def test_save_to_stdout(self, capsys):
        """Test output to stdout (when no file specified)."""
        result = {"status": "success", "data": "test"}
        
        # Uncomment when script is imported
        # save_output(result, None)
        # captured = capsys.readouterr()
        # assert "success" in captured.out
        pass


class TestIntegration:
    """Integration tests for end-to-end workflows."""
    
    def test_full_workflow(self):
        """Test complete workflow: validate → process → save."""
        test_data = {"key": "value"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input file
            input_file = Path(temp_dir) / "input.json"
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            output_file = Path(temp_dir) / "output.json"
            
            # Uncomment when script is imported
            # input_path = validate_input(str(input_file))
            # result = process_data(input_path, {"verbose": False})
            # save_output(result, str(output_file))
            
            # assert output_file.exists()
            pass


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
