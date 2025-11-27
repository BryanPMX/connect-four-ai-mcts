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
    print("<10")
    print("-" * 60)

    algo_names = list(results.keys())
    header = "<10" + "".join("<10")
    print(header)

    for algo1 in algo_names:
        row = "<10"
        for algo2 in algo_names:
            if algo1 == algo2:
                row += "<10"
            else:
                row += "<10.1f"
        print(row)

    print("\nTournament completed in {:.2f} seconds".format(end_time - start_time))

    # Save detailed results to file
    with open("tournament_results.txt", "w") as f:
        f.write("Connect Four MCTS Tournament Results\n")
        f.write(f"Games per match: {num_games}\n")
        f.write(f"Total time: {end_time - start_time:.2f} seconds\n\n")

        f.write("Win percentages (row algorithm vs column algorithm):\n\n")
        f.write("Algorithm".ljust(15))
        for name in algo_names:
            f.write(name.ljust(15))
        f.write("\n" + "-" * (15 * (len(algo_names) + 1)) + "\n")

        for algo1 in algo_names:
            f.write(algo1.ljust(15))
            for algo2 in algo_names:
                if algo1 == algo2:
                    f.write("-".ljust(15))
                else:
                    f.write(".1f")
            f.write("\n")

    print("\nDetailed results saved to 'tournament_results.txt'")


if __name__ == "__main__":
    main()
