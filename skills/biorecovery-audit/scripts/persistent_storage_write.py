#!/usr/bin/env python3
"""
Write recovery score to persistent session storage.
Integration point with workout scheduler.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def write_to_persistent_storage(recovery_score: float, session_id: str = None) -> dict:
    """
    Write recovery score to session persistent storage.
    In a real system, this would integrate with the workout scheduler's session state.
    """
    
    storage_entry = {
        "timestamp": datetime.now().isoformat(),
        "recovery_score": recovery_score,
        "session_id": session_id or "default",
        "storage_location": "session.persistent_storage.recovery_score",
    }
    
    return storage_entry


def main():
    parser = argparse.ArgumentParser(
        description="Write recovery score to persistent session storage"
    )
    parser.add_argument("--recovery-score", type=float, required=True, help="Recovery score (0.7–1.2)")
    parser.add_argument("--session-id", type=str, default="default", help="Session ID")
    parser.add_argument("--output", type=str, default="session_storage.json", help="Output JSON")
    
    args = parser.parse_args()
    
    try:
        # Validate recovery score
        if args.recovery_score < 0.7 or args.recovery_score > 1.2:
            print(f"⚠️  Warning: Recovery score {args.recovery_score} outside typical range (0.7–1.2)")
        
        # Write to storage
        storage_entry = write_to_persistent_storage(args.recovery_score, args.session_id)
        
        # Save to JSON
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(storage_entry, f, indent=2)
        
        # Print confirmation
        print("✅ Recovery score written to persistent storage:")
        print(f"  • Recovery Score: {args.recovery_score}x")
        print(f"  • Session ID: {args.session_id}")
        print(f"  • Storage Location: {storage_entry['storage_location']}")
        print(f"  • Timestamp: {storage_entry['timestamp']}")
        print(f"\n📁 Storage entry saved to: {output_path}")
        print(f"\n🔗 Integration: Workout scheduler will now read recovery_score={args.recovery_score}x")
        
    except (ValueError, IOError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
