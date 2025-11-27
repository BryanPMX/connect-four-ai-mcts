"""
CS 4320 PA3: Game Playing with UCT
Connect Four Game Implementation with MCTS Algorithms

Team: [Student A, Student B]
"""

import sys
import random
import math
import time
from typing import List, Optional, Tuple, Dict


class Board:
    """Represents a Connect Four game board (7 columns x 6 rows)"""

    ROWS = 6
    COLS = 7

    def __init__(self):
        """Initialize empty board"""
        self.grid = [['O' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.heights = [0] * self.COLS  # Track how many pieces in each column

    def copy(self) -> 'Board':
        """Create a copy of the board"""
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        new_board.heights = self.heights[:]
        return new_board

    def is_valid_move(self, col: int) -> bool:
        """Check if a move is valid (column not full)"""
        return 0 <= col < self.COLS and self.heights[col] < self.ROWS

    def make_move(self, col: int, player: str) -> bool:
        """Make a move in the specified column for the given player"""
        if not self.is_valid_move(col):
            return False

        row = self.ROWS - 1 - self.heights[col]
        self.grid[row][col] = player
        self.heights[col] += 1
        return True

    def undo_move(self, col: int) -> bool:
        """Undo the last move in the specified column"""
        if self.heights[col] == 0:
            return False

        self.heights[col] -= 1
        row = self.ROWS - 1 - self.heights[col]
        self.grid[row][col] = 'O'
        return True

    def get_legal_moves(self) -> List[int]:
        """Get list of legal moves (columns that aren't full)"""
        return [col for col in range(self.COLS) if self.is_valid_move(col)]

    def is_full(self) -> bool:
        """Check if board is completely full (draw)"""
        return all(height == self.ROWS for height in self.heights)

    def check_win(self, player: str) -> bool:
        """Check if the specified player has won"""
        # Check horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if all(self.grid[row][col+i] == player for i in range(4)):
                    return True

        # Check vertical
        for row in range(self.ROWS - 3):
            for col in range(self.COLS):
                if all(self.grid[row+i][col] == player for i in range(4)):
                    return True

        # Check diagonal (down-right)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if all(self.grid[row+i][col+i] == player for i in range(4)):
                    return True

        # Check diagonal (down-left)
        for row in range(self.ROWS - 3):
            for col in range(3, self.COLS):
                if all(self.grid[row+i][col-i] == player for i in range(4)):
                    return True

        return False

    def is_terminal(self) -> Tuple[bool, int]:
        """
        Check if game is terminal
        Returns: (is_terminal, value)
        Value: 1 for Yellow win, -1 for Red win, 0 for draw
        """
        if self.check_win('Y'):
            return True, 1
        if self.check_win('R'):
            return True, -1
        if self.is_full():
            return True, 0
        return False, 0

    def load_from_file(self, filename: str) -> Tuple[str, str]:
        """Load board state from file, return (algorithm, player_to_move)"""
        with open(filename, 'r') as f:
            lines = f.readlines()

        algorithm = lines[0].strip()
        player = lines[1].strip()

        # Load board state (lines 2-7)
        for row in range(self.ROWS):
            line = lines[2 + row].strip()
            for col in range(self.COLS):
                if col < len(line):
                    self.grid[row][col] = line[col]
                    if line[col] != 'O':
                        self.heights[col] += 1

        return algorithm, player

    def __str__(self) -> str:
        """String representation of the board"""
        return '\n'.join(''.join(row) for row in self.grid)


class MCTSNode:
    """Node in the MCTS tree"""

    def __init__(self, parent: Optional['MCTSNode'] = None, move: Optional[int] = None):
        self.parent = parent
        self.move = move  # Move that led to this node
        self.children: Dict[int, 'MCTSNode'] = {}
        self.wi = 0  # Total value
        self.ni = 0  # Visit count
        self.untried_moves: List[int] = []

    def is_fully_expanded(self) -> bool:
        """Check if all possible moves have been tried"""
        return len(self.untried_moves) == 0

    def best_child(self, c_param: float = 1.4) -> Optional['MCTSNode']:
        """Select best child using UCB formula"""
        if not self.children:
            return None

        best_value = -float('inf')
        best_child = None

        for move, child in self.children.items():
            if child.ni == 0:
                return child

            # UCB formula
            exploitation = child.wi / child.ni
            exploration = c_param * math.sqrt(math.log(self.ni) / child.ni)
            ucb_value = exploitation + exploration

            if ucb_value > best_value:
                best_value = ucb_value
                best_child = child

        return best_child

    def best_child_final(self) -> Tuple[int, 'MCTSNode']:
        """Select best child for final move (no exploration)"""
        if not self.children:
            return -1, None

        best_value = -float('inf')
        best_move = -1
        best_child = None

        for move, child in self.children.items():
            if child.ni > 0:
                value = child.wi / child.ni
                if value > best_value:
                    best_value = value
                    best_move = move
                    best_child = child

        return best_move, best_child


class URAlgorithm:
    """Uniform Random algorithm"""

    def __init__(self, board: Board):
        self.board = board

    def select_move(self, player: str, verbosity: str = "None", param: int = 0) -> int:
        """Select a random legal move"""
        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            return -1

        move = random.choice(legal_moves)

        if verbosity != "None":
            print(f"FINAL Move selected: {move + 1}")  # 1-indexed

        return move


class PMCGSAlgorithm:
    """Pure Monte Carlo Game Search algorithm"""

    def __init__(self, board: Board):
        self.board = board

    def select_move(self, player: str, verbosity: str, num_simulations: int) -> int:
        """Run PMCGS and select best move"""
        root = MCTSNode()
        root.untried_moves = self.board.get_legal_moves()

        for _ in range(num_simulations):
            self._run_simulation(root, player, verbosity)

        # Print column values
        self._print_column_values(root)

        # Select final move
        final_move, _ = root.best_child_final()

        if verbosity != "None":
            print(f"FINAL Move selected: {final_move + 1}")  # 1-indexed

        return final_move

    def _run_simulation(self, root: MCTSNode, player: str, verbosity: str) -> None:
        """Run a single simulation"""
        current_board = self.board.copy()
        path = [root]
        current_player = player

        # Selection phase (random)
        while not path[-1].is_fully_expanded() and path[-1].children:
            move = random.choice(list(path[-1].children.keys()))
            child = path[-1].children[move]

            if verbosity == "Verbose":
                print(f"wi: {path[-1].wi}")
                print(f"ni: {path[-1].ni}")
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'
            path.append(child)

        # Expansion
        if not path[-1].is_fully_expanded():
            move = random.choice(path[-1].untried_moves)
            path[-1].untried_moves.remove(move)

            new_node = MCTSNode(path[-1], move)
            path[-1].children[move] = new_node
            path.append(new_node)

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'

            if verbosity == "Verbose":
                print("NODE ADDED")

        # Rollout (random moves until terminal)
        while True:
            is_terminal, value = current_board.is_terminal()
            if is_terminal:
                if verbosity == "Verbose":
                    print(f"TERMINAL NODE VALUE: {value}")
                break

            legal_moves = current_board.get_legal_moves()
            if not legal_moves:
                break

            move = random.choice(legal_moves)
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'

        # Backpropagation
        for node in reversed(path):
            node.ni += 1
            if current_player == 'Y':  # Max player perspective
                node.wi += value
            else:  # Min player perspective
                node.wi -= value

            if verbosity == "Verbose":
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")

    def _print_column_values(self, root: MCTSNode) -> None:
        """Print the estimated values for each column"""
        for col in range(Board.COLS):
            if col in root.children and root.children[col].ni > 0:
                value = root.children[col].wi / root.children[col].ni
                print(f"Column {col + 1}: {value:.3f}")
            else:
                print(f"Column {col + 1}: Null")


class UCTAlgorithm:
    """Upper Confidence Bound for Trees algorithm"""

    def __init__(self, board: Board):
        self.board = board

    def select_move(self, player: str, verbosity: str, num_simulations: int) -> int:
        """Run UCT and select best move"""
        root = MCTSNode()
        root.untried_moves = self.board.get_legal_moves()

        for _ in range(num_simulations):
            self._run_simulation(root, player, verbosity)

        # Print column values
        self._print_column_values(root)

        # Select final move
        final_move, _ = root.best_child_final()

        if verbosity != "None":
            print(f"FINAL Move selected: {final_move + 1}")  # 1-indexed

        return final_move

    def _run_simulation(self, root: MCTSNode, player: str, verbosity: str) -> None:
        """Run a single simulation with UCT selection"""
        current_board = self.board.copy()
        path = [root]
        current_player = player

        # Selection phase (UCT)
        while not path[-1].is_fully_expanded() and path[-1].children:
            if verbosity == "Verbose":
                print(f"wi: {path[-1].wi}")
                print(f"ni: {path[-1].ni}")
                # Print UCB values for children
                for i, (move, child) in enumerate(path[-1].children.items(), 1):
                    if child.ni > 0:
                        exploitation = child.wi / child.ni
                        exploration = 1.4 * math.sqrt(math.log(path[-1].ni) / child.ni)
                        ucb_value = exploitation + exploration
                        print(f"V{i}: {ucb_value:.3f}")

            # Select best child using UCB
            best_child = path[-1].best_child()
            if best_child is None:
                break

            move = best_child.move
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'
            path.append(best_child)

        # Expansion
        if not path[-1].is_fully_expanded():
            move = random.choice(path[-1].untried_moves)
            path[-1].untried_moves.remove(move)

            new_node = MCTSNode(path[-1], move)
            path[-1].children[move] = new_node
            path.append(new_node)

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'

            if verbosity == "Verbose":
                print("NODE ADDED")

        # Rollout (random moves until terminal)
        while True:
            is_terminal, value = current_board.is_terminal()
            if is_terminal:
                if verbosity == "Verbose":
                    print(f"TERMINAL NODE VALUE: {value}")
                break

            legal_moves = current_board.get_legal_moves()
            if not legal_moves:
                break

            move = random.choice(legal_moves)
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = 'Y' if current_player == 'R' else 'R'

        # Backpropagation
        for node in reversed(path):
            node.ni += 1
            if current_player == 'Y':  # Max player perspective
                node.wi += value
            else:  # Min player perspective
                node.wi -= value

            if verbosity == "Verbose":
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")

    def _print_column_values(self, root: MCTSNode) -> None:
        """Print the estimated values for each column"""
        for col in range(Board.COLS):
            if col in root.children and root.children[col].ni > 0:
                value = root.children[col].wi / root.children[col].ni
                print(f"Column {col + 1}: {value:.3f}")
            else:
                print(f"Column {col + 1}: Null")


class Tournament:
    """Manages tournament between algorithms"""

    def __init__(self):
        self.algorithms = {
            "UR": lambda board: URAlgorithm(board),
            "PMCGS_500": lambda board: PMCGSAlgorithm(board),
            "PMCGS_10000": lambda board: PMCGSAlgorithm(board),
            "UCT_500": lambda board: UCTAlgorithm(board),
            "UCT_10000": lambda board: UCTAlgorithm(board)
        }

    def play_game(self, algo1_name: str, algo2_name: str) -> str:
        """Play a single game between two algorithms"""
        board = Board()
        current_player = 'R'
        algo1 = self.algorithms[algo1_name](board)
        algo2 = self.algorithms[algo2_name](board)

        while True:
            if current_player == 'R':
                if "PMCGS" in algo1_name:
                    move = algo1.select_move(current_player, "None", 500 if "500" in algo1_name else 10000)
                elif "UCT" in algo1_name:
                    move = algo1.select_move(current_player, "None", 500 if "500" in algo1_name else 10000)
                else:  # UR
                    move = algo1.select_move(current_player, "None", 0)
            else:
                if "PMCGS" in algo2_name:
                    move = algo2.select_move(current_player, "None", 500 if "500" in algo2_name else 10000)
                elif "UCT" in algo2_name:
                    move = algo2.select_move(current_player, "None", 500 if "500" in algo2_name else 10000)
                else:  # UR
                    move = algo2.select_move(current_player, "None", 0)

            if move == -1 or not board.make_move(move, current_player):
                # Invalid move, current player loses
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

    def run_tournament(self, num_games: int = 100) -> Dict[str, Dict[str, float]]:
        """Run tournament between all algorithm pairs"""
        algo_names = list(self.algorithms.keys())
        results = {name: {opponent: 0.0 for opponent in algo_names} for name in algo_names}

        for i, algo1 in enumerate(algo_names):
            for j, algo2 in enumerate(algo_names):
                if i == j:
                    continue  # Skip self-play

                print(f"Running {algo1} vs {algo2}...")

                algo1_wins = 0
                algo2_wins = 0
                draws = 0

                for game in range(num_games):
                    winner = self.play_game(algo1, algo2)
                    if winner == 'R':
                        algo1_wins += 1
                    elif winner == 'Y':
                        algo2_wins += 1
                    else:
                        draws += 1

                # Calculate win percentage for algo1
                total_games = algo1_wins + algo2_wins + draws
                win_percentage = (algo1_wins / total_games) * 100 if total_games > 0 else 0
                results[algo1][algo2] = win_percentage

        return results


def main():
    """Main function to handle command line execution"""
    if len(sys.argv) != 4:
        print("Usage: python connect_four.py <input_file> <verbosity> <parameter>")
        sys.exit(1)

    input_file = sys.argv[1]
    verbosity = sys.argv[2]
    param = int(sys.argv[3])

    if verbosity not in ["Verbose", "Brief", "None"]:
        print("Error: verbosity must be 'Verbose', 'Brief', or 'None'")
        sys.exit(1)

    board = Board()
    algorithm, player = board.load_from_file(input_file)

    if algorithm == "UR":
        algo = URAlgorithm(board)
        algo.select_move(player, verbosity, param)
    elif algorithm == "PMCGS":
        algo = PMCGSAlgorithm(board)
        algo.select_move(player, verbosity, param)
    elif algorithm == "UCT":
        algo = UCTAlgorithm(board)
        algo.select_move(player, verbosity, param)
    else:
        print(f"Error: Unknown algorithm '{algorithm}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
