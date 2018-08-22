import logging
from salpytools import salpylib

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] [%(threadName)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

__all__ = ['BaseSequence']


class BaseSequence:

    def __init__(self, component_list):
        self.log = logging.getLogger(type(self).__name__)

        self.component_list = component_list

        # Dynamically create a sender for each of the components...
        for component in component_list:
            setattr(self, component[0], salpylib.DDSSend(component[0], component[1]))

    def configure(self):
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
