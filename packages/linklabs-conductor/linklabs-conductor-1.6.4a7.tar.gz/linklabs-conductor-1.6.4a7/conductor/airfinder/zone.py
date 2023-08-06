""" Represents an Airfinder Zone. """

from conductor.airfinder.base import AirfinderSubject
from conductor.airfinder.devices.location import Location


class Zone(AirfinderSubject):
    """ An Airfinder Zone within an Airfinder Area. """
    subject_name = 'Zone'

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def version(self):
        return None

    @property
    def site_id(self):
        """ Get the Site that the area is within. """
        return self._make_prop('siteId', str)

    @property
    def area_id(self):
        return self._make_prop('areaId', str)

    ###########################################################################
    # Private Methods
    ###########################################################################

    def _get_registered_asset_by_zone(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the Network
        Asset API.

        Args:
            subject_name (str): Asset name.
            subject_id (srt): Asset id.

        Returns:
            (dict) json data.
        """
        url = ''.join([self._af_network_asset_url, '/{}/{}'.format(subject_name, subject_id)])
        params = {
            'siteId': self.site_id,
            'areaId': self.area_id,
            'zoneId': self.subject_id
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _get_registered_assets_by_zone(self, asset_name):
        """ Base function for getting list of registered assets from the
        Network Asset API.

        Args:
            asset_name: Asset name.

        Returns:
            (dict) json data.
        """
        url = ''.join([self._af_network_asset_url, '/', asset_name])
        params = {
            'siteId': self.site_id,
            'areaId': self.area_id,
            'zoneId': self.subject_id
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    ###########################################################################
    # Manage Locations
    ###########################################################################

    def add_location(self, mac_id, name):
        """ Adds a location to a site. """
        url = ''.join([self._af_network_asset_url, 'locations'])
        params = {
            "macAddress": mac_id,
            'siteId': self.site_id,
            'areaId': self.area_id,
            'zoneId': self.subject_id,
            "name": name,
            "properties": "object",
            "proxyLocations": [""]
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        x = resp.json()
        return Location(self.session, x.get('id'), _data=x)

    def get_location(self, mac_id):
        """ Gets a location, in a site. """
        x = self._get_registered_asset_by_zone('location', mac_id)
        return Location(self.session, mac_id, self.instance, _data=x)

    def get_locations(self):
        """ Get all the locations in a site. """
        return [Location(self.session, x['assetInfo']['metadata']['props']['macAddress'], self.instance, _data=x)
                for x in self._get_registered_assets_by_zone('locations')]

    # TODO
    def remove_location(self, mac_id):
        """ Remove a location from a site. """
        raise NotImplementedError
