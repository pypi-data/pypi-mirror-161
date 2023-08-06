"""
Calculations with time series
"""

from seven2one import TechStack
from .scope import Scope

class CalQlator:

    def __init__(self, client: TechStack):
        self._client = client

    def scope(self, inventory_name: str, from_timepoint: str, to_timepoint: str) -> Scope:
        return Scope(self._client, inventory_name, from_timepoint, to_timepoint)
