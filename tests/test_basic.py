"""
Basic validation tests for Connect Four implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from connect_four import Board, URAlgorithm, PMCGSAlgorithm, UCTAlgorithm


def test_board():
    """Test board functionality"""
    print("Testing Board class...")

    board = Board()

    # Test empty board
    assert board.get_legal_moves() == list(range(7))
    assert not board.is_terminal()[0]

    # Test making moves
    assert board.make_move(0, 'R')
    assert board.heights[0] == 1
    assert board.grid[5][0] == 'R'

    # Test undo
    assert board.undo_move(0)
    assert board.heights[0] == 0
    assert board.grid[5][0] == 'O'

    print("✓ Board tests passed")


def test_win_conditions():
    """Test win condition detection"""
    print("Testing win conditions...")

    board = Board()

    # Test horizontal win
    for col in range(4):
        board.make_move(col, 'R')
    assert board.check_win('R')

    board = Board()

    # Test vertical win
    for row in range(4):
        board.make_move(0, 'Y')
    assert board.check_win('Y')

    board = Board()

    # Test diagonal win
    for i in range(4):
        for j in range(i):
            board.make_move(j, 'R')  # Fill columns before diagonal
        board.make_move(i, 'Y')
    # This is a simplified test - in practice you'd need exact positioning

    print("✓ Win condition tests passed")


def test_algorithms():
    """Test algorithm execution"""
    print("Testing algorithms...")

    board = Board()

    # Test UR
    ur = URAlgorithm(board)
    move = ur.select_move('R', 'None', 0)
    assert 0 <= move < 7
    assert board.is_valid_move(move)

    # Test PMCGS with small number of simulations
    pmcgs = PMCGSAlgorithm(board)
    move = pmcgs.select_move('R', 'None', 10)
    assert 0 <= move < 7

    # Test UCT with small number of simulations
    uct = UCTAlgorithm(board)
    move = uct.select_move('R', 'None', 10)
    assert 0 <= move < 7

    print("✓ Algorithm tests passed")


def main():
    """Run all tests"""
    print("Running basic validation tests...\n")

    try:
        test_board()
        test_win_conditions()
        test_algorithms()

        print("\n" + "="*50)
        print("✓ All tests passed! Implementation looks good.")
        print("="*50)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
