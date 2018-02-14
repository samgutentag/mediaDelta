#!/usr/bin/end python

import logging
from datetime import datetime

class MediaFileObject:

    """
    Media File Object is information about a media file, can be an image or video file
    @attributes:
        type            - media file type (str), defaults to 'image'
            - ['image', 'video', 'other']
        extension       - file extention (str), defaults to 'txt'
        creation        - media file creation timestamp (datetime), defaults to epoch
        cameraObject    - CameraObject (CameraObject). defaults to 'NaN'
        creator         - creator name or username (str), defaults to logged in user's username
        width           - media width in pixes (int), defaults to 0
        height          - media height in pixes (int), defaults to 0
        duration        - media file duration in seconds (int), defaults to 0

    """

    def __init__(self, type, extension, dateTimeObject, cameraObject, creator, width, height):
        self.type = type
        self.extension = extension
        self.creation = creation
        self.camera = cameraObject
        self.creator = creator
        self.width = width
        self.height = height
        self.duration = duration

    def printInfo(self, logging=True):
        print('Type         {}'.format(self.type))
        print('Extension    {}'.format(self.extension))
        print('Creation     {}'.format(self.creation))
        print('Creator      {}'.format(self.creator))
        print('Width        {}'.format(self.width))
        print('Height       {}'.format(self.height))
        print('Duration     {}'.format(self.duration))

        if logging:
            logging.info('Type         {}'.format(self.type))
            logging.info('Extension    {}'.format(self.extension))
            logging.info('Creation     {}'.format(self.creation))
            logging.info('Creator      {}'.format(self.creator))
            logging.info('Width        {}'.format(self.width))
            logging.info('Height       {}'.format(self.height))
            logging.info('Duration     {}'.format(self.duration))

        self.camera.printInfo(logging=logging)
