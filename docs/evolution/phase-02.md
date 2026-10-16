# Phase 02 Evolution Record: From Design to Objects

> This record was started during Section 2 to log known test failures. The remaining sections are written in Section 8 of the Phase 02 guide.

## Known Test Failures

Daniel recorded two existing API tests as known failures from before Phase 01. They are not caused by Phase 02 work.

| Test | Expected | Actual |
|---|---|---|
| `tests/test_api_endpoints.py::test_get_candles_unknown_pair_404` | 404 for `/candles/FAKE_PAIR/H1` | 502 |
| `tests/test_api_endpoints.py::test_get_candles_unknown_timeframe_404` | 404 for `/candles/EUR_USD/D1` | 502 |

**Evidence:**

- `tests/test_api_endpoints.py` and `tools/api/server.py` have not changed since the repository's first commit (`e4b62a2`), and are identical at `phase-00-completed`.
- No code outside `tools/models/` imports `tools.models`.
- In the first full `pytest` run of Phase 02, these were the only failures: 87 passed, 2 failed.

**Likely cause (requirement → test → code):**

- No requirement in `docs/design/requirements.md` covers the API endpoints. The tests come from code written before Phase 01.
- The tests expect 404 for an unknown pair or an unsupported timeframe.
- The candles endpoint does not validate the pair or timeframe. When no cached file exists, it tries to fetch from OANDA and returns 502 when that fails. Both tests therefore cause a fetch attempt against the OANDA practice API.

The code and the tests were left unchanged. The Phase 02 guide forbids changes to existing tools, and `AGENTS.md` forbids changing a test only because the code fails it.
