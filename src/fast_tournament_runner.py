"""
Fast Tournament Runner - Reduced simulation counts for testing
Uses 50 simulations instead of 500/10000 to complete much faster
"""

import sys
import time
from connect_four import Tournament, Board, URAlgorithm, PMCGSAlgorithm, UCTAlgorithm


class FastTournament(Tournament):
    """Tournament with reduced simulation counts for faster execution"""

    def play_game(self, algo1_name: str, algo2_name: str) -> str:
        """Play a single game with reduced simulation counts"""
        board = Board()
        current_player = 'R'

        while True:
            if current_player == 'R':
                move = self._get_move(algo1_name, board, current_player)
            else:
                move = self._get_move(algo2_name, board, current_player)

            if move == -1 or not board.make_move(move, current_player):
                # Invalid move, current player loses
                return 'Y' if current_player == 'R' else 'R'

            is_terminal, value = board.is_terminal()
            if is_terminal:
                if value == 1:
                    return 'Y'  # Yellow wins
                elif value == -1:
                    return 'R'  # Red wins
                else:
                    return 'Draw'

            current_player = 'Y' if current_player == 'R' else 'R'

    def _get_move(self, algo_name: str, board: Board, player: str) -> int:
        """Get move from specified algorithm with reduced sim counts"""
        if algo_name == "UR":
            algo = URAlgorithm(board)
            return algo.select_move(player, "None", 0)
        elif "PMCGS_50" in algo_name:
            algo = PMCGSAlgorithm(board)
            return algo.select_move(player, "None", 50)
        elif "PMCGS_500" in algo_name:
            algo = PMCGSAlgorithm(board)
            return algo.select_move(player, "None", 50)  # Reduced for speed
        elif "UCT_50" in algo_name:
            algo = UCTAlgorithm(board)
            return algo.select_move(player, "None", 50)
        elif "UCT_500" in algo_name:
            algo = UCTAlgorithm(board)
            return algo.select_move(player, "None", 50)  # Reduced for speed
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")


def main():
    """Run fast tournament and print results"""
    if len(sys.argv) != 2:
        print("Usage: python fast_tournament_runner.py <num_games_per_match>")
        print("Example: python fast_tournament_runner.py 10")
        print("NOTE: This uses 50 simulations instead of 500/10000 for speed")
        sys.exit(1)

    num_games = int(sys.argv[1])

    print(f"Running FAST Connect Four tournament with {num_games} games per match...")
    print("NOTE: Using 50 simulations instead of 500/10000 for faster execution")
    print("=" * 70)

    # Use reduced algorithm set
    tournament = FastTournament()
    tournament.algorithms = {
        "UR": lambda board: URAlgorithm(board),
        "PMCGS_50": lambda board: PMCGSAlgorithm(board),
        "PMCGS_500": lambda board: PMCGSAlgorithm(board),  # Actually 50 sims
        "UCT_50": lambda board: UCTAlgorithm(board),
        "UCT_500": lambda board: UCTAlgorithm(board),      # Actually 50 sims
    }

    start_time = time.time()
    results = tournament.run_tournament(num_games)
    end_time = time.time()

    # Print results table
    print("\n" + "=" * 70)
    print("FAST TOURNAMENT RESULTS (50 sims instead of 500/10000)")
    print("=" * 70)
    print("<10")
    print("-" * 70)

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

    print(f"\nTournament completed in {end_time - start_time:.2f} seconds")
    # Save detailed results to file
    with open("fast_tournament_results.txt", "w") as f:
        f.write("Connect Four MCTS Fast Tournament Results\n")
        f.write("NOTE: Used 50 simulations instead of 500/10000 for speed\n")
        f.write(f"Games per match: {num_games}\n")
        f.write(f"Total time: {end_time - start_time:.2f} seconds\n\n")
        f.write("\nWin percentages (row algorithm vs column algorithm):\n\n")
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

    print("\nDetailed results saved to 'fast_tournament_results.txt'")
    print("\n⚠️  NOTE: This used 50 simulations instead of the required 500/10000.")
    print("   For the actual assignment, you'll need to run with full simulation counts")
    print("   or note the reduction in your report.")


if __name__ == "__main__":
    main()
