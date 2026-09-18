"""Caching Module demonstrating functools.lru_cache and Caching Best Practices.

WHAT IS CACHING?
----------------
Caching stores the results of expensive function calls so that future requests with
the exact same arguments can return the pre-calculated result instantly without re-executing
the underlying computation.

HOW functools.lru_cache WORKS:
-------------------------------
- LRU stands for "Least Recently Used".
- It maintains a hash map of (arguments -> return_value).
- When the cache exceeds `maxsize` entries, the least recently accessed item is evicted.
- `maxsize` sets an upper bound on memory usage (e.g. maxsize=128).
- `cache_clear()` flushes all entries from the cache to release memory or force re-evaluation.

CACHING RISKS & DANGERS:
------------------------
1. Mutable Return Values:
   If a cached function returns a mutable object (like a list or dictionary), modifying
   the returned object will mutate the cached instance directly! Future callers receiving
   the cached result will see those unintended mutations.
   -> Solution: Return immutable types (tuples, strings, ints, frozensets) or return fresh copies.

2. Unbounded Memory Growth:
   If `@lru_cache(maxsize=None)` is used without a limit and a function is called with thousands
   or millions of distinct inputs, the cache will grow indefinitely, consuming memory and causing OOM.
   -> Solution: Always use a bounded cache (e.g., `@lru_cache(maxsize=128)`).

3. Stale Data:
   If the function depends on external state (database records, global configuration, or time)
   that changes over time, cached values will become outdated and inaccurate.
   -> Solution: Clear cache when underlying state mutates (`func.cache_clear()`) or avoid caching state-dependent code.
"""

from functools import lru_cache
import logging
from typing import Dict, Tuple

logger = logging.getLogger("task_analytics.caching")


@lru_cache(maxsize=128)
def calculate_task_priority_score(priority: str, complexity: int, due_days: int) -> float:
    """Calculates a normalized task priority score based on priority, complexity, and due days.

    Uses a bounded LRU cache (maxsize=128) so repeated calculations for the same inputs
    are returned instantly.

    Args:
        priority: Priority string ('high', 'medium', 'low').
        complexity: Story point complexity (1 to 10).
        due_days: Days remaining until due date.

    Returns:
        Calculated priority score as float.
    """
    priority_weights: Dict[str, float] = {
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0,
    }
    p_weight = priority_weights.get(priority.strip().lower(), 1.0)
    # Simulated computation
    score = (p_weight * 10.0) + (complexity * 1.5) - (due_days * 0.5)
    return round(score, 2)


@lru_cache(maxsize=64)
def get_task_category_weight(category: str) -> float:
    """Returns category weight multiplier.

    Demonstrates safe immutable return caching.
    """
    weights = {
        "bug": 2.5,
        "feature": 1.8,
        "documentation": 1.0,
        "refactor": 1.2,
    }
    return weights.get(category.strip().lower(), 1.0)


def dangerous_mutable_cache_demo(tags: Tuple[str, ...]) -> list:
    """Demonstrates why returning mutable values from a cache is dangerous.

    Note: We do NOT use this in pipeline code; it is provided purely for testing/demo.
    """
    return list(tags)  # Returning fresh list to avoid shared state mutations
