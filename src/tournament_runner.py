"""
Tournament Runner for Connect Four MCTS Algorithms
Runs the tournament experiments required for Part II of the assignment
"""

import sys
import time
from connect_four import Tournament


def main():
    """Run tournament and print results"""
    if len(sys.argv) != 2:
        print("Usage: python tournament_runner.py <num_games_per_match>")
        print("Example: python tournament_runner.py 100")
        sys.exit(1)

    num_games = int(sys.argv[1])

    print(f"Running Connect Four tournament with {num_games} games per match...")
    print("=" * 60)

    tournament = Tournament()
    start_time = time.time()

    results = tournament.run_tournament(num_games)

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
