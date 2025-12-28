# Progressive Coding Interview Prep

Practice coding interview questions from OpenAI and Anthropic using their "staged-build" format.

## Overview

Both companies use a staged approach where you implement systems incrementally:
- **Anthropic**: 90-minute CodeSignal with 4 locked levels
- **OpenAI**: Multi-part problems with progressive follow-ups

**CRITICAL RULE**: When implementing Stage N, do NOT look at Stage N+1 requirements!

## Project Structure

```
interview-prep/
├── anthropic/
│   ├── 01-in-memory-database/    # Most commonly reported question
│   ├── 02-inventory-management/
│   ├── 03-chat-messages/
│   ├── 04-banking-application/
│   └── 05-file-system/
├── openai/
│   ├── 01-resumable-iterator/
│   ├── 02-versioned-kv-store/
│   ├── 03-in-memory-sql/
│   ├── 04-spreadsheet/
│   └── 05-cd-command/
└── README.md
```

Each question folder contains `stage1/`, `stage2/`, `stage3/`, `stage4/` with:
- `solution.py` - The implementation
- `test_solution.py` - pytest test suite

## How to Practice

### Starting a New Question

1. Read ONLY Stage 1 requirements
2. Implement `stage1/solution.py`
3. Write tests in `stage1/test_solution.py`
4. Run tests: `cd stage1 && python -m pytest test_solution.py -v`

### Moving to Next Stage

1. Copy solution to next stage: `cp stage1/solution.py stage2/`
2. Read Stage 2 requirements
3. Extend the solution
4. Add new tests

## Running Tests

```bash
# Run a single stage
cd interview-prep/anthropic/01-in-memory-database/stage1
python -m pytest test_solution.py -v

# Run all tests for a question
python -m pytest interview-prep/anthropic/01-in-memory-database/*/test_solution.py -v
```

## Anthropic Questions Summary

| Question | Stages | Key Concepts |
|----------|--------|--------------|
| In-Memory Database | 4 | SET/GET, Scanning, TTL, Backup/Quotas |
| Inventory Management | 4 | CRUD, Prefix Search, Multi-user, Duplicates |
| Chat Messages | 4 | Messages, Listing, TTL, Backup/Restore |
| Banking Application | 4 | Accounts, Transactions, Transfers, Fees/Limits |
| File System | 4 | Files, Directories, Permissions, Quotas |

## OpenAI Questions Summary

| Question | Stages | Key Concepts |
|----------|--------|--------------|
| Resumable Iterator | 4 | State save/restore, JSON files, Async, N-D arrays |
| Versioned KV Store | 4 | Versioning, Thread-safety, Timestamps, Persistence |
| In-Memory SQL | 4 | CREATE/INSERT/SELECT, WHERE, Complex queries, ORDER BY |
| Spreadsheet | 3 | Formulas, O(1) get_cell, Cycle detection |
| CD Command | 3 | Path resolution, Home dir (~), Symlinks |

## Tips

1. **Time yourself**: Anthropic gives 90 min for 4 stages (~22 min each)
2. **Don't peek ahead**: Resist looking at future stages
3. **Write tests first**: TDD helps clarify requirements
4. **Commit after each stage**: Track code evolution
5. **Focus on correctness**: Speed comes with practice

## Design Rationale Included

Each solution includes design rationale explaining:
- Data structure choices
- Trade-offs made
- Why the approach was chosen

This helps understand the thought process for real interviews.

## Requirements

- Python 3.10+
- pytest: `pip install pytest`
