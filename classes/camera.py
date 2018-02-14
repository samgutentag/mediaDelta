#!/usr/bin/end python

import logging

class CaptureDeviceObject:

    """
    Capture Device Object consists of capture or creation device specs
    @attributes:
        make        - capture device make name or brand (str)
        model       - capture device model name (str)
        serial      - capture device serial number (str)
        software    - software program used to create media file, punctuation and spaces removed (str)
    """

    def __init__(self, make, model, serial, software):
        self.make       = str(make).replace(' ','.').lower()
        self.model      = str(model).replace(' ','.').lower()
        self.serial     = str(serial).lower()
        self.software   = str(software).split('(')[0].replace(' ', '.').lower()

    def printInfo(self, logging=True):
        print('Capture Device Make:     {}'.format(self.make))
        print('Capture Device Model:    {}'.format(self.model))
        print('Serial Number:   {}'.format(self.serial))
        print('Software:        {}'.format(self.software))

        if logging:
            logging.info('Camera Make:     {}'.format(self.make))
            logging.info('Camera Model:    {}'.format(self.model))
            logging.info('Serial Number:   {}'.format(self.serial))
            logging.info('Software:        {}'.format(self.software))
