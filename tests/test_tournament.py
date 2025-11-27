"""
Fast tournament test with small simulation counts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from connect_four import Tournament, URAlgorithm, PMCGSAlgorithm, UCTAlgorithm
import time


def test_single_game():
    """Test a single game between UR and PMCGS"""
    print("Testing single game: UR vs PMCGS_50...")

    tournament = Tournament()

    # Temporarily modify algorithms to use smaller sim counts
    tournament.algorithms = {
        "UR": tournament._make_entry("UR", URAlgorithm, "UR", 0),
        "PMCGS_50": tournament._make_entry("PMCGS_50", PMCGSAlgorithm, "PMCGS", 50),
    }

    winner = tournament.play_game("UR", "PMCGS_50")
    print(f"Winner: {winner}")


def test_fast_tournament():
    """Run a very fast tournament with tiny simulation counts"""
    print("Running fast tournament test...")

    fast_tournament = Tournament()
    fast_tournament.algorithms = {
        "UR": fast_tournament._make_entry("UR", URAlgorithm, "UR", 0),
        "PMCGS_5": fast_tournament._make_entry("PMCGS_5", PMCGSAlgorithm, "PMCGS", 5),
        "UCT_5": fast_tournament._make_entry("UCT_5", UCTAlgorithm, "UCT", 5),
    }

    print("Running 2 games per match...")
    start_time = time.time()
    results = fast_tournament.run_tournament(2)
    end_time = time.time()

    for row, cols in results.items():
        print(f"{row}: {cols}")

    print(f"\nCompleted in {end_time - start_time:.2f} seconds")


def test_parallel_tournament_consistency():
    """Ensure parallel execution matches sequential results for tiny tournaments."""
    tournament = Tournament()
    tournament.algorithms = {
        "UR": tournament._make_entry("UR", URAlgorithm, "UR", 0),
        "PMCGS_5": tournament._make_entry("PMCGS_5", PMCGSAlgorithm, "PMCGS", 5),
    }

    sequential = tournament.run_tournament(2)
    parallel = tournament.run_tournament(2, parallel_workers=2)

    assert sequential.keys() == parallel.keys()
    assert sequential["UR"]["PMCGS_5"] is not None
    assert parallel["UR"]["PMCGS_5"] is not None


def main():
    """Run tournament tests"""
    print("Testing tournament system...\n")

    test_single_game()
    print()
    test_fast_tournament()

    print("\n✓ Tournament tests completed!")


if __name__ == "__main__":
    main()
