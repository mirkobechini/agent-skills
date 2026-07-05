#!/usr/bin/env python3
"""
Example script template for a Copilot skill.

This script demonstrates the recommended structure for skill scripts:
- Proper argument parsing
- Error handling with informative messages
- Logging for debugging
- Type hints for clarity
- Docstring for the module and functions
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def validate_input(input_file: str) -> Path:
    """
    Validate that the input file exists and is readable.
    
    Args:
        input_file: Path to the input file.
        
    Returns:
        Path object if valid.
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        PermissionError: If file isn't readable.
    """
    path = Path(input_file)
    
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {input_file}")
    
    if not path.stat().st_size > 0:
        raise ValueError(f"File is empty: {input_file}")
    
    return path


def process_data(input_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the input data according to options.
    
    Args:
        input_path: Path to input file.
        options: Dictionary of processing options.
        
    Returns:
        Dictionary with processed results.
    """
    logger.info(f"Processing {input_path.name}...")
    
    try:
        # Example: read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Apply transformations based on options
        if options.get('verbose'):
            logger.info(f"Data keys: {list(data.keys())}")
        
        result = {
            "status": "success",
            "file": str(input_path),
            "processed_items": len(data) if isinstance(data, dict) else 0,
            "output": data
        }
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {input_path.name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def save_output(result: Dict[str, Any], output_file: Optional[str]) -> None:
    """
    Save results to output file.
    
    Args:
        result: Dictionary with results.
        output_file: Path to output file (optional).
    """
    if not output_file:
        # Print to stdout
        print(json.dumps(result, indent=2))
        return
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Output saved to: {output_path}")


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Example script for Copilot skill template",
        epilog="Example: python example.py input.json --output result.json --verbose"
    )
    
    parser.add_argument(
        "input_file",
        help="Path to input file"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (default: print to stdout)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Validate input
        input_path = validate_input(args.input_file)
        
        # Process
        options = {
            "verbose": args.verbose
        }
        result = process_data(input_path, options)
        
        # Save output
        save_output(result, args.output)
        
        return 0
        
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
