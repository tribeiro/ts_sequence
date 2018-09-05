import os
import time
from salpytools import salpylib
from astropy.io import fits
import numpy as np
import datetime

from lsst.ts.sequence import BaseSequence

__all__ = ['ATTakeImage']


def time_stamped(fmt='AT-O-%Y%m%d-%H%M%S_{index:05}'):
    return datetime.datetime.now().strftime(fmt)


class ATTakeImage(BaseSequence):
    """
    Implementation of the take image sequence with the AT Camera.
    """
    def __init__(self):
        super().__init__(component_list=[('atcamera', None),
                                         ('atHeaderService', None),
                                         ('atArchiver', None)],
                         sub_sequences=[])

        # Subscribing to events from the components
        # Super class creates a sender for each of the components but does not subscribe to events as this will be
        # heavily dependent on how the sequence is written.
        # In principle, this could be done at the super class level but not all sequences may need this,
        # so I'll do it here for now
        self.atcam_events = salpylib.DDSSubscriberContainer(self.component_list[0][0],
                                                            device_id=self.component_list[0][1])
        self.athdr_events = salpylib.DDSSubscriberContainer(self.component_list[1][0],
                                                            device_id=self.component_list[1][1])
        self.atarc_events = salpylib.DDSSubscriberContainer(self.component_list[2][0],
                                                            device_id=self.component_list[2][1])

        # Set the parameters required to configure the script
        self.image_counter = 0

        self.config['numImages'] = 1  # Number of images to be taken.
        self.config['expTime'] = 0.  # Exposure time in seconds
        self.config['shutter'] = False  # Should the shutter be opened (True) or kept closed?
        self.config['science'] = False  # Is this a science image? True or False
        self.config['read_out_time'] = 2.  # Readout time in seconds

        self.image_root_name = time_stamped()

    def configure(self, **kwargs):
        # Get the parameters from an event and configure script
        self.log.debug('Configuring...')
        self.config['numImages'] = kwargs.pop('numImages', 1)
        self.config['expTime'] = kwargs.pop('expTime', 0.)
        self.config['shutter'] = kwargs.pop('shutter', False)
        self.config['science'] = kwargs.pop('science', False)
        self.config['read_out_time'] = kwargs.pop('read_out_time', 2.)
        self.config['shutter_time'] = kwargs.pop('shutter_time', 2.)

    def run_time(self):
        """
        Extimate run time from set of parameters.

        :return:
        run_time: float : seconds
        """

        return (self.config['expTime'] +
                self.config['read_out_time'] +
                self.config['shutter_time'] if self.config['shutter'] else 0.) * self.config['numImages']

    def execute(self):

        self.log.debug('Starting take image sequence...')

        for n_image in self.config['numImages']:
            self.log.debug('Taking image %i of %i...', n_image, self.config['numImages'])

            cmd_id = self.atcamera.send_Command('takeImages', numImages=1,
                                                expTime=self.config['expTime'],
                                                shutter=self.config['shutter'],
                                                imageSequenceName=self.image_name,
                                                science=self.config['science'],
                                                wait_command=True)

            # Checks that the command was executed, interrupt if it failed
            ack = self.atcamera.cmd_responses[cmd_id[0]]['ack'][-1]  # Get the last ack
            if ack[0] != 303 and ack[1] != 0:
                raise IOError('Sequence could not be executed. Received (%i, %i, %s) ack response.' % (ack[0],
                                                                                                       ack[1],
                                                                                                       ack[2]))
            else:
                self.log.debug('Image %i of %i complete.', n_image, self.config['numImages'])

        self.log.debug('Take image sequence complete...')

    @property
    def image_name(self):
        """
        Image name generator. Increments internal counter and returns time_stamped string.

        Returns
        -------
        image_name: str: Self generated image name.
        """
        self.image_counter += 1
        return self.image_root_name.format(self.image_counter)
