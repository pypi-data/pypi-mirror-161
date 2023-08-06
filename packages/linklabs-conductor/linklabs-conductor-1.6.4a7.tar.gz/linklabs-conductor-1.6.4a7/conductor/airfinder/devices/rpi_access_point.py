""" Interface for the Raspberry Pi Access Point. """
from conductor.airfinder.devices.access_point import AccessPoint, AccessPointMessageSpecV1_0_0
from conductor.airfinder.devices.xle_access_point import XLEAccessPoint


class RPiAccessPoint(AccessPoint):
    """ Represents the legacy Raspberry Pi Access Point. """
    application = "8da02bc5df23f5b9017b"

    @classmethod
    def _get_spec(cls, vers):
        return AccessPointMessageSpecV1_0_0()


class RPiXLEAccessPoint(XLEAccessPoint):
    """ """
    application = "df64514ac54496149881"
