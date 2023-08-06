#!/usr/bin/env python3

# Components
from ..engines.engine import Engine

# ImagesFeature class
class ImagesFeature:

    # Members
    __engine = None
    __images = []

    # Constructor
    def __init__(self, jobs, options):

        # Prepare container images
        self.__images = []
        for job in jobs:

            # Extract container image
            image = jobs[job]['image']
            if image and not jobs[job]['options']['host'] and image not in self.__images:
                self.__images += [image]

            # Extract container services
            for service in jobs[job]['services']:
                if service['image'] not in self.__images:
                    self.__images += [service['image']]

        # Prepare container engine
        self.__engine = Engine(options)

    # Pull
    def pull(self, force=False):

        # Pull container images
        if self.__images:
            self.__images.sort()
            for image in self.__images:
                self.__engine.pull(image, force)

        # Result
        return bool(self.__images)

    # Remove images
    def rmi(self):

        # Remove container images
        if self.__images:
            self.__images.sort()
            for image in self.__images:
                self.__engine.rmi(image)

        # Result
        return bool(self.__images)
