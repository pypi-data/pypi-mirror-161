#!/usr/bin/env python3

# Images class
class Images:

    # Constants
    DOCKER_DIND_REGEX = r'.*docker:.*dind'
    LOCAL_IMAGE = 'local'
    LOCAL_QUIET_IMAGE = 'local:quiet'
    LOCAL_SILENT_IMAGE = 'local:silent'

    # Host
    @staticmethod
    def host(image):
        return image in (Images.LOCAL_IMAGE, Images.LOCAL_QUIET_IMAGE,
                         Images.LOCAL_SILENT_IMAGE)

    # Quiet
    @staticmethod
    def quiet(image):
        return image in (Images.LOCAL_QUIET_IMAGE, Images.LOCAL_SILENT_IMAGE)

    # Silent
    @staticmethod
    def silent(image):
        return image in Images.LOCAL_SILENT_IMAGE
