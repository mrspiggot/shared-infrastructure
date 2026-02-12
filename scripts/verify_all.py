#!/usr/bin/env python3
"""Run all database verifications and optionally seed with test data.

This is the master verification script that checks both Horizon (Neo4j)
and LuciCRM (SQLite/PostgreSQL) databases.

Usage:
    python scripts/verify_all.py          # Verify only
    python scripts/verify_all.py --seed   # Verify and seed test data
    python scripts/verify_all.py --clear  # Clear and re-seed test data
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_script(script_path: str, args: list[str] = None) -> bool:
    """Run a Python script and return success status."""
    args = args or []
    full_path = Path(script_path)
    
    if not full_path.exists():
        print(f"✗ Script not found: {script_path}")
        return False
    
    # Run the script from its directory
    cwd = full_path.parent
    result = subprocess.run(
        [sys.executable, full_path.name] + args,
        cwd=cwd,
        capture_output=False
    )
    
    return result.returncode == 0


def main():
    """Run all database verifications."""
    args = sys.argv[1:]
    seed = "--seed" in args
    clear = "--clear" in args
    
    # Get workspace root (parent of scripts/)
    workspace = Path(__file__).parent.parent
    os.chdir(workspace)
    
    results = {}
    
    # ==========================================
    # Horizon (Neo4j)
    # ==========================================
    print("=" * 60)
    print("HORIZON (Neo4j)")
    print("=" * 60)
    
    horizon_verify = workspace / "Horizon" / "scripts" / "verify_neo4j.py"
    horizon_seed = workspace / "Horizon" / "scripts" / "seed_test_data.py"
    
    if horizon_verify.exists():
        results["horizon_verify"] = run_script(str(horizon_verify))
    else:
        print(f"⚠ Horizon verify script not found at {horizon_verify}")
        results["horizon_verify"] = None
    
    if seed or clear:
        print("\n--- Seeding Horizon ---")
        if horizon_seed.exists():
            seed_args = ["--clear"] if clear else []
            results["horizon_seed"] = run_script(str(horizon_seed), seed_args)
        else:
            print(f"⚠ Horizon seed script not found at {horizon_seed}")
            results["horizon_seed"] = None
    
    # ==========================================
    # LuciCRM (SQLite/PostgreSQL)
    # ==========================================
    print("\n" + "=" * 60)
    print("LuciCRM (SQLite/PostgreSQL)")
    print("=" * 60)
    
    lucicrm_verify = workspace / "lucicrm-analysis" / "scripts" / "verify_database.py"
    lucicrm_seed = workspace / "lucicrm-analysis" / "scripts" / "seed_test_data.py"
    
    if lucicrm_verify.exists():
        results["lucicrm_verify"] = run_script(str(lucicrm_verify))
    else:
        print(f"⚠ LuciCRM verify script not found at {lucicrm_verify}")
        results["lucicrm_verify"] = None
    
    if seed or clear:
        print("\n--- Seeding LuciCRM ---")
        if lucicrm_seed.exists():
            seed_args = ["--clear"] if clear else []
            results["lucicrm_seed"] = run_script(str(lucicrm_seed), seed_args)
        else:
            print(f"⚠ LuciCRM seed script not found at {lucicrm_seed}")
            results["lucicrm_seed"] = None
    
    # ==========================================
    # Summary
    # ==========================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
            all_passed = False
        else:
            status = "○ SKIPPED"
        print(f"  {name}: {status}")
    
    if all_passed:
        print("\n✓ All verifications complete!")
    else:
        print("\n⚠ Some verifications failed - check output above")
        sys.exit(1)


if __name__ == "__main__":
    main()
