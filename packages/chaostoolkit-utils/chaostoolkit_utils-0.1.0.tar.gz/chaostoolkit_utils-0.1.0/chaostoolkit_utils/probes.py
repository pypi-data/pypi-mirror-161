import re
import requests

from chaoslib.exceptions import ActivityFailed

__all__ = ["check_site_content"]


def check_site_content(
    url: str,
    pattern: str,
    timeout: int=5,
) -> bool:
    """Checks a site content against a pattern"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            raise ActivityFailed(f"HTTP request failed: {response.status_code}")
        if re.search(pattern, response.text):
            return True
        else:
            return False
    except Exception as e:
        raise ActivityFailed(f"Something else went wrong!: {e}")
