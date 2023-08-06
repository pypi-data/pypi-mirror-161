from conductor.airfinder.devices.access_point import AccessPoint
from conductor.airfinder.devices.nordic_access_point import NordicAccessPoint
from conductor.airfinder.devices.sercomm_supertag import SercommSupertag
from conductor.airfinder.devices.xle_access_point import XLEAccessPoint


def is_access_point_application(app_token):
    """ Determines if the given application token is that of an Access Point device.

    :param app_token: The application token
    :return if the application token is an access point type
    """
    return app_token == AccessPoint.application or \
        app_token == NordicAccessPoint.application or \
        app_token == XLEAccessPoint.application


def is_supertag_token(app_token):
    """ Determines if the given application token is that of an Access Point device.

    @param app_token The application token
    @returns if the application token is an access point type
    """
    return app_token == SercommSupertag.application or \
        app_token == SercommSupertag.virtual_ap_app
