"""
Strategy module – isolated, extensible, easy to test.

Each strategy is a callable: (prices: list[float], **kwargs) -> dict
returning {"signal": "BUY"|"SELL"|"HOLD", "reason": str}
"""
from __future__ import annotations
import numpy as np


# ─── Strategy implementations ────────────────────────────────────────────────

def moving_average_crossover(prices: list[float], window_short: int = 7, window_long: int = 25, **_) -> dict:
    """
    Classic dual-MA crossover.
    BUY  – short MA crosses above long MA (golden cross)
    SELL – short MA crosses below long MA (death cross)
    HOLD – no crossover
    """
    if len(prices) < window_long:
        return {"signal": "HOLD", "reason": f"Not enough data (need {window_long} points)"}

    arr = np.array(prices, dtype=float)
    short_ma = float(np.mean(arr[-window_short:]))
    long_ma = float(np.mean(arr[-window_long:]))

    # Previous candle MAs for crossover detection
    prev_short = float(np.mean(arr[-(window_short + 1):-1]))
    prev_long = float(np.mean(arr[-(window_long + 1):-1]))

    if prev_short <= prev_long and short_ma > long_ma:
        return {
            "signal": "BUY",
            "reason": f"Golden cross: {window_short}-MA ({short_ma:.2f}) crossed above {window_long}-MA ({long_ma:.2f})",
        }
    if prev_short >= prev_long and short_ma < long_ma:
        return {
            "signal": "SELL",
            "reason": f"Death cross: {window_short}-MA ({short_ma:.2f}) crossed below {window_long}-MA ({long_ma:.2f})",
        }
    direction = "above" if short_ma > long_ma else "below"
    return {
        "signal": "HOLD",
        "reason": f"{window_short}-MA ({short_ma:.2f}) is {direction} {window_long}-MA ({long_ma:.2f}), no crossover",
    }


def momentum_threshold(prices: list[float], window: int = 14, threshold: float = 3.0, **_) -> dict:
    """
    Simple momentum: if price ROC over `window` bars > +threshold% → BUY,
    < -threshold% → SELL, else HOLD.
    """
    if len(prices) < window + 1:
        return {"signal": "HOLD", "reason": f"Not enough data (need {window + 1} points)"}

    arr = np.array(prices, dtype=float)
    roc = (arr[-1] - arr[-window - 1]) / arr[-window - 1] * 100

    if roc > threshold:
        return {"signal": "BUY", "reason": f"Momentum +{roc:.2f}% over {window} periods (threshold {threshold}%)"}
    if roc < -threshold:
        return {"signal": "SELL", "reason": f"Momentum {roc:.2f}% over {window} periods (threshold -{threshold}%)"}
    return {"signal": "HOLD", "reason": f"Momentum {roc:.2f}% within threshold ±{threshold}%"}


# ─── Registry ────────────────────────────────────────────────────────────────

STRATEGIES: dict[str, callable] = {
    "moving_average": moving_average_crossover,
    "momentum": momentum_threshold,
}


def run_strategy(name: str, prices: list[float], **kwargs) -> dict:
    fn = STRATEGIES.get(name)
    if not fn:
        raise ValueError(f"Unknown strategy '{name}'. Available: {list(STRATEGIES)}")
    return fn(prices, **kwargs)
