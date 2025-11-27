"""
Fast tournament test with small simulation counts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from connect_four import Tournament, Board, URAlgorithm, PMCGSAlgorithm, UCTAlgorithm
import time


def test_single_game():
    """Test a single game between UR and PMCGS"""
    print("Testing single game: UR vs PMCGS_50...")

    tournament = Tournament()

    # Temporarily modify algorithms to use smaller sim counts
    original_algorithms = tournament.algorithms.copy()
    tournament.algorithms = {
        "UR": lambda board: URAlgorithm(board),
        "PMCGS_50": lambda board: PMCGSAlgorithm(board),
    }

    winner = tournament.play_game("UR", "PMCGS_50")
    print(f"Winner: {winner}")

    # Restore original
    tournament.algorithms = original_algorithms


def test_fast_tournament():
    """Run a very fast tournament with tiny simulation counts"""
    print("Running fast tournament test...")

    # Create a modified tournament class with smaller sim counts
    class FastTournament(Tournament):
        def play_game(self, algo1_name: str, algo2_name: str) -> str:
            """Play a single game with very small simulation counts"""
            board = Board()
            current_player = 'R'

            while True:
                if current_player == 'R':
                    if algo1_name == "UR":
                        algo = URAlgorithm(board)
                        move = algo.select_move(current_player, "None", 0)
                    else:  # MCTS algorithms with small sim count
                        if "PMCGS" in algo1_name:
                            algo = PMCGSAlgorithm(board)
                        else:
                            algo = UCTAlgorithm(board)
                        move = algo.select_move(current_player, "None", 5)  # Very small
                else:
                    if algo2_name == "UR":
                        algo = URAlgorithm(board)
                        move = algo.select_move(current_player, "None", 0)
                    else:  # MCTS algorithms with small sim count
                        if "PMCGS" in algo2_name:
                            algo = PMCGSAlgorithm(board)
                        else:
                            algo = UCTAlgorithm(board)
                        move = algo.select_move(current_player, "None", 5)  # Very small

                if move == -1 or not board.make_move(move, current_player):
                    return 'Y' if current_player == 'R' else 'R'

                is_terminal, value = board.is_terminal()
                if is_terminal:
                    if value == 1:
                        return 'Y'
                    elif value == -1:
                        return 'R'
                    else:
                        return 'Draw'

                current_player = 'Y' if current_player == 'R' else 'R'

    fast_tournament = FastTournament()
    fast_tournament.algorithms = {
        "UR": lambda board: URAlgorithm(board),
        "PMCGS_5": lambda board: PMCGSAlgorithm(board),
        "UCT_5": lambda board: UCTAlgorithm(board),
    }

    algo_names = ["UR", "PMCGS_5", "UCT_5"]

    print("Running 2 games per match...")
    start_time = time.time()

    for algo1 in algo_names:
        for algo2 in algo_names:
            if algo1 == algo2:
                continue

            print(f"  {algo1} vs {algo2}: ", end="")

            algo1_wins = 0
            for _ in range(2):
                winner = fast_tournament.play_game(algo1, algo2)
                if winner == 'R':
                    algo1_wins += 1

            win_rate = algo1_wins / 2 * 100
            print(".1f")

    end_time = time.time()
    print(f"\nCompleted in {end_time - start_time:.2f} seconds")


def main():
    """Run tournament tests"""
    print("Testing tournament system...\n")

    test_single_game()
    print()
    test_fast_tournament()

    print("\n✓ Tournament tests completed!")


if __name__ == "__main__":
    main()
