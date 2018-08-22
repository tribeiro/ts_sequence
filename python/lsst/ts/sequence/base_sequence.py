import logging
from salpytools import salpylib

__all__ = ['BaseSequence']


class BaseSequence:

    def __init__(self, component_list, sub_sequences=None):
        self.log = logging.getLogger(type(self).__name__)

        self.component_list = component_list

        # TODO: Placeholder for when a sequence uses a list of sub-sequences to perform part of its actions.
        self.sub_sequences = []
        if sub_sequences is not None:
            self.sub_sequences = sub_sequences

        # Dynamically create a sender for each of the components...
        for component in component_list:
            setattr(self, component[0], salpylib.DDSSend(component[0], component[1]))

    def configure(self, **kwargs):
        """
        Get set of parameters from event and configure sequence.

        :return:
        """
        raise NotImplementedError()

    def run_time(self):
        """
        Extimate run time from set of parameters
        :return:
        """

        return -1

    def execute(self):
        """
        Executes script to completion.

        :return:
        """
        raise NotImplementedError()
