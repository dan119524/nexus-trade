# Phase 03 Evolution Record: Connecting Objects

## Starting State

- Phase 02 was merged into `main` through pull request #4 (merge commit `34c5a84`) and tagged `phase-02-completed`.
- Two fixes were merged into `main` after that tag and before Phase 03 started:
  - Pull request #5 (`d519890`, merge `39f4978`): `tools/oanda/fetch_candles.py`, `fetch_account.py`, `fetch_instruments.py`, and `execute_trade.py` choose the OANDA environment with `"live" if env == "live" else "practice"`.
  - Pull request #6 (`33c38e8`, merge `7621b96`): the same change in `tools/api/server.py` and `tools/scheduler/weekly_cycle.py`.
- The `phase-03` branch was created from `7621b96`.
- The baseline was the Phase 02 code in `tools/models/`. `TradeSetup` and `BacktestResult` referred to their currency pair only by a `pair_name` string, and no class held another class's object. Phase 02 had deferred three items to later phases: D1 (object references and the same-pair rule), finding 4 (which trade setups were tested), and D5 (the reward-to-risk minimum of 2).

## Start Check

The Phase 03 start check reported BLOCKED on two conditions:

- `phase-03` starts at `7621b96`, not at the `phase-02-completed` commit `34c5a84`.
- `pytest` gave 178 passed and 2 failed. The 2 failures are the known failures recorded in `docs/evolution/phase-02.md`.

Daniel accepted `7621b96` as the start and kept the Phase 02 rule of "no new test failures".

## Design Decisions

Daniel made these decisions before any Phase 03 code was written:

| Topic | Decision |
|---|---|
| R1: `TradeSetup` → `CurrencyPair` | One-way object reference (`self._pair`). Classified as association. |
| R2: `BacktestResult` → `CurrencyPair` | One-way object reference (`self._pair`). Classified as association. |
| R3: `BacktestResult` → `TradeSetup` | Classified as aggregation, deferred to Phase 06. `setups_tested` stays a count. |
| Wording in `requirements.md` | The relationship word "has" is kept. |
| D1 (Phase 02) | Object references in Phase 03. The same-pair check is deferred to Phase 06 together with R3. |
| Finding 4 (Phase 02) | Deferred to Phase 06. |
| D5 (Phase 02) | Stays deferred. |
| Constructors | `TradeSetup` and `BacktestResult` take a `CurrencyPair` object. A wrong-type pair raises `ValueError`. |
| Properties | `pair_name` is kept and returns `self._pair.name`. A read-only `pair` property is added. |
| Tests | `tests/models/` is updated for the new constructors. |

## Initial Implementation

The initial implementation is commit `643d042` ("Complete Phase 03 initial implementation"), tagged `phase-03-v1`.

- `requirements.md`: the Relationships and Multiplicities table has a Classification column (Association, Association, Aggregation). Two bullets were added: the CurrencyPair associations are one-way, and the BacktestResult–TradeSetup aggregation and the same-pair rule are implemented in Phase 06.
- `trade_setup.py` and `backtest_result.py`: the first constructor argument is `pair`. Each constructor checks `isinstance(pair, CurrencyPair)`, raises `ValueError` otherwise, and stores `self._pair`. Each class has a read-only `pair` property, and `pair_name` returns `self._pair.name`. Neither file imports `validate_pair_name` any more.
- `demo.py`: one `eur_usd` object is shared by the buy setup and the EUR_USD backtest, and one `gbp_usd` object by the sell setup and the no-trades backtest. A "Connected objects" section shows the shared pair and both objects using it. A pair-name string passed as the pair is shown being rejected.
- `tests/models/test_trade_setup.py` and `test_backtest_result.py`: constructors use `CurrencyPair` objects. In each file the 4 invalid-name tests became 4 wrong-type tests (a string, `None`, `1`, and a tuple), and tests were added for `pair is` the object passed in, `pair_name` matching it, `pair` being read-only, and a pair being used or shared.
- `domain-model.puml`: the SharedHelpers note says `validate_pair_name` is used by `CurrencyPair` only.
- No lists, dicts, or sets are used for relationships. No inheritance, interfaces, or patterns were added. No code outside `tools/models/` calls the changed constructors.

