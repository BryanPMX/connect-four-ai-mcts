"""
Fast Tournament Runner - Reduced simulation counts for testing
Uses 50 simulations instead of 500/10000 to complete much faster
"""

import argparse
import time
from connect_four import Tournament, URAlgorithm, PMCGSAlgorithm, UCTAlgorithm


class FastTournament(Tournament):
    """Tournament with reduced simulation counts for faster execution"""

    def __init__(self):
        super().__init__()
        self.algorithms = {
            "UR": self._make_entry("UR", URAlgorithm, "UR", 0),
            "PMCGS_50": self._make_entry("PMCGS_50", PMCGSAlgorithm, "PMCGS", 50),
            "PMCGS_500": self._make_entry("PMCGS_500", PMCGSAlgorithm, "PMCGS", 50),
            "UCT_50": self._make_entry("UCT_50", UCTAlgorithm, "UCT", 50),
            "UCT_500": self._make_entry("UCT_500", UCTAlgorithm, "UCT", 50),
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Run a reduced-speed tournament for quick testing.")
    parser.add_argument("num_games", type=int, help="Games per pairing (e.g., 10).")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Optional number of parallel worker processes.",
    )
    return parser.parse_args()


def main():
    """Run fast tournament and print results"""
    args = parse_args()
    num_games = args.num_games
    workers = args.workers if args.workers and args.workers > 1 else None

    print(f"Running FAST Connect Four tournament with {num_games} games per match...")
    if workers:
        print(f"Using up to {workers} parallel workers (still limited to 50 sims).")
    print("NOTE: Using 50 simulations instead of 500/10000 for faster execution")
    print("=" * 70)

    # Use reduced algorithm set
    tournament = FastTournament()

    start_time = time.time()
    results = tournament.run_tournament(num_games, parallel_workers=workers)
    end_time = time.time()

    # Print results table
    print("\n" + "=" * 70)
    print("FAST TOURNAMENT RESULTS (50 sims instead of 500/10000)")
    print("=" * 70)
    _print_table(results)

    print(f"\nTournament completed in {end_time - start_time:.2f} seconds")
    # Save detailed results to file
    with open("fast_tournament_results.txt", "w") as f:
        f.write("Connect Four MCTS Fast Tournament Results\n")
        f.write("NOTE: Used 50 simulations instead of 500/10000 for speed\n")
        f.write(f"Games per match: {num_games}\n")
        f.write(f"Total time: {end_time - start_time:.2f} seconds\n\n")
        f.write("\nWin percentages (row algorithm vs column algorithm):\n\n")
        _write_table(f, results)

    print("\nDetailed results saved to 'fast_tournament_results.txt'")
    print("\n⚠️  NOTE: This used 50 simulations instead of the required 500/10000.")
    print("   For the actual assignment, you'll need to run with full simulation counts")
    print("   or note the reduction in your report.")


def _print_table(results):
    algo_names = list(results.keys())
    width = 14
    header = "".ljust(width) + "".join(name.ljust(width) for name in algo_names)
    divider = "-" * len(header)
    print(header)
    print(divider)

    for row in algo_names:
        line = row.ljust(width)
        for col in algo_names:
            value = results[row][col]
            if value is None:
                line += "-".ljust(width)
            else:
                line += f"{value:6.1f}%".ljust(width)
        print(line)


def _write_table(handle, results):
    algo_names = list(results.keys())
    width = 14
    header = "".ljust(width) + "".join(name.ljust(width) for name in algo_names)
    divider = "-" * len(header)
    handle.write(header + "\n")
    handle.write(divider + "\n")

    for row in algo_names:
        line = row.ljust(width)
        for col in algo_names:
            value = results[row][col]
            if value is None:
                line += "-".ljust(width)
            else:
                line += f"{value:6.1f}%".ljust(width)
        handle.write(line + "\n")


if __name__ == "__main__":
    main()
