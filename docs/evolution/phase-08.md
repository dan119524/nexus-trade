# Phase 08 Evolution Record: Factory and Builder

## Starting State

- Phase 07 was merged into `main` through pull request #20 (merge commit `4ed5e63`) and tagged `phase-07-completed`. The README roadmap was then marked ✅ for Phase 07 through pull request #21 (merge commit `b81ad33`).
- The `workshop-08` branch was created from `main` at `b81ad33`, one merge after `phase-07-completed`. The working tree was clean, and `pytest` gave 983 passed and 0 failed.
- The guide `phases/phase-08-factory-and-builder.md` was adapted from CSC 413 Workshop 08 (`9a14896`). The copied workshop files in `workshops/` are kept out of Git through `.gitignore` (`75f9723`).
- The start check reported PHASE-07 COMPLETION: VERIFIED and PHASE-08 START CHECK: PASS. `AGENTS.md` was byte-identical to `origin/main`.

## Section 2: V1 Builder

### AI Use

The workshop marks Section 2 as student owned, with no AI. Claude Code first declined to implement it. Daniel clarified that Nexus is a personal project that is not submitted or graded, and that his CSC 413 semester application is Tirgum (`csc413-fall26-05-dan119524`). The guide's Section 2 was changed to say AI is allowed for Nexus and that the no-AI rule applies to Tirgum (`f44a651`).

### Decisions

Daniel decided:

| Question | Decision |
|---|---|
| Problem | `build_trade_plan` builds a trade plan in one long function, mixing file reads, the OANDA call, SL/TP, lot size, and dict building (Phase 07 review row 1). |
| Pattern | Builder: one complex object assembled step by step. There is only one `TradePlan` type, so not Factory. |
| Responsibility | `TradePlanBuilder` only assembles and validates. The caller passes in all values. It never reads files or calls OANDA. |
| Shape | Next to `TradePlan`, one method per part, and `build()` returns the existing `TradePlan` or raises `ValueError` if a required part is missing. Reuse `TradePlan`'s validation, no new rules. `build_trade_plan` not changed yet. |

### Implementation

Commit `f671d07` ("Phase 08 V1: add TradePlanBuilder"), tagged `phase-08-v1`.

- `tools/models/trade_plan_builder.py`: `TradePlanBuilder` with `signal`, `account`, `entry`, `stop_loss`, `take_profit_1`, `take_profit_2`, and `lot_size`, each returning the builder, and `build()`. A part is missing only if its method was never called; a value passed explicitly, even `None`, goes to `TradePlan`, which rejects it with its own error.
- `tools/models/__init__.py` exports `TradePlanBuilder`.
- `tools/models/demo.py`: a Builder section builds one plan and shows an incomplete builder being rejected.
- `tests/models/test_trade_plan_builder.py`: 11 tests. A valid plan has the given parts and the same derived values as a directly constructed plan; each of the 7 missing parts is rejected and named; an empty builder names all 7; `TradePlan`'s reward-to-risk rejection still applies through the builder.

`pytest` gave 994 passed and 0 failed. The tag was created before the V1 check, at Daniel's request. The V1 check was then run read-only and reported PHASE-08 V1: READY.

## Section 4: Object Creation Collaboration

### Switching `build_trade_plan` to the Builder

Daniel asked to switch `build_trade_plan` to `TradePlanBuilder` with exactly the same output and unchanged tests. Claude Code reported that this was not possible within Phase 08:

- `TradePlanBuilder` needs a domain `Signal` and `Account`, and `build_trade_plan` has only pipeline dicts. `detect_trend` returns `bullish`/`bearish`/`ranging`, while `TimeframeAnalysis` accepts only `uptrend`/`downtrend`/`ranging`. Building a `Signal` needs `TimeframeAnalysis`, `StructureEvent`, `SwingPoint`, and `CurrencyPair` objects. That translation is Adapter work, which is Phase 09.
- `Signal` computes direction, score, validity, and reference timeframe from the voting table, while `build_trade_plan` trusts `score_confluence`. The tie conflict is already recorded in `requirements.md`.
- `TradePlan` rejects cross pairs, while `calculate_lot_size` sized them (see below).
- The existing tests' fake account is `{"balance": 10000.0}`, which is not enough to build an `Account`.

Daniel decided to defer the switch to Phase 09 (option A). `docs/design/phase-07-review.md` rows 1 and 2 now record this.

### Factory

