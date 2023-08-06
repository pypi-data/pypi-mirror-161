from conductor.airfinder.devices.location import Location
from conductor.util import Version


class af3Location(Location):

    application = "32badd3393adef587b10"

    @property
    def symble_version(self):
        pass

    @property
    def version(self):
        major = self._md.get('appFwVersionMajor')
        minor = self._md.get('appFwVersionMinor')
        tag = self._md.get('appFwVersionTag')
        if not major or not minor or not tag:
            return None
        return Version(int(major), int(minor), int(tag))
