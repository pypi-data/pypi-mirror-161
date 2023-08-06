from conductor.airfinder.devices.nordic_access_point import NordicAccessPoint, NordicAPMessageSpecV2_0_5
from conductor.util import Version


class XLEAccessPoint(NordicAccessPoint):

    application = "0fd6d1a99148c4534548"

    @property
    def bootloader_version(self):
        """ Message Spec Version of the AP """
        major = self._md.get('bootloaderVersionMajor')
        minor = self._md.get('bootloaderVersionMinor')
        tag = self._md.get('bootloaderVersionTag')
        if not major or not minor or not tag:
            return None
        return Version(int(major), int(minor), int(tag))

    @classmethod
    def _get_spec(cls, vers):
        # TODO: Implement XLE msg spec.
        return NordicAPMessageSpecV2_0_5()

    @property
    def dfu_file_id(self):
        header_file_id = self._md.get("spiHeaderFileID")
        if header_file_id:
            return int(header_file_id)
        return self._make_prop('fileID', str)

    @property
    def dfu_file_version(self):
        version = self._md.get('spiHeaderVersion')
        if version:
            v = "{:08x}".format(int(version))
            try:
                return Version(int(v[:2], 16), int(v[2:4], 16), int(v[4:], 16)) if v else None
            except IndexError:
                return None