Claude Code reviewed where buy or sell is decided. In the domain, `Signal.trade_direction()` is the only place that chooses `BuyDirection` or `SellDirection`. In the pipeline tools, four places decide it from strings: `calculate_sl_tp.py` (SL and TP side), `execute_trade.py` (units sign), `simulate_signals.py` (backtest outcome), and `build_trade_plan.py` (invalidation note). A `trade_direction_for(direction)` factory was sketched but not written.

Daniel decided that a Factory is **not required for Phase 08**: the domain has one creation site whose callers already don't choose concrete types, so a factory would move one line, and the four tool branches need the tools to use `TradeDirection` objects first. The four branches are noted for Phase 09/10. The README roadmap's `OrderFactory` was not added, because `Order` has only one type.

### Direct Construction

All other classes keep direct construction: each has a short constructor with no optional parts.

### Synchronization

- `docs/design/requirements.md`: a `TradePlanBuilder` CRC card and an "Object Creation" section. No FR changed.
- `docs/design/uml/crc.puml` and `docs/design/uml/domain-model.puml`: the `TradePlanBuilder` card and class, and `TradePlanBuilder ..> TradePlan : builds >`. PlantUML was not available to render them here.

## Related Fix: Cross Pairs Rejected (FR9)

| Item | Detail |
|---|---|
| Where | `tools/trade_plan/calculate_lot_size.py` |
| Bug | Found during the Section 4 review. FR9 rejects cross pairs until a real conversion exists, but `pip_value_per_lot` returned an approximate $10 per lot for a cross pair and only logged a warning, so `build_trade_plan` wrote a plan for it. |
| Fix | Made on branch `fix/reject-cross-pairs` from `main`, at Daniel's request, as pull request #22 (not merged when this record was written). `pip_value_per_lot` raises `ValueError` for a cross pair, `calculate_lot_size` returns `None` (no trade), and `build_trade_plan`'s rejection message covers both no-lot cases. |
| Tests | 9 new tests: `pip_value_per_lot` raises and `calculate_lot_size` returns `None` for EUR_GBP, GBP_JPY, EUR_JPY, and AUD_NZD, and `build_trade_plan("EUR_GBP")` writes no plan. All 9 fail against the old code. `pytest` on the branch gave 992 passed. |
| Records | A resolution note under Known Conflicts in `requirements.md`, on that branch. |

## Final Review

The final review reported PHASE-08: PASSED, with two advisory recommendations:

1. `TradePlanBuilder` keeps its parts after `build()`, so reusing one builder for a second plan carries over the earlier parts.
2. Pull request #22 and `workshop-08` both edit `docs/design/requirements.md`, in different sections.

## Tests

`pytest` gave 994 passed and 0 failed in a normal run, with network blocked and `.tmp/` pointed at an empty directory, and with network blocked and the real `.tmp/` under access tracking. No test attempted a network connection or read the real `.tmp/`. `python -m tools.models.demo` exits 0.

## Notes for Later Phases

| Phase | Note |
|---|---|
| 09 | Switch `build_trade_plan` to `TradePlanBuilder`, which needs the pipeline dicts turned into domain objects (Adapter). `calculate_sl_tp` can then use `TradeSetup` and `TradeDirection`. |
| 09/10 | The four tool branches on `bullish`/`bearish` (`calculate_sl_tp`, `execute_trade`, `simulate_signals`, `build_trade_plan`) could use `TradeDirection`, with a direction factory if there is then more than one creation site. |
| Open | Whether TP1 should come from market structure (from Phase 07). |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code adapted the workshop guide, ran the start check, the V1 check, and the final review, implemented `TradePlanBuilder` and the cross-pair fix from Daniel's decisions, reported why the `build_trade_plan` switch could not be done as asked, reviewed the factory option, synchronized the design documents, and wrote this record.
- Claude Code committed the work, created `phase-08-v1`, and opened the pull requests at Daniel's request.

## End State

- `phase-08-v1` points to `f671d07`, the V1 Builder. It is pushed to `origin`.
- The Section 4 documentation, the README update (Phase 08 ✅), and this record are in the commit "Complete Phase 08 factory and builder", made after `phase-08-v1`. This record was written before the merge. A pull request from `workshop-08` into `main` was opened and not yet merged.
- Since `phase-07-completed`, no pipeline tool outside `tools/models/` changed on `workshop-08`.

## Verification Confirmation

To be completed by Daniel.
