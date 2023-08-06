from __future__ import annotations

from typing import Dict, Any

import pandas as pd


class BaseResult:
    """Base class for the internal representation of experimental observations and export to a dictionary of values.

    Each observation will be a collection of named values arising from a single run of an experiment.

    The basic attributes of start/end times, error states, and argument values are handled in this class. Subclasses
    must call super().__init__ in order to initialise these values properly.

    """

    def __init__(self):
        """Base constructor of the BaseResult class. Please call this in the constructor of your subclass.

        """
        self.execution_id = None
        self.start = pd.NaT
        self.end = pd.NaT
        self.errored = False
        self.force_stopped = False
        self.error_message = None
        self.args = None

    def to_dict(self) -> Dict[str, Any]:
        """Export the result values to a dictionary.

        Returns:
            Dict[str, Any]: dictionary of values derived from this result.
        """
        d = {}
        for k, v in self.__dict__.items():
            if k != 'args':
                d[k] = v
            else:
                for i, a in enumerate(v):
                    d[f'arg{i}'] = a
        return d