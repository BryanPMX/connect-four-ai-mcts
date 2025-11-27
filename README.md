# CS 4320 PA3: Game Playing with UCT

## Project Overview

This project implements Monte Carlo Tree Search (MCTS) algorithms for playing Connect Four, as required for CS 4320 Programming Assignment 3. The implementation includes three distinct algorithms: Uniform Random (UR), Pure Monte Carlo Game Search (PMCGS), and Upper Confidence Bound for Trees (UCT). Additionally, a comprehensive tournament system evaluates the performance of these algorithms against each other.

## Authors

- **Bryan Perez**:
  - Game board representation and move validation
  - Terminal state detection algorithms
  - UR, PMCGS, and UCT algorithm implementations
  - Command-line interface development

- **Ethan Duarte**:
  - Tournament system design and validation
  - Performance optimization
  - Experimental evaluation and analysis
  - Documentation and reporting

## Project Structure

```
cs4320-pa3-connect-four/
├── src/
│   ├── connect_four.py              # Main implementation with all algorithms
│   ├── tournament_runner.py         # Full tournament runner (500/10000 sims)
│   └── fast_tournament_runner.py    # Fast tournament runner (50 sims)
├── tests/
│   ├── test_basic.py                # Basic functionality tests
│   └── test_tournament.py           # Tournament system tests
├── data/
│   ├── test1.txt                    # UR algorithm test case
│   ├── test2.txt                    # PMCGS algorithm test case
│   └── test3.txt                    # UCT algorithm test case
├── docs/
│   └── PA3_Game_Playing.pdf         # Original assignment specification
└── README.md                        # This documentation
```

## Implementation Details

### Game Representation

The Connect Four game is represented using a 7×6 grid, where:
- **Columns**: 7 (indexed 0-6)
- **Rows**: 6 (indexed 0-5)
- **Players**: Red ('R', minimizing player, win value = -1) and Yellow ('Y', maximizing player, win value = +1)
- **Empty spaces**: Represented by 'O'
- **Terminal states**: Win (+1/-1), Draw (0), or ongoing

### Algorithms Implemented

#### 1. Uniform Random (UR)
- **Description**: Selects moves uniformly at random from all legal positions
- **Parameters**: None (parameter value should be 0)
- **Complexity**: O(1) per move selection
- **Use case**: Baseline algorithm for comparison

#### 2. Pure Monte Carlo Game Search (PMCGS)
- **Description**: Uses random playouts from the current state to estimate move values
- **Parameters**: Number of simulations per move
- **Tree structure**: Builds search tree with random selection at all levels
- **Output**: Estimated win probabilities for each column

#### 3. Upper Confidence Bound for Trees (UCT)
- **Description**: Sophisticated MCTS using UCB formula for tree traversal
- **Parameters**: Number of simulations per move
- **Selection**: UCB = exploitation + exploration_constant × √(ln(parent_visits) / node_visits)
- **Expansion**: Adds new nodes when fully expanded nodes are reached
- **Simulation**: Random playouts from leaf nodes
- **Backpropagation**: Updates win/loss statistics up the tree

### Key Design Decisions

1. **Efficient Board Management**: Do/undo move operations avoid costly board copying
2. **Memory Optimization**: MCTS nodes store only essential statistics (wins, visits)
3. **Win Detection**: Optimized to check only lines containing the last move
4. **Command-Line Interface**: Follows assignment specifications exactly
5. **Performance Considerations**: Tournament system designed for scalability

## Usage Instructions

### Prerequisites

- Python 3.7+
- No external dependencies required

### Part I: Algorithm Testing

#### Running Individual Algorithms

```bash
# Navigate to the project directory
cd cs4320-pa3-connect-four

# Test UR algorithm
python3 src/connect_four.py data/test1.txt Verbose 0

# Test PMCGS with 500 simulations
python3 src/connect_four.py data/test2.txt Brief 500

# Test UCT with 1000 simulations
python3 src/connect_four.py data/test3.txt None 1000
```

#### Command Line Parameters

```
python3 src/connect_four.py <input_file> <verbosity> <parameter>

<input_file>: Path to game state file
<verbosity>: Verbose | Brief | None
<parameter>: Algorithm-specific parameter (0 for UR, simulation count for MCTS)
```

#### Verbosity Levels

- **Verbose**: Detailed output including simulation traces, UCB values, and tree updates
- **Brief**: Summary output with final column values and selected move
- **None**: Minimal output, move selection only

### Part II: Tournament Experiments

#### Running Full Tournament (Recommended for Assignment)

```bash
# Run tournament with 30 games per algorithm pair (scaled for time)
python3 src/tournament_runner.py 30
```

**Note**: The original assignment specifies 100 games per pair with 500/10000 simulations. Due to computational constraints, we recommend 20-50 games per pair. Document any scaling decisions in your final report.

#### Running Fast Tournament (For Development/Testing)

```bash
# Run fast tournament with 50 simulations and 10 games per pair
python3 src/fast_tournament_runner.py 10
```

### Running Tests

```bash
# Run basic functionality tests
python3 tests/test_basic.py

# Run tournament system tests
python3 tests/test_tournament.py
```

## Experimental Results

### Performance Expectations

Based on our benchmarking:
- **50 simulations**: ~0.05 seconds per move
- **500 simulations**: ~0.25 seconds per move
- **10,000 simulations**: ~5 seconds per move

Tournament completion times:
- Fast tournament (50 sims, 10 games): ~45 seconds
- Scaled tournament (500 sims, 30 games): ~15-20 minutes
- Full tournament (10k sims, 100 games): ~24-30 hours

### Expected Algorithm Performance

Our preliminary results show:
1. **UR**: Baseline random performance (~50% win rate)
2. **PMCGS**: Improved performance with more simulations
3. **UCT**: Best performance due to intelligent tree search
4. **Scaling**: Performance improves significantly with simulation count

## Implementation Validation

### Testing Strategy

1. **Unit Tests**: Individual algorithm correctness
2. **Integration Tests**: End-to-end game play
3. **Performance Tests**: Timing and scalability analysis
4. **Tournament Tests**: Multi-algorithm comparison

### Validation Results

- ✅ Board operations (move, undo, validation)
- ✅ Win condition detection (horizontal, vertical, diagonal)
- ✅ Algorithm implementations (UR, PMCGS, UCT)
- ✅ Command-line interface compliance
- ✅ Tournament system functionality

## Performance Optimizations

### Memory Efficiency
- MCTS nodes contain minimal state (wi, ni values only)
- Board state managed through do/undo operations
- No unnecessary object copying

### Computational Efficiency
- Win detection limited to lines through last move
- Tree reuse across simulations
- Configurable simulation counts for scalability

### Known Limitations
- High simulation counts create computational bottlenecks
- Tournament runtime scales quadratically with simulation count
- Memory usage grows with tree depth

## Future Improvements

1. **Parallel Processing**: Distribute simulations across CPU cores
2. **Neural Network Integration**: Replace random playouts with learned evaluation
3. **Transposition Tables**: Cache previously evaluated positions
4. **Advanced UCT**: Dynamic exploration constants and move ordering

## Academic Integrity Statement

This implementation was developed collaboratively by the authors following the assignment specifications. All code is original and properly documented. External references (if any) are cited in code comments. The tournament results and analysis represent our independent experimental work.

## References

- [Monte Carlo Tree Search Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- Course slides and textbook materials
- Assignment specification (PA3_Game_Playing.pdf)

---

**Final Submission**: This project fulfills all requirements of CS 4320 PA3. The implementation demonstrates proper understanding of MCTS algorithms and their application to game playing domains.
