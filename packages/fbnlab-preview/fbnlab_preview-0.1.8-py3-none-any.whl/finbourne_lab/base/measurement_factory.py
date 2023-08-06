from __future__ import annotations

from typing import Dict, Callable, List, Iterable


class BaseMeasurementFactory:
    """Base class for standard measurement sets. Standard measurement sets are the set of standard measurements that
    characterise the performance of a given Finbourne application.

    Standard measurement sets should have a set of methods ending with _measurement for each individual standard
    measurement which output a Convener instance or a tuple of Convener instances.

    Each measurement method must be documented with a docstring.
    """

    def __init__(self, work_dir):
        """Base constructor of the measurement set

        Args:
            work_dir: the working directory to use in the conveners of the standard measurement set.

        """

        self.work_dir = work_dir
        self._validate()

    @staticmethod
    def make_range_label(rng, prefix):
        rng = rng if hasattr(rng, '__len__') else [rng]
        return prefix + '-'.join(str(v) for v in rng)

    def get_measurements(self) -> Dict[str, Callable]:
        """Get a dictionary of all the measurement methods of this class.

        Returns:
            Dict[str, Callable]: the dictionary of measurement names and methods.

        """
        return {m: getattr(self, m) for m in dir(self) if m.endswith('_measurement')}

    def list_conveners(self, **kwargs) -> List['Convener']:
        """List all the conveners to run in this standard measurement set.

        Returns:
            List[Convener]: the list of conveners.

        """

        def _flatten(it):
            for x in it:
                if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                    yield from _flatten(x)
                else:
                    yield x

        return list(_flatten(map(lambda x: x(**kwargs), self.get_measurements().values())))

    def _validate(self):
        d = self.get_measurements()
        not_documented = []
        for k, v in d.items():
            doc = v.__doc__
            if doc is None:
                not_documented.append(k)

    def teardown(self):
        pass

    def setup(self):
        pass

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()