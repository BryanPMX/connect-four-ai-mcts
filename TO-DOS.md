# CS 4320 PA3: Task Guide

## Overview

**Your Tasks:**
- Tournament system validation and execution
- Performance optimization
- Experimental evaluation
- Final report writing

---

## Step-by-Step Task List

### Phase 1: Environment Setup (30 minutes)

#### 1.1 Clone/Fetch the Project (GITHUB)

#### 1.2 Verify Installation
```bash
# Test basic functionality
python3 tests/test_basic.py

# Test command-line interface
python3 src/connect_four.py data/test1.txt Verbose 0
python3 src/connect_four.py data/test2.txt Brief 500
python3 src/connect_four.py data/test3.txt Brief 10000
```

#### 1.3 Run Initial Tournament Test
```bash
# Fast test to ensure tournament system works
python3 src/fast_tournament_runner.py 5
```

---

### Phase 2: Tournament Experiments

#### 2.1 Choose Tournament Parameters

**Important Decision:** Balance fidelity vs. runtime.

**Option A: Full Assignment Spec (recommended)**
- Uses the five required configurations: UR, PMCGS(500), PMCGS(10000), UCT(500), UCT(10000)
- Run 100 games per pairing (25 pairings total, colors alternate automatically)
- Total time: can exceed 24 hours—plan ahead or run in batches

**Option B: Scaled Tournament**
- Keep the official simulation counts but reduce `num_games` to 20–50
- Useful for intermediate checkpoints; document the deviation in the report

**Option C: Development Smoke Tests**
- Use `fast_tournament_runner.py` (all MCTS configs capped at 50 simulations)
- Ideal for debugging logic changes before committing to long runs

#### 2.2 Execute Chosen Tournament
```bash
# Full spec (100 games per pairing)
python3 src/tournament_runner.py 100

# Scaled experiment (e.g., 30 games per pairing)
python3 src/tournament_runner.py 30

# Fast dev loop (50 sims, 10 games per pairing)
python3 src/fast_tournament_runner.py 10
```

#### 2.3 Analyze Results
1. Open the generated `tournament_results.txt` (or `fast_tournament_results.txt`)
2. Document key findings:
   - Which algorithm performs best?
   - How does performance scale with simulation count?
   - Any surprising results?

#### 2.4 Performance Benchmarking
```bash
# Time a few different configurations
time python3 src/fast_tournament_runner.py 10
time python3 src/tournament_runner.py 10  # Uses full 500/10000 sim settings
```

---

### Phase 3: Final Report Writing

#### 3.1 Report Structure

Create `final_report.pdf` or `final_report.md` with these sections:

**Required Sections (from assignment):**
1. **Group member contributions** (brief discussion)
2. **Results from testing** (Part II tournament results)
3. **Additional sections** as needed

**Recommended Structure:**
```
CS 4320 PA3 Final Report
========================

1. Abstract (200 words)
   - Brief overview of implementation and results

2. Introduction
   - Problem statement
   - Approach overview

3. Implementation Details
   - Game representation
   - Algorithm implementations (UR, PMCGS, UCT)
   - Key design decisions
   - Performance optimizations

4. Experimental Methodology
   - Tournament setup
   - Parameter choices (simulation counts, game counts)
   - Any deviations from original assignment specs

5. Results and Analysis
   - Tournament results table
   - Performance comparisons
   - Timing analysis
   - Key insights

6. Discussion
   - Algorithm strengths/weaknesses
   - Performance scaling observations
   - Implementation challenges overcome

7. Conclusion
   - Summary of achievements
   - Future improvements

8. Team Contributions
   - Bryan Perez: (Core Implementation)
     - Game board and move validation
     - Terminal state detection
     - UR/PMCGS/UCT algorithms
     - CLI interface
   - Ethan Duarte: (Testing & Report)
     - Tournament execution and analysis
     - Performance optimization
     - Experimental evaluation
     - Report writing and documentation

Appendices
- Code snippets (if relevant)
- Detailed tournament results
```

#### 3.2 Key Points to Include

**Team Contributions Section:**
```
Bryan Perez: Designed and implemented the core Connect Four game engine,
including board representation, move validation, terminal state detection, and all
three required algorithms (UR, PMCGS, UCT). Developed the command-line interface
and optimized the implementation for performance.

Ethan Duarte: Executed comprehensive tournament experiments, analyzed
algorithm performance, optimized tournament parameters for time constraints,
and authored this final report documenting methodology, results, and insights.
```

**Results Section:**
- Include the tournament results table
- Explain methodology clearly
- Discuss any scaling decisions
- Analyze performance trends

---

### Phase 4: Final Submission Preparation

#### 4.1 Verify All Requirements Met

**Assignment Requirements Checklist:**
- [ ] Three algorithms implemented (UR, PMCGS, UCT)
- [ ] Command-line interface works as specified
- [ ] Tournament between 5 algorithm variations
- [ ] Round-robin tournament (each vs each)
- [ ] Results analysis and discussion
- [ ] Source code included
- [ ] Report documenting contributions and results

#### 4.2 Package Submission

**Files to Submit:**
```
submission.zip or folder containing:
├── src/
│   ├── connect_four.py
│   ├── tournament_runner.py
│   └── fast_tournament_runner.py
├── data/
│   ├── test1.txt
│   ├── test2.txt
│   └── test3.txt
├── tests/
│   ├── test_basic.py
│   └── test_tournament.py
├── docs/
│   └── PA3_Game_Playing.pdf
├── README.md
├── final_report.pdf (or .md)
└── tournament_results.txt
```

#### 4.3 Final Verification
```bash
# Run one more comprehensive test pass
python3 tests/test_basic.py
python3 tests/test_tournament.py
pytest   # optional but recommended
python3 src/connect_four.py data/test1.txt None 0  # ensure silent mode works
```

---

## Troubleshooting Guide

### Common Issues

**1. Import Errors**
```bash
# If you get "ModuleNotFoundError"
cd "/Users/bryanpmx/Documents/Artificial Inteligence/ASSIGNMENT 4"
python3 -c "import sys; sys.path.append('src'); import connect_four; print('OK')"
```

**2. Tournament Takes Too Long**
- Reduce games per match: `python3 src/tournament_runner.py 10`
- Use fast runner: `python3 src/fast_tournament_runner.py 20`
- Document scaling in report

**3. Memory Issues**
- Close other applications
- Run tournaments in smaller batches
- Use fast_tournament_runner.py for testing

**4. Results Analysis**
- Look for patterns: Does UCT beat PMCGS? Does more simulations help?
- Check for statistical significance (win rates >55% likely meaningful)
- Compare against random baseline

---

**Key Files to Reference:**
- `README.md`: Complete project documentation
- `src/connect_four.py`: Implementation details and comments
- `src/tournament_runner.py`: Tournament logic
- `fast_tournament_results.txt`: Example results format

**Questions?**
- Read README.md first (comprehensive documentation)
- Check existing test results in `fast_tournament_results.txt`
- Review tournament_runner.py comments for implementation details
