"""
CS 4320 PA3: Game Playing with UCT
Connect Four Game Implementation with MCTS Algorithms

Team: [Student A, Student B]
"""

import sys
import random
import math
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Optional, Tuple


def _opponent(player: str) -> str:
    """Return the opposing player's token."""
    return 'Y' if player == 'R' else 'R'


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

    def __init__(
        self,
        parent: Optional['MCTSNode'] = None,
        move: Optional[int] = None,
        player_to_move: str = 'Y',
    ):
        self.parent = parent
        self.move = move  # Move that led to this node (0-indexed col)
        self.children: Dict[int, 'MCTSNode'] = {}
        self.wi = 0.0  # Total accumulated value from Yellow's perspective
        self.ni = 0  # Visit count
        self.untried_moves: List[int] = []
        self.player_to_move = player_to_move

    def is_fully_expanded(self) -> bool:
        """Check if all possible moves have been tried"""
        return len(self.untried_moves) == 0

    def best_child(self, c_param: float = 1.4) -> Optional['MCTSNode']:
        """Select best child using the UCB rule with min/max behaviour."""
        if not self.children:
            return None

        unexplored = [child for child in self.children.values() if child.ni == 0]
        if unexplored:
            return random.choice(unexplored)

        if self.player_to_move == 'Y':
            best_value = -float('inf')
            comparator = lambda current, best: current > best
        else:
            best_value = float('inf')
            comparator = lambda current, best: current < best

        best_child = None

        for child in self.children.values():
            exploitation = child.wi / child.ni
            exploration = c_param * math.sqrt(math.log(self.ni) / child.ni)
            ucb_value = exploitation + exploration

            if comparator(ucb_value, best_value):
                best_value = ucb_value
                best_child = child

        return best_child

    def best_child_final(self) -> Tuple[int, Optional['MCTSNode']]:
        """Select best child for final move (no exploration)"""
        if not self.children:
            return -1, None

        if self.player_to_move == 'Y':
            best_value = -float('inf')
            comparator = lambda current, best: current > best
        else:
            best_value = float('inf')
            comparator = lambda current, best: current < best

        best_move = -1
        best_child = None

        for move, child in self.children.items():
            if child.ni > 0:
                value = child.wi / child.ni
                if comparator(value, best_value):
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
        root = MCTSNode(player_to_move=player)
        root.untried_moves = self.board.get_legal_moves().copy()

        for _ in range(num_simulations):
            self._run_simulation(root, player, verbosity)

        # Print column values
        if verbosity in ("Verbose", "Brief"):
            self._print_column_values(root)

        # Select final move
        final_move, _ = root.best_child_final()

        if verbosity in ("Verbose", "Brief"):
            print(f"FINAL Move selected: {final_move + 1}")  # 1-indexed

        return final_move

    def _run_simulation(self, root: MCTSNode, player: str, verbosity: str) -> None:
        """Run a single simulation"""
        current_board = self.board.copy()
        path = [root]

        # Selection phase (random choice among expanded children)
        while path[-1].is_fully_expanded() and path[-1].children:
            node = path[-1]
            move = random.choice(list(node.children.keys()))
            child = node.children[move]

            if verbosity == "Verbose":
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, node.player_to_move)
            path.append(child)

        node = path[-1]
        is_terminal, value = current_board.is_terminal()

        # Expansion
        if not is_terminal and not node.is_fully_expanded():
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            current_board.make_move(move, node.player_to_move)

            next_player = _opponent(node.player_to_move)
            new_node = MCTSNode(node, move, next_player)
            new_node.untried_moves = current_board.get_legal_moves().copy()
            node.children[move] = new_node
            path.append(new_node)

            if verbosity == "Verbose":
                print("NODE ADDED")

            is_terminal, value = current_board.is_terminal()
            node = new_node

        # Rollout (random moves until terminal)
        current_player = path[-1].player_to_move
        if is_terminal and verbosity == "Verbose":
            print(f"TERMINAL NODE VALUE: {value}")

        while not is_terminal:
            legal_moves = current_board.get_legal_moves()
            if not legal_moves:
                value = 0
                break

            move = random.choice(legal_moves)
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = _opponent(current_player)
            is_terminal, value = current_board.is_terminal()

            if is_terminal and verbosity == "Verbose":
                print(f"TERMINAL NODE VALUE: {value}")

        # Backpropagation (values already from Yellow perspective)
        for node in reversed(path):
            node.ni += 1
            node.wi += value

            if verbosity == "Verbose":
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")

    def _print_column_values(self, root: MCTSNode) -> None:
        """Print the estimated values for each column"""
        for col in range(Board.COLS):
            if not self.board.is_valid_move(col):
                print(f"Column {col + 1}: Null")
                continue

            if col in root.children and root.children[col].ni > 0:
                value = root.children[col].wi / root.children[col].ni
                print(f"Column {col + 1}: {value:.3f}")
            else:
                print(f"Column {col + 1}: 0.000")


