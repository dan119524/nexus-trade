# Phase 04 Evolution Record: Inheritance

## Starting State

- Phase 03 was merged into `main` through pull request #7 (merge commit `b245189`) and tagged `phase-03-completed`.
- The `phase-04` branch was created from `b245189`. The Phase 04 start check reported PASS: the branch starts at the `phase-03-completed` commit, the tree was clean, and `pytest` gave 184 passed and 2 failed, the 2 known failures recorded in `docs/evolution/phase-02.md`.
- The baseline was the Phase 03 code. `TradeSetup` took a `direction` string (`"buy"` or `"sell"`) and used `if direction == …` branches for FR2's price order. `reward_to_risk()` used absolute differences. No class inherited from another.

## Design Decisions

Claude Code suggested three candidate hierarchies: `TradeSetup` → `BuySetup`/`SellSetup` (FR2), `TradeSetup` → `SuggestedSetup`/`TestedSetup` (FR2 and FR3), and `MarketStructure` → `Uptrend`/`Downtrend`/`Ranging` (FR1). Daniel decided:

| # | Decision |
|---|---|
| 1 | `TradeSetup` is the superclass, with subclasses `BuySetup` and `SellSetup` (FR2: direction buy or sell, with opposite price orders). |
| 2 | A bare `TradeSetup` cannot be created. Its price-order check raises `NotImplementedError`, so only subclasses can be built. Phase 05 makes `TradeSetup` abstract. |
| 3 | The subclasses are named `BuySetup` and `SellSetup`. |
| 4 | The subclasses override the price-order check, `risk()`, and `reward()`. `reward_to_risk()` stays in `TradeSetup` and uses `risk()` and `reward()`. |
| 5 | `direction` stays as a read-only property returning `"buy"` or `"sell"`, and is removed from the constructor. |
| 6 | `BuySetup` and `SellSetup` are added to the Domain Entities table and the CRC cards in `requirements.md`. The superclass is not listed as a collaborator. |
| 7 | `tests/models/` is updated for the new constructors. |
| — | Each subclass calls `super().__init__` for the shared state. |

## Initial Implementation

The initial implementation is commit `573ed95` ("Complete Phase 04 initial implementation"), tagged `phase-04-v1`.

- `trade_setup.py`: `TradeSetup.__init__(pair, entry, stop_loss, take_profit)` validates the pair and the prices, stores `_pair`, `_entry`, `_stop_loss`, and `_take_profit`, and then calls `self._check_price_order()`. In `TradeSetup`, `_check_price_order()`, `direction`, `reward()`, and `risk()` raise `NotImplementedError`. `reward_to_risk()` returns `self.reward() / self.risk()`. The `_direction` attribute and the `if direction == …` branches were removed.
- `buy_setup.py` (new): `BuySetup(TradeSetup)`. Its `__init__` calls `super().__init__(…)`. It overrides `_check_price_order()` (stop loss < entry < take profit), `direction` (`"buy"`), `reward()` (take profit − entry), and `risk()` (entry − stop loss).
- `sell_setup.py` (new): `SellSetup(TradeSetup)`, with the same structure and the sell rules: take profit < entry < stop loss, `"sell"`, entry − take profit, and stop loss − entry.
- `__init__.py`: exports `BuySetup` and `SellSetup`. Its docstring changed from "Phase 02 domain classes for NEXUS Trade." to "Domain classes for NEXUS Trade."
- `demo.py`: builds both subclasses and, for each, prints the is-a check, the inherited members (`pair_name`, prices, `reward_to_risk()`), and the overridden members (`direction`, `reward()`, `risk()`). It shows an invalid buy, an invalid sell, a pair-name string, and a bare `TradeSetup` being rejected.
- `tests/models/test_trade_setup.py`: 10 constructor calls became `BuySetup(…)` and 4 became `SellSetup(…)`. The 4 wrong-direction tests were removed, because direction is no longer an input. Tests were added for a bare `TradeSetup` raising `NotImplementedError`, both subclasses being `TradeSetup`s, `direction` being read-only, and `reward()` and `risk()` for buy and sell. `test_backtest_result.py` uses `BuySetup` in its shared-pair test.
- `requirements.md`: Domain Entities rows and CRC cards for `BuySetup` and `SellSetup`, with no collaborators.

The Phase 04 v1 check reported PHASE-04 V1: READY.

## Engineering Review

Claude Code ran the Phase 04 engineering review against `phase-04-v1` without modifying files, and probed edge cases with a throwaway script. The requested checks passed for the code: both subclasses pass the is-a test, the superclass holds only shared state and behavior, the overrides are meaningful, a bare `TradeSetup` cannot be created, the Phase 03 relationships still work, and nothing beyond Phase 04 scope was added. It reported 10 numbered findings. Daniel decided every finding.

**Real problems**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 1 | `domain-model.puml` still showed the Phase 03 `TradeSetup`, without subclasses or generalization arrows. | ACCEPT | Synced (see Diagram Sync). |
| 2 | `crc.puml` had no `BuySetup` or `SellSetup` cards. | ACCEPT | Cards added. |
| 3 | `requirements.md` did not record the inheritance decision. | ACCEPT | New "Inheritance" section. |
| 4 | Inherited behavior was tested only through `BuySetup`. | ACCEPT | `SellSetup` tests added (see Tests). |

**Assessed points**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 5 | The subclass `__init__` methods only call `super().__init__`, so they are redundant. | REJECT | None. The guide requires each subclass `__init__` to call `super().__init__`. |
| 6 | `TradeSetup.__init__` calls `_check_price_order()`, which subclasses override. It is safe today but fragile: a subclass that sets its own state after `super().__init__` and uses it in its check gets `AttributeError`, because the check runs before that state exists. | Keep until Phase 05 | None in code. Phase 05 switches to `@abstractmethod`. The risk is recorded below. |

