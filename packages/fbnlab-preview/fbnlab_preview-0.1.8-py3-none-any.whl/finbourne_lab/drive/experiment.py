from finbourne_lab.common.api import ApiExperiment


class DriveExperiment(ApiExperiment):
    """Experiment class for the drive api

    """

    def __init__(self, build_fn, *ranges, **kwargs):
        """Constructor for the Drive API experiment class

        Args:
            build_fn (Callable): a function that builds a callable given a set of values. This callable makes a request
            to the API in question and returns the HTTPResponse object.
            application (str): the name of the application the experiment is running against.
            *ranges: range pairs, single values or sets to sample when running experiments.

        Keyword Args:
            throw_on_failure (bool): whether to throw an error when the metadata header doesn't show a success.
            Sometimes a lusid call can fail but have a success status code.

        """
        super().__init__(build_fn, 'drive', *ranges, **kwargs)
