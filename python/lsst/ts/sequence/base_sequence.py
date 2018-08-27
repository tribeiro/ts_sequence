import logging
from salpytools import salpylib
import json

__all__ = ['BaseSequence']


class BaseSequence:

    def __init__(self, component_list, sub_sequences=None):
        self._name = type(self).__name__
        self.log = logging.getLogger(self._name)

        self.sender = salpylib.DDSSend('scheduler')  # to send request to the OCS.

        self.config = {}

        self.component_list = component_list

        # TODO: Placeholder for when a sequence uses a list of sub-sequences to perform part of its actions.
        self.sub_sequences = []
        if sub_sequences is not None:
            self.sub_sequences = sub_sequences

        # Dynamically create a sender for each of the components...
        for component in component_list:
            self.log.debug('Subscribing to %s sender...', component[0])
            setattr(self, component[0], salpylib.DDSSend(component[0], component[1]))
            getattr(getattr(self, component[0]), 'start')()

    def configure(self, **kwargs):
        """Get set of parameters from event and configure sequence.

        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        raise NotImplementedError()

    def run_time(self):
        """Estimate run time from set of parameters.

        Returns
        -------

        """
        return -1

    def execute(self):
        """Executes script to completion.

        Returns
        -------

        """
        raise NotImplementedError()

    def request(self):
        """Send request to the OCS to run this script.

        Returns
        -------

        """
        payload = {"script": self._name,
                   "components": self.component_list,
                   "sub_sequences": self.sub_sequences,
                   "config": self.config,
                   "run_time": self.run_time()}

        self.log.debug('payload: %s', json.dumps(payload))
        self.sender.send_Event('target', payload=json.dumps(payload))  # This may need to be a command!?

        return True
