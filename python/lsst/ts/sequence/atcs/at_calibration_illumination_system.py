import os
import time
from salpytools import salpylib
from astropy.io import fits
import numpy as np

from lsst.ts.sequence import BaseSequence

__all__ = ['WavelengthCalibrationSequence']


class WavelengthCalibrationSequence(BaseSequence):
    '''

    '''
    def __init__(self):
        super().__init__(component_list=[('calibrationElectrometer', 1),
                                         ('atMonochromator', None),
                                         ('sedSpectrometer', None)],
                         sub_sequences=[])

        # Subscribing to events from the components
        # Super class creates a sender for each of the components but does not subscribe to events as this will be
        # heavily dependent on how the sequence is written.
        # In principle, this could be done at the super class level but not all sequences may need this,
        # so I'll do it here for now
        self.ce_events = salpylib.DDSSubscriberContainer(self.component_list[0][0],
                                                         device_id=self.component_list[0][1])
        self.atm_event = salpylib.DDSSubscriberContainer(self.component_list[1][0],
                                                         device_id=self.component_list[1][1])
        self.sed_events = salpylib.DDSSubscriberContainer(self.component_list[2][0],
                                                          device_id=self.component_list[2][1])

        # Set the parameters required to configure the script
        self.intensity = 15000.  # Default intensity
        self.max_exptime = 120.  # Max exptime in seconds
        self.gratingType = 1  # Grating type
        self.fontExitSlitWidth = 4.0  # size of exit slit
        self.fontEntranceSlitWidth = 2.0  # size of entrance slit
        self.wavelength = 550  # wavelength in nm

        # In principle the (O, T, AT)CS should be able to interrogate the class about the components it will use,
        # which are available on self.component_list. Then, the CS would be responsible for enabling them, so when
        # self.execute() is called all the required components are up and running and ready to go.

    def configure(self, **kwargs):
        # Get the parameters from an event and configure script
        self.log.debug('Configuring...')
        self.intensity = 15000.  # Default intensity
        self.max_exptime = 120.  # Max exptime in seconds
        self.gratingType = 1  # Grating type
        self.fontExitSlitWidth = 4.0  # size of exit slit
        self.fontEntranceSlitWidth = 2.0  # size of entrance slit
        self.wavelength = 550  # wavelength in nm

    def run_time(self):
        """
        Extimate run time from set of parameters.

        :return:
        run_time: float : seconds
        """
        total_sleep_time = 3  # seconds spent sleeping...

        current_grating = self.atm_event.selectedGrating.gratingType
        grating_time = 0.
        if current_grating != self.gratingType:
            current_grating += 30.  # add 30 seconds to switch grating
        exptime = self.max_exptime  # will assume max_exptime for simplicity

        return total_sleep_time+grating_time+exptime

    def execute(self):

        # Set up monochromator. This command is commented now so it won't stress the system with tests
        # cmd_id = self.sender.atMonochromator.send_Command('updateMonochromatorSetup',
        #                                                   gratingType=self.gratingType,
        #                                                   fontExitSlitWidth=self.fontExitSlitWidth,
        #                                                   fontEntranceSlitWidth=self.fontEntranceSlitWidth,
        #                                                   wavelength=self.wavelength,
        #                                                   wait_command=True)

        # sleep for 1 second after setting monochromator so the measurement stabilizes
        time.sleep(1.)
        # Get a measure of the current intensity from events
        if self.ce_events.intensity.intensity == 0.:
            raise IOError("Lamp intensity is zero! It is either switched off or integration time is too short.")
        flux = self.ce_events.intensity.intensity / self.ce_events.integrationTime.intTime
        exptime = self.intensity / flux
        if exptime > self.max_exptime:
            # Will probably want to send a warning event here
            exptime = self.max_exptime

        # Now take a spectrum and measure intensity at the same time
        # Will not wait for this command, so we can capture a spectrum simultaneously
        # We can improve this control sequence here but for now lets keep it simple, I'll just add 2 extra seconds
        # so the electrometer read starts 1 second before the sed spectrum and finishes 1 second after.
        cmd_id2 = self.sender.calibrationElectrometer.send_Command('StartScanDt',
                                                                   time=exptime + 2.,
                                                                   wait_command=False)
        # wait a second before starting to capture
        time.sleep(1)
        # Take a spectrum with SED Spectrograph. Wait for the read to complete.
        cmd_id3 = self.sender.sedSpectrometer.send_Command('captureSpectImage', imageType='test',
                                                           integrationTime=exptime, lamp='lamp',
                                                           wait_command=True)
        # wait a second after spectrum is captured
        time.sleep(1)
