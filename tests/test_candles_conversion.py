"""Standalone test script for Candles.to_dataframe() and Candles.to_numpy()."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from models.candles import Candle, Candles

EXPECTED_COLUMNS = ["open_time", "open", "high", "low", "close", "volume"]

passed = 0
failed = 0


def _make_candle(i: int) -> Candle:
    """Helper: build a deterministic candle from an index."""
    return Candle(
        open_time=1000 * i,
        open_price=100.0 + i,
        high_price=110.0 + i,
        low_price=90.0 + i,
        close_price=105.0 + i,
        volume=50.0 + i,
    )


def run(name: str, fn) -> None:  # noqa: ANN001
    global passed, failed
    try:
        fn()
        print(f"  {name} ... PASS")
        passed += 1
    except AssertionError as exc:
        print(f"  {name} ... FAIL  ({exc})")
        failed += 1


# ── Test 1: Empty Candles → to_dataframe() ──────────────────────────────────

def test_empty_to_dataframe() -> None:
    c = Candles()
    df = c.to_dataframe()
    assert isinstance(df, pd.DataFrame), "expected DataFrame"
    assert list(df.columns) == EXPECTED_COLUMNS, f"columns mismatch: {list(df.columns)}"
    assert len(df) == 0, f"expected 0 rows, got {len(df)}"


# ── Test 2: Empty Candles → to_numpy() ──────────────────────────────────────

def test_empty_to_numpy() -> None:
    c = Candles()
    arrays = c.to_numpy()
    assert isinstance(arrays, dict), "expected dict"
    assert set(arrays.keys()) == set(EXPECTED_COLUMNS), f"keys mismatch: {set(arrays.keys())}"
    for key in EXPECTED_COLUMNS:
        assert isinstance(arrays[key], np.ndarray), f"{key} is not ndarray"
        assert len(arrays[key]) == 0, f"{key} should be empty"


# ── Test 3: One candle → 1-row results ──────────────────────────────────────

def test_one_candle() -> None:
    c = Candles()
    c.add_candle(_make_candle(1))

    df = c.to_dataframe()
    assert len(df) == 1, f"expected 1 row, got {len(df)}"
    assert df["open_time"].iloc[0] == 1000
    assert df["open"].iloc[0] == 101.0
    assert df["high"].iloc[0] == 111.0
    assert df["low"].iloc[0] == 91.0
    assert df["close"].iloc[0] == 106.0
    assert df["volume"].iloc[0] == 51.0

    arrays = c.to_numpy()
    assert len(arrays["close"]) == 1
    assert arrays["open_time"][0] == 1000
    assert arrays["close"][0] == 106.0


# ── Test 4: Two candles → 2-row results ─────────────────────────────────────

def test_two_candles() -> None:
    c = Candles()
    c.add_candle(_make_candle(1))
    c.add_candle(_make_candle(2))

    df = c.to_dataframe()
    assert len(df) == 2, f"expected 2 rows, got {len(df)}"
    assert df["close"].iloc[0] == 106.0
    assert df["close"].iloc[1] == 107.0

    arrays = c.to_numpy()
    assert len(arrays["close"]) == 2
    assert arrays["close"][0] == 106.0
    assert arrays["close"][1] == 107.0


# ── Test 5: Cache hit — _df_cache_gen unchanged on second call ──────────────

def test_cache_hit() -> None:
    c = Candles()
    c.add_candle(_make_candle(1))

    df1 = c.to_dataframe()
    gen_after_first = c._df_cache_gen

    df2 = c.to_dataframe()
    gen_after_second = c._df_cache_gen

    assert gen_after_first == gen_after_second, (
        f"cache gen changed: {gen_after_first} → {gen_after_second}"
    )
    assert df1.equals(df2), "DataFrames should be equal"


# ── Test 6: Cache invalidation after add_candle() ───────────────────────────

def test_cache_invalidation() -> None:
    c = Candles()
    c.add_candle(_make_candle(1))

    df1 = c.to_dataframe()
    assert len(df1) == 1

    c.add_candle(_make_candle(2))
    df2 = c.to_dataframe()
    assert len(df2) == 2, f"expected 2 rows after add, got {len(df2)}"
    assert df2["close"].iloc[1] == 107.0


# ── Test 7: Deque rollover with max_candles=2 ───────────────────────────────

def test_deque_rollover() -> None:
    c = Candles(max_candles=2)
    c.add_candle(_make_candle(1))
    c.add_candle(_make_candle(2))
    c.add_candle(_make_candle(3))

    df = c.to_dataframe()
    assert len(df) == 2, f"expected 2 rows, got {len(df)}"
    assert df["open_time"].iloc[0] == 2000, "first candle should be index 2"
    assert df["open_time"].iloc[1] == 3000, "second candle should be index 3"

    arrays = c.to_numpy()
    assert len(arrays["close"]) == 2
    assert arrays["open_time"][0] == 2000
    assert arrays["open_time"][1] == 3000


# ── Test 8: Mutation safety ─────────────────────────────────────────────────

def test_mutation_safety() -> None:
    c = Candles()
    c.add_candle(_make_candle(1))

    # DataFrame mutation
    df = c.to_dataframe()
    original_close = df["close"].iloc[0]
    df.loc[0, "close"] = 999.0
    df_again = c.to_dataframe()
    assert df_again["close"].iloc[0] == original_close, (
        "DataFrame mutation leaked into cache"
    )

    # Numpy mutation
    arrays = c.to_numpy()
    original_np_close = arrays["close"][0]
    arrays["close"][0] = 999.0
    arrays_again = c.to_numpy()
    assert arrays_again["close"][0] == original_np_close, (
        "Numpy mutation leaked into cache"
    )


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Candles conversion tests")
    print("=" * 60)
    run("1. Empty Candles → to_dataframe()", test_empty_to_dataframe)
    run("2. Empty Candles → to_numpy()", test_empty_to_numpy)
    run("3. One candle → 1-row results", test_one_candle)
    run("4. Two candles → 2-row results", test_two_candles)
    run("5. Cache hit (gen unchanged)", test_cache_hit)
    run("6. Cache invalidation after add", test_cache_invalidation)
    run("7. Deque rollover (max_candles=2)", test_deque_rollover)
    run("8. Mutation safety", test_mutation_safety)
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
