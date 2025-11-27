"""
Tournament Runner for Connect Four MCTS Algorithms
Runs the tournament experiments required for Part II of the assignment
"""

import argparse
import time
from connect_four import Tournament


def parse_args():
    parser = argparse.ArgumentParser(description="Run the full CS4320 PA3 tournament.")
    parser.add_argument(
        "num_games",
        type=int,
        help="Number of games per algorithm pairing (assignment requires 100).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Optional number of parallel worker processes to speed up tournaments.",
    )
    return parser.parse_args()


def main():
    """Run tournament and print results"""
    args = parse_args()
    num_games = args.num_games
    workers = args.workers if args.workers and args.workers > 1 else None

    print(f"Running Connect Four tournament with {num_games} games per match...")
    if workers:
        print(f"Using up to {workers} parallel workers for game simulation.")
    print("=" * 60)

    tournament = Tournament()
    start_time = time.time()

    results = tournament.run_tournament(num_games, parallel_workers=workers)

    end_time = time.time()

    # Print results table
    print("\n" + "=" * 60)
    print("TOURNAMENT RESULTS")
    print("=" * 60)
    _print_table(results)

    print("\nTournament completed in {:.2f} seconds".format(end_time - start_time))

    # Save detailed results to file
    with open("tournament_results.txt", "w") as f:
        f.write("Connect Four MCTS Tournament Results\n")
        f.write(f"Games per match: {num_games}\n")
        if workers:
            f.write(f"Parallel workers: {workers}\n")
        f.write(f"Total time: {end_time - start_time:.2f} seconds\n\n")

        f.write("Win percentages (row algorithm vs column algorithm):\n\n")
        _write_table(f, results)

    print("\nDetailed results saved to 'tournament_results.txt'")


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