### Phase Guide Changes

Also in `643d042`, at Daniel's request:

- `phases/phase-03-connecting-objects.md`: the "Before You Start" list, the start check, the v1 check, and the Section 4 PASSED condition say "`pytest` shows no new test failures". The v1 check accepts a relationship "recorded in requirements.md as deferred to a later phase" and allows changes in `tests/models/`.
- `phases/phase-04-inheritance.md`, `phase-05-polymorphism-interfaces.md`, and `phase-06-growing-the-object-model.md`: every "`pytest` passes", "all tests pass", and "all of `pytest` passes" became "`pytest` shows no new test failures". The Phase 04 Section 2 path list includes `tests/models/`.

The first v1 check reported BLOCKED, because R3 is classified but not implemented and `tests/models/` was outside the allowed paths. After the guide changes, it reported PHASE-03 V1: READY.

## Engineering Review

Claude Code ran the Phase 03 engineering review against `phase-03-v1` without modifying files. All requested checks passed for the code: the classifications fit the lifetimes, both references are validated before any other check, and nothing beyond Phase 03 scope was added. It reported 13 numbered findings: 8 real problems and 5 optional ideas. Daniel decided every finding.

**Real problems**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 1 | `domain-model.puml` class boxes still showed `_pair_name : str` and the old constructors, without the `pair` property. | ACCEPT | Synced with the code (see Diagram Sync). |
| 2 | The AssociationLinks note said the links were `pair_name` strings and put the same-pair check in Phase 03, against `requirements.md`. | ACCEPT | Note rewritten. |
| 3 | R1 and R2 were drawn without direction, though they are one-way. | ACCEPT | Drawn as arrows toward `CurrencyPair`. |
| 4 | R3 was drawn as a plain association, though classified as aggregation. | ACCEPT | Drawn as aggregation with the note "planned, not yet implemented (Phase 06)". |
| 5 | Moving finding 4, R3, and the same-pair check from Phase 03 to Phase 06 was recorded only in `requirements.md`. | ACCEPT | Recorded in this file (Design Decisions and Deferred Items). |
| 6 | Guide Section 2 allowed changes only in `tools/models/`, which was stricter than its own v1 check. | ACCEPT | It allows `tools/models/`, `tests/models/`, `docs/`, and `phases/`. |
| 7 | Guide Section 2 said to connect a single object for a one-to-many relationship, against the R3 decision. | ACCEPT | It says "connect a single object, or record the relationship as deferred in requirements.md". |
| 8 | The guides changed the README after the merge, which would need a commit on `main` (`AGENTS.md` section 11). | ACCEPT | The README step comes first in the Merge and Tag section of the Phase 03–06 guides (the only guides from 03 to 12 that exist) and in Step 12 of `docs/phase-workflow.md`. |

**Optional ideas**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 9 | Two `CurrencyPair` objects with the same name are different objects, so the same-pair rule must choose between identity and name. | ACCEPT | Recorded as an open question for Phase 06 (below). |
| 10 | The wrong-type pair check was duplicated in `trade_setup.py` and `backtest_result.py`. | ACCEPT | A public `validate_pair(pair)` in `currency_pair.py`, used by both. |
| 11 | The test pairs were defined in both test files. | ACCEPT | `tests/models/conftest.py` provides `eur_usd`, `gbp_usd`, and `usd_jpy` fixtures. |
| 12 | `crc.puml` lists `TradeSetup` as a collaborator of `BacktestResult`, though no reference exists yet. | ACCEPT | Shown as `TradeSetup (Phase 06)`. |
| 13 | `requirements.md` line 73 is an implementation schedule inside the requirements. | REJECT | None. The v1 check relies on deferrals being recorded in `requirements.md`. |