class UCTAlgorithm:
    """Upper Confidence Bound for Trees algorithm"""

    def __init__(self, board: Board):
        self.board = board

    def select_move(self, player: str, verbosity: str, num_simulations: int) -> int:
        """Run UCT and select best move"""
        root = MCTSNode(player_to_move=player)
        root.untried_moves = self.board.get_legal_moves().copy()

        for _ in range(num_simulations):
            self._run_simulation(root, player, verbosity)

        # Print column values
        if verbosity in ("Verbose", "Brief"):
            self._print_column_values(root)

        # Select final move
        final_move, _ = root.best_child_final()

        if verbosity in ("Verbose", "Brief"):
            print(f"FINAL Move selected: {final_move + 1}")  # 1-indexed

        return final_move

    def _run_simulation(self, root: MCTSNode, player: str, verbosity: str) -> None:
        """Run a single simulation with UCT selection"""
        current_board = self.board.copy()
        path = [root]

        # Selection phase (UCT)
        while path[-1].is_fully_expanded() and path[-1].children:
            node = path[-1]
            if verbosity == "Verbose":
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")
                for i, (move, child) in enumerate(sorted(node.children.items()), 1):
                    if child.ni > 0 and node.ni > 0:
                        exploitation = child.wi / child.ni
                        exploration = 1.4 * math.sqrt(math.log(node.ni) / child.ni)
                        ucb_value = exploitation + exploration
                        print(f"V{i}: {ucb_value:.3f}")
                    else:
                        print(f"V{i}: INF")

            best_child = path[-1].best_child()
            if best_child is None or best_child.move is None:
                break

            move = best_child.move
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, node.player_to_move)
            path.append(best_child)

        node = path[-1]
        is_terminal, value = current_board.is_terminal()

        # Expansion
        if not is_terminal and not node.is_fully_expanded():
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            current_board.make_move(move, node.player_to_move)

            next_player = _opponent(node.player_to_move)
            new_node = MCTSNode(node, move, next_player)
            new_node.untried_moves = current_board.get_legal_moves().copy()
            node.children[move] = new_node
            path.append(new_node)

            if verbosity == "Verbose":
                print("NODE ADDED")

            is_terminal, value = current_board.is_terminal()
            node = new_node

        # Rollout (random moves until terminal)
        current_player = path[-1].player_to_move
        if is_terminal and verbosity == "Verbose":
            print(f"TERMINAL NODE VALUE: {value}")

        while not is_terminal:
            legal_moves = current_board.get_legal_moves()
            if not legal_moves:
                value = 0
                break

            move = random.choice(legal_moves)
            if verbosity == "Verbose":
                print(f"Move selected: {move + 1}")

            current_board.make_move(move, current_player)
            current_player = _opponent(current_player)
            is_terminal, value = current_board.is_terminal()

            if is_terminal and verbosity == "Verbose":
                print(f"TERMINAL NODE VALUE: {value}")

        # Backpropagation
        for node in reversed(path):
            node.ni += 1
            node.wi += value

            if verbosity == "Verbose":
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")

    def _print_column_values(self, root: MCTSNode) -> None:
        """Print the estimated values for each column"""
        for col in range(Board.COLS):
            if not self.board.is_valid_move(col):
                print(f"Column {col + 1}: Null")
                continue

            if col in root.children and root.children[col].ni > 0:
                value = root.children[col].wi / root.children[col].ni
                print(f"Column {col + 1}: {value:.3f}")
            else:
                print(f"Column {col + 1}: 0.000")


