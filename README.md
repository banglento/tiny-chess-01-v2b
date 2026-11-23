# tiny-chess-01 entry "v2b"

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/banglento/tiny-chess-01-v2b/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/banglento/tiny-chess-01-v2b/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A chess engine in 4,055 bytes of Python (limit 4,096), packed as an
lzma payload in `main.py` in the same format as the previous entry
("chess3"). Deterministic: fixed 72,000-node budget per move, no clock
is ever read. Same protocol and budget as chess3 — only the search and
evaluation changed.

What changed against chess3 (all in `main_src.py`):

- Check extension: a node where the side to move is in check is
  searched one ply deeper.
- Late Move Reduction: quiet moves at move-list position >= 4 and
  depth >= 3 are probed at depth-2 with a null window and re-searched
  at full depth only if they raise alpha.
- Qsearch delta pruning: captures that cannot reach alpha even with a
  200 cp margin are skipped (promotions exempt).
- Tapered king piece-square tables: middlegame and endgame tables
  interpolated by game phase instead of an abrupt switch.
- Rook open-file bonus: +15 on a file with no pawns at all, +8 on a
  file with no enemy pawns.

Measured strength (local, 2026-11-23):

- Official practice trial (fresh kit, trial-0, run on the packed
  `main.py` itself): **Elo 1,654** (5W/0D/1L).
- Same-instance control, the live chess3 packed entry under identical
  conditions: **Elo 1,451** (3W/2D/1L). The paired difference is +203.
- Head-to-head against chess3 at equal 36,000-node budgets, practice
  book openings, colours swapped: W6 D7 L3, score 0.594, about +66 Elo
  over 16 games.

`main.py` decompresses byte-for-byte to `main_src.py`. Reproduce the
pack with `python3 pack.py` (it verifies the written file by reading
it back independently). The readable development source is
`main_src.py`.