## Diagram Sync

- **`domain-model.puml`:**
  - The header names `tools/models/` (Phase 03) as the source of attributes, methods, and object references.
  - `TradeSetup` and `BacktestResult` show `- _pair : CurrencyPair`, `+ __init__(pair : CurrencyPair, …)`, `+ pair : CurrencyPair`, and `+ pair_name : str`.
  - R1 and R2 are arrows from `TradeSetup` and `BacktestResult` to `CurrencyPair`, with the same multiplicities and "has" labels.
  - R3 is an aggregation with the note "planned, not yet implemented (Phase 06)".
  - The AssociationLinks note says the two CurrencyPair associations are one-way object references, and that the same-pair check is planned, not yet implemented (Phase 06).
  - The SharedHelpers note lists `validate_pair(pair)`, used by `TradeSetup` and `BacktestResult`. The ValidationRules note says the pair must be a `CurrencyPair`.
- **`crc.puml`:** the `BacktestResult` collaborator is `TradeSetup (Phase 06)`. The `BacktestResult` CRC table in `requirements.md` shows the same `TradeSetup (Phase 06)` collaborator.
- **`use-cases.puml`:** unchanged, because no actor goal changed.
- Claude Code could not run PlantUML's syntax check, because PlantUML is not installed in its environment.

## Tests

| File | Tests at `phase-02-completed` | Tests now | Change |
|---|---|---|---|
| `conftest.py` | — | — | New. `eur_usd`, `gbp_usd`, and `usd_jpy` fixtures with fixed prices. |
| `test_currency_pair.py` | 37 | 37 | Unchanged. |
| `test_trade_setup.py` | 32 | 35 | `CurrencyPair` objects from the fixtures; 4 wrong-type tests replace 4 invalid-name tests; new tests for `pair is` the object passed in, `pair` read-only, and a setup using its pair. |
| `test_backtest_result.py` | 22 | 25 | Same changes, with a test that a result and a setup can share one pair. |

The tests use only fixed data and do not call the OANDA API.

Results: `tests/models/` gives 97 passed. The full suite gives 184 passed and 2 failed, and the 2 failures are the known failures recorded in `docs/evolution/phase-02.md`.

## Deferred Items and Open Questions

| Item | Status |
|---|---|
| R3: `BacktestResult` → `TradeSetup` (aggregation) | Deferred to Phase 06. `setups_tested` is a count. |
| Same-pair rule | Deferred to Phase 06 with R3. |
| Phase 02 finding 4: which trade setups were tested | Deferred to Phase 06. |
| Phase 02 D5: reward-to-risk minimum of 2 | Still deferred. |
| **Open question for Phase 06:** same object vs same name | Two `CurrencyPair("EUR_USD", …)` objects with different price data are different objects but have the same `pair_name`. When the same-pair rule is implemented, decide whether it compares objects (`is`) or names. |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code ran the start check, explained the Section 2 decisions as suggestions, and implemented only Daniel's decisions.
- Claude Code ran the v1 check, and after Daniel's guide changes committed `643d042` and created `phase-03-v1`.
- Claude Code ran the engineering review without modifying files, applied only the findings Daniel accepted, synced the diagrams, and wrote this record.

## End State

- `phase-03-v1` points to commit `643d042`, the implementation before review. It is pushed to `origin/phase-03`.
- The review changes, the diagram sync, `tests/models/conftest.py`, this record, the corrected Phase 02 test counts, and the README roadmap update are in the commit "Complete Phase 03 connecting objects", made after `phase-03-v1`.
- `tools/` files outside `tools/models/` changed since `phase-02-completed` only in pull requests #5 and #6, both merged into `main` before Phase 03 started.

## Verification Confirmation
I personally inspected domain-model.puml and crc.puml in IntelliJ and confirmed they match my approved Phase 03 decisions.
