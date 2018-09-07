import time

from lsst.ts.sequence import BaseSequence

__all__ = ['ATRaiseException']

class ATRaiseException(BaseSequence):
    """
    Test script that just raises an exception.
    """
    def __init__(self):
        super().__init__(component_list=[],
                         sub_sequences=[])

    def execute(self):
        """Wait one second and raises an exception.

        Returns
        -------

        """
        time.sleep(1.)

        raise IOError("This is a test exception.")
