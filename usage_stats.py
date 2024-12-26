# usage_stats.py
from collections import defaultdict

# A dictionary to track usage counts.
# Example: {"GET /numbers": 5, "GET /numbers/13136399690": 2}
endpoint_usage = defaultdict(int)

def record_usage(endpoint_id: str):
    """
    Increments usage for a given endpoint (like "GET /numbers" or "GET /numbers/123").
    """
    endpoint_usage[endpoint_id] += 1

def get_usage_stats():
    """
    Returns a dict of usage stats. Example:
    {
      "GET /numbers": 5,
      "GET /numbers/13136399690": 2
    }
    """
    return dict(endpoint_usage)