class Tournament:
    """Manages tournament between algorithms"""

    def __init__(self):
        self.algorithms = {
            "UR": self._make_entry("UR", URAlgorithm, "UR", 0),
            "PMCGS_500": self._make_entry("PMCGS_500", PMCGSAlgorithm, "PMCGS", 500),
            "PMCGS_10000": self._make_entry("PMCGS_10000", PMCGSAlgorithm, "PMCGS", 10000),
            "UCT_500": self._make_entry("UCT_500", UCTAlgorithm, "UCT", 500),
            "UCT_10000": self._make_entry("UCT_10000", UCTAlgorithm, "UCT", 10000),
        }

    @staticmethod
    def _make_entry(name: str, cls, kind: str, simulations: int) -> Dict[str, object]:
        return {"name": name, "cls": cls, "kind": kind, "sims": simulations}

    @staticmethod
    def _select_move(algo, spec: Dict[str, object], player: str) -> int:
        """Dispatch select_move with the appropriate parameters."""
        kind = spec["kind"]
        sims = spec["sims"]

        if kind == "UR":
            return algo.select_move(player, "None", 0)
        elif kind in {"PMCGS", "UCT"}:
            return algo.select_move(player, "None", sims)
        else:
            raise ValueError(f"Unknown algorithm kind '{kind}'")

    def play_game(self, algo1_name: str, algo2_name: str) -> str:
        """Play a single game between two algorithms"""
        board = Board()
        current_player = 'R'
        spec1 = self.algorithms[algo1_name]
        spec2 = self.algorithms[algo2_name]
        algo1 = spec1["cls"](board)
        algo2 = spec2["cls"](board)

        while True:
            if current_player == 'R':
                move = self._select_move(algo1, spec1, current_player)
            else:
                move = self._select_move(algo2, spec2, current_player)

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

    def run_tournament(
        self,
        num_games: int = 100,
        parallel_workers: Optional[int] = None,
    ) -> Dict[str, Dict[str, Optional[float]]]:
        """Run tournament between all algorithm pairs"""
        algo_names = list(self.algorithms.keys())
        results: Dict[str, Dict[str, Optional[float]]] = {
            name: {opponent: None for opponent in algo_names} for name in algo_names
        }

        use_parallel = parallel_workers is not None and parallel_workers > 1

        for row in algo_names:
            for col in algo_names:
                if row == col:
                    results[row][col] = None
                    continue

                print(f"Running {row} vs {col}...", flush=True)

                if use_parallel:
                    win_percentage = self._run_pair_parallel(row, col, num_games, parallel_workers)
                else:
                    win_percentage = self._run_pair_sequential(row, col, num_games)

                results[row][col] = win_percentage

        return results

    def _run_pair_sequential(self, row: str, col: str, num_games: int) -> float:
        row_wins = 0
        draws = 0

        for game in range(num_games):
            if game % 2 == 0:
                winner = self.play_game(row, col)
                if winner == 'R':
                    row_wins += 1
                elif winner == 'Draw':
                    draws += 1
            else:
                winner = self.play_game(col, row)
                if winner == 'Y':
                    row_wins += 1
                elif winner == 'Draw':
                    draws += 1

        return ((row_wins + 0.5 * draws) / num_games) * 100 if num_games else 0

    def _run_pair_parallel(
        self,
        row: str,
        col: str,
        num_games: int,
        parallel_workers: Optional[int],
    ) -> float:
        if num_games == 0:
            return 0.0

        seeds = [random.randrange(1_000_000_000) for _ in range(num_games)]
        row_is_red_flags = [(i % 2 == 0) for i in range(num_games)]

        with ProcessPoolExecutor(max_workers=parallel_workers) as executor:
            futures = []
            for is_red, seed in zip(row_is_red_flags, seeds):
                if is_red:
                    red_spec = dict(self.algorithms[row])
                    yellow_spec = dict(self.algorithms[col])
                else:
                    red_spec = dict(self.algorithms[col])
                    yellow_spec = dict(self.algorithms[row])

                futures.append(executor.submit(_play_game_worker, red_spec, yellow_spec, seed))

            row_wins = 0
            draws = 0

            for is_red, future in zip(row_is_red_flags, futures):
                winner = future.result()
                if is_red:
                    if winner == 'R':
                        row_wins += 1
                    elif winner == 'Draw':
                        draws += 1
                else:
                    if winner == 'Y':
                        row_wins += 1
                    elif winner == 'Draw':
                        draws += 1

        return ((row_wins + 0.5 * draws) / num_games) * 100


def _play_game_worker(red_spec: Dict[str, object], yellow_spec: Dict[str, object], seed: Optional[int] = None) -> str:
    """Standalone game simulator for multiprocessing contexts."""
    if seed is not None:
        random.seed(seed)

    board = Board()
    algo_red = red_spec["cls"](board)
    algo_yellow = yellow_spec["cls"](board)
    current_player = 'R'

    while True:
        if current_player == 'R':
            move = Tournament._select_move(algo_red, red_spec, current_player)
        else:
            move = Tournament._select_move(algo_yellow, yellow_spec, current_player)

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

        current_player = _opponent(current_player)


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