**Optional ideas**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 7 | The `TradeSetup` CRC card and Domain Entities row described direction as the superclass's own knowledge. | ACCEPT | Both say the direction comes from `BuySetup` or `SellSetup`, in `requirements.md` and `crc.puml`. |
| 8 | A bare `TradeSetup` with invalid input raises `ValueError` before `NotImplementedError`. | REJECT | None. A bare `TradeSetup` still cannot be built, and Phase 05 fixes the message. |
| 9 | The `direction`, `reward()`, and `risk()` stubs in `TradeSetup` cannot be reached and are not tested. | ACCEPT as a note | Recorded below for Phase 05. |
| 10 | The Phase 06 guide asks for "a subclass that exists only to change one behavior". `BuySetup` and `SellSetup` change only the direction rules. | ACCEPT as a note | Recorded below for Phase 06. |

## Requirements

- The `TradeSetup` Domain Entities row and CRC card say its direction comes from `BuySetup` or `SellSetup`.
- A new "Inheritance" section lists `BuySetup` is a `TradeSetup` and `SellSetup` is a `TradeSetup`. It says why the subclasses exist (FR2), what `TradeSetup` holds, what each subclass supplies, and that a bare `TradeSetup` cannot be created until Phase 05 makes it abstract.

## Diagram Sync

- **`domain-model.puml`:**
  - The header names `tools/models/` (Phase 04) as the source, explains `#` for attributes a subclass reads, and says subclasses list only the members they define or override.
  - `TradeSetup` shows `- _pair`, `# _entry`, `# _stop_loss`, `# _take_profit`, the four-argument `__init__`, `# _check_price_order()`, the `direction` property, and `reward()`, `risk()`, and `reward_to_risk()`. `_entry`, `_stop_loss`, and `_take_profit` are protected because the subclasses read them. A note says `TradeSetup` cannot be created directly and becomes abstract in Phase 05.
  - New `BuySetup` and `SellSetup` boxes list only their own `__init__`, `# _check_price_order()`, `direction`, `reward()`, and `risk()`.
  - Generalization arrows: `TradeSetup <|-- BuySetup` and `TradeSetup <|-- SellSetup`. The `CurrencyPair` association and the `BacktestResult` aggregation stay on `TradeSetup` only.
  - The ValidationRules note gives `TradeSetup` the price rule (finite numbers > 0) and gives each subclass its own FR2 price order.
- **`crc.puml`:** new `BuySetup` and `SellSetup` cards with no collaborators. The `TradeSetup` card says its direction comes from `BuySetup` or `SellSetup`.
- **`use-cases.puml`:** unchanged, because no actor goal changed.
- Claude Code compared every class box with the code (attributes, properties, methods, and visibility) and the generalization arrows with the class hierarchy. All matched. Claude Code could not run PlantUML's syntax check, because PlantUML is not installed in its environment.

## Tests

| File | `phase-03-completed` | `phase-04-v1` | Now | Change |
|---|---|---|---|---|
| `test_currency_pair.py` | 37 | 37 | 37 | Unchanged. |
| `test_trade_setup.py` | 35 | 36 | 53 | At `phase-04-v1`: the constructor and direction changes above. After review: 17 `SellSetup` tests for inherited behavior (integer prices stored as floats, pair identity, pair read-only, using its pair, 4 wrong-type pairs, and 9 invalid prices). |
| `test_backtest_result.py` | 25 | 25 | 25 | The shared-pair test uses `BuySetup`. |

The tests use only fixed data and do not call the OANDA API.

Results: `tests/models/` gives 115 passed. The full suite gives 202 passed and 2 failed, and the 2 failures are the known failures recorded in `docs/evolution/phase-02.md`.

## Notes for Later Phases

| Phase | Note |
|---|---|
| 05 | Make `TradeSetup` abstract with `@abstractmethod`. The candidates are the stubs that raise `NotImplementedError` today: `_check_price_order()`, `direction`, `reward()`, and `risk()`. They cannot be reached and are not tested (finding 9). The error message for a bare `TradeSetup` with invalid input is fixed there (finding 8). |
| 05 | **Risk for future subclasses (finding 6):** `TradeSetup.__init__` calls `_check_price_order()` before a subclass `__init__` continues after `super().__init__`. A subclass that sets its own state after `super().__init__` and reads it in `_check_price_order()` gets `AttributeError`. Keep this in mind for any subclass added before the switch. |
| 06 | `BuySetup` and `SellSetup` exist only to change the direction rules. They are a likely candidate for the Phase 06 refactoring to composition, delegation, or interface-based polymorphism (finding 10). |
| Still deferred | R3, the same-pair rule, and Phase 02 finding 4 (Phase 06). Phase 02 D5, the reward-to-risk minimum of 2. |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code ran the start check, suggested candidate hierarchies, and implemented only Daniel's decisions.
- Claude Code ran the v1 check, committed `573ed95`, and created `phase-04-v1`.
- Claude Code ran the engineering review without modifying files, applied only the findings Daniel accepted, synced the diagrams, and wrote this record.

## End State

- `phase-04-v1` points to commit `573ed95`, the implementation before review. It is pushed to `origin/phase-04`.
- The review changes, the diagram sync, the new tests, this record, and the README roadmap update are in the commit "Complete Phase 04 inheritance", made after `phase-04-v1`.
- No files outside `tools/models/`, `tests/models/`, `docs/`, and the README roadmap changed since `phase-03-completed`.

## Verification Confirmation
I personally inspected domain-model.puml and crc.puml in IntelliJ and confirmed they match my approved Phase 04 decisions.
