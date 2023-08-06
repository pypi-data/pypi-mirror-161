"""" Represents an Airfinder Site. """
import logging

from conductor.devices.gateway import Gateway
from conductor.airfinder.base import AirfinderSubject
from conductor.airfinder.area import Area
from conductor.airfinder.devices.access_point import AccessPoint
from conductor.airfinder.devices.location import Location
from conductor.airfinder.devices.tag import Node, Tag
from conductor.util import find_cls, mac_to_addr, addr_to_mac

LOG = logging.getLogger(__name__)


class SiteUser(AirfinderSubject):
    """
    This class is used to manage other Airfinder SiteUsers,
    given the User has Admin-level permissions.
    """
    subject_name = 'SiteUser'

    SITE_USER_PERMISSIONS = {
        "Admin": False,
        "Status": True,
        "AddTags": True,
        "EditDeleteTags": True,
        "EditDeleteGroupsCategories": False
    }

    ###########################################################################
    # Methods
    ###########################################################################

    def forgot_password(self):
        """ Sends the site user an email to reset their password. """
        url = ''.join([self._af_network_asset_url, 'users/forgotPassword'])
        params = {'email': self.email}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def resend_email(self):
        """ Resends the site user an email to reset their password. """
        url = ''.join([self._af_network_asset_url, 'users/resend'])
        params = {'email': self.email}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def role(self):
        return self._md.get("role")

    @property
    def can_add_tags(self):
        """ Can the SiteUser add tags? """
        return self._make_prop(bool, 'AddTags')

    @property
    def is_admin(self):
        """ Is the SiteUser an Admin? """
        return self._make_prop(bool, 'Admin')

    @property
    def can_edit_delete_groups_categories(self):
        """ Can the SiteUser Edit/Delete Groups and Categories? """
        return self._make_prop(bool, 'EditDeleteGroupsCategories')

    @property
    def can_edit_delete_tags(self):
        """ Can the SiteUser Edit/Delete tags? """
        return self._make_prop(bool, 'EditDeleteTags')

    @property
    def email(self):
        """ The SiteUser's email address. """
        return self._md.get('email')

    @property
    def user_id(self):
        return self._md.get('userId')

    @property
    def site(self):
        return Site(self.session, self._md.get('siteId'))


class Site(AirfinderSubject):
    """ Represents an Airfinder Site. """
    subject_name = 'Site'

    ###########################################################################
    # Private Methods.
    ###########################################################################

    def _get_registered_asset_by_site(self, subject_name, subject_id, group_by=""):
        """ Gets a registered asset by site-id. """
        url = ''.join([self._af_network_asset_url, '/{}/{}/'.format(subject_name, subject_id)])
        params = {'siteId': self.subject_id, 'groupBy': group_by}
        return self._get(url, params)

    def _get_registered_assets_by_site(self, asset_name, group_by=""):
        """ Gets all the registered assets by site-id. """
        url = ''.join([self._af_network_asset_url, '/', asset_name])
        params = {'siteId': self.subject_id, 'groupBy': group_by}
        return self._get(url, params=params)

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def organization_id(self):
        return self._make_prop(str, "organizationId")

    ###########################################################################
    # Manage Site Details.
    ###########################################################################

    # TODO: Test
    def rename(self, name):
        """ Rename an existing site. """
        url = ''.join([self._af_network_asset_url, "/sites"])
        params = {'siteId': self.subject_id}
        updates = {
            "name": name,
        }
        self._data = self._put(url, params, updates)

    ###########################################################################
    # Manage Areas.
    ###########################################################################

    def create_area(self, name):
        """ Create an area as a part of this Site.
        Args:
            name (str): The name of the new Site.

        Returns:
            :class.`conductor.airfinder.site.Site`
        """
        url = ''.join([self._af_network_asset_url, "/area"])
        params = {'siteId': self.subject_id}
        return self._get(url, params)

    def get_area(self, area_id):
        """ Gets an area in a site.
        Args:
            area_id (str): The ID of the area to receive.

        Returns:
            :class.`conductor.airfinder.area.Area`
        """
        x = self._get_registered_asset_by_site('area', area_id)
        return Area(self.session, x.get('id'), self.instance, _data=x)

    def get_areas(self):
        """ Gets all the areas for a site. """
        return [Area(self.session, x.get('id'), self.instance, _data=x) for x
                in self._get_registered_assets_by_site("areas")]

    def delete_area(self, area_id):
        """ Delete an area. """
        url = ''.join([self._af_network_asset_url, "area"])
        params = {'siteId': self.subject_id}
        return self._delete(url, params)

    ###########################################################################
    # Manage Gateways
    ###########################################################################

    def add_gateway(self, gateway_id, area=None):
        """ Register a gateway to an Airfinder Site. """
        data = {
            "accountId": self._md.get('accountId'),
            "nodeAddress": gateway_id,
            "siteId": self.subject_id,
            "areaId": area
        }
        url = ''.join([self._af_network_asset_url, '/gateways'])
        return self._post(url, json=data)

    def get_gateway(self, gateway_id):
        """ Get a gateway by address """
        x = self._get_registered_assets_by_site('gateways', gateway_id)
        return Gateway(self.session, x.get('nodeAddress'), self.instance, _data=x)

    def get_gateways(self):
        """ Gets all gateway's from a Site.

        Returns:
            (list) of :class.`conductor.devices.gateway.Gateway`.
        """
        return [Gateway(self.session, x.get('nodeAddress'), self.instance,
                        _data=x) for x in
                self._get_registered_assets_by_site('gateways')]

    def get_gateways_by_status(self):
        """ Gets all gateway's from a Site, sorted by health - GREEN or RED.

        Returns:
            (dict) of :class.`conductor.devices.gateway.Gateway` sorted by
            GREEN (good) or RED (bad) health.
        """
        ret = {"GREEN": [], "RED": []}
        url = '{}/status/gateways'.format(self._af_network_asset_url)
        params = {'siteId': self.subject_id}
        data = self._get(url, params=params)
        for x in data:
            ret[x.get('health')].append(Gateway(self.session,
                                                x['node']['nodeAddress'],
                                                self.instance,
                                                x['node']))
        return ret

    # TODO
    def remove_gateway(self, gateway):
        """ """
        raise NotImplementedError

    ###########################################################################
    # Manage Acceess Points
    ###########################################################################

    def add_access_point(self, name, mac_addr=None, node_addr=None, area=None):
        """ """
        if not mac_addr and not node_addr:
            raise ValueError("Must define node or mac address!")

        data = {
            "accountId": self._md.get('accountId'),
            "macAddress": mac_addr if mac_addr else addr_to_mac(node_addr),
            "nodeAddress": node_addr if node_addr else mac_to_addr(mac_addr),
            "siteId": self.subject_id,
            "areaId": area,
            "name": name,
        }
        url = ''.join([self._af_network_asset_url, '/accesspoints'])
        return self._post(url, json=data)

    # TODO
    def get_access_point(self, mac):
        """ """
        raise NotImplementedError

    def get_access_points(self):
        """ """
        assets = self._get_registered_assets_by_site('accesspoints')
        aps = []
        for x in assets:
            subject_id = x['nodeAddress']
            cls = find_cls(AccessPoint, x['registrationToken'])
            if cls:
                aps.append(cls(session=self.session, subject_id=subject_id,
                               instance=self.instance, _data=x))
            else:
                LOG.error("{} {}".format(subject_id, x['registrationToken']))
                aps.append(AccessPoint(session=self.session,
                                       subject_id=subject_id,
                                       instance=self.instance,
                                       _data=x))
        return aps

    def get_access_points_by_status(self):
        """ """
        ret = {"GREEN": [], "RED": []}
        url = '{}/status/accessPoints'.format(self._af_network_asset_url)
        params = {'siteId': self.subject_id}
        data = self._get(url, params=params)
        for x in data:
            subject_id = x['node']['nodeAddress']
            cls = find_cls(AccessPoint, x['node']['registrationToken'])
            if cls:
                ret[x.get('health')].append(
                        cls(session=self.session, subject_id=subject_id,
                            instance=self.instance, _data=x['node']))
            else:
                ret[x.get('health')].append(
                        AccessPoint(session=self.session,
                                    subject_id=subject_id,
                                    instance=self.instance,
                                    _data=x['node']))
        return ret

    # TODO
    def remove_access_point(self, access_point):
        """ """
        raise NotImplementedError

    ###########################################################################
    # Manage Tags
    ###########################################################################

    def add_node(self, mac_id, field1="", field2="", category="", description=""):
        """ Adds a node in the site. """
        url = ''.join([self._af_network_asset_url, '/tags'])
        data = {
            "accountId": self._md.get('accountId'),
            "macAddress": mac_id.mac_address,
            "siteId": self.subject_id,
            "description": description,
            "categoryId": category,
            "field1": field1,
            "field2": field2,
        }
        print(data)
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    # TODO
    def bulk_add_nodes(self, file_path):
        """ Bulk-add nodes to an airfinder site. """
        raise NotImplementedError

    def get_node(self, mac_id):
        """ Gets a node in the site. """
        return self._get_registered_asset_by_site('tag', mac_id)

    def get_nodes(self):
        """ Gets all the nodes in a site. """
        nodes = []
        for x in self._get_registered_assets_by_site('tags', 'none'):
            subject_id = x.get('id') if 'id' in x else x.get('nodeAddress')
            obj = find_cls(Node, x['registrationToken'])
            if obj:
                nodes.append(obj(self.session, subject_id, self.instance, x))
            else:
                dev = x['assetInfo']['metadata']['props'].get('deviceType')
                LOG.error("No device conversion for {}".format(dev))
                nodes.append(Tag(self.session, subject_id, self.instance, x))
        return nodes

    def remove_node(self, mac_id):
        """ Remove a tag to an airfinder site. """
        url = ''.join([self._af_network_asset_url, '/tag'])
        data = {
            "nodeAddress": [
                str(mac_id)
            ],
            "siteId": self.subject_id
        }
        resp = self.session.delete(url, json=data)
        resp.raise_for_status()
        return resp.json()

    ###########################################################################
    # Manage Locations
    ###########################################################################

    def add_location(self, name, mac_addr=None, node_addr=None, area=None, zone=None):
        """ """
        if not mac_addr and not node_addr:
            raise ValueError("Must define node or mac address!")

        data = {
            "accountId": self._md.get('accountId'),
            "macAddress": mac_addr if mac_addr else addr_to_mac(node_addr),
            "nodeAddress": node_addr if node_addr else mac_to_addr(mac_addr),
            "siteId": self.subject_id,
            "areaId": area,
            "name": name,
        }
        url = ''.join([self._af_network_asset_url, '/locations'])
        return self._post(url, json=data)

    # TODO
    def bulk_add_locations(self, file_name):
        """ Bulk-add locations to a site. """
        raise NotImplementedError

    def get_locations(self):
        """ Gets all the locations in a site. """
        nodes = []
        for x in self._get_registered_assets_by_site('locations', 'none'):
            subject_id = x.get('id') if 'id' in x else x.get('nodeAddress')
            obj = find_cls(Location, x['registrationToken'])
            if obj:
                nodes.append(obj(self.session, subject_id, self.instance, x))
            else:
                dev = x['assetInfo']['metadata']['props'].get('deviceType')
                LOG.error("No device conversion for {}".format(dev))
                nodes.append(Location(self.session, subject_id, self.instance, x))
        return nodes

    def get_location(self, mac_id):
        """ Gets a location in the site. """
        return self._get_registered_asset_by_site('location', mac_id)

    # TODO: Test
    def remove_location(self, locations):
        """ Remove locations from a Site. """
        url = ''.join([self._af_network_asset_url, 'location'])
        data = {
            "nodeAddresses": [locations],
            "siteId": self.subject_id
        }
        resp = self.session.delete(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def get_locations_by_status(self):
        """ """
        ret = {"GREEN": [], "RED": []}
        url = '{}/status/locations'.format(self._af_network_asset_url)
        params = {'siteId': self.subject_id}
        data = self._get(url, params=params)
        for x in data:
            subject_id = x['node']['nodeAddress']
            obj = find_cls(Location, x['node']['registrationToken'])
            ret[x.get('health')].append(obj(self.session, subject_id,
                                            self.instance, x['node']))
        return ret

    ###########################################################################
    # Manage Site Users
    ###########################################################################

    # TODO
    def add_site_user(self, email):
        """ """
        raise NotImplementedError

    def get_site_user(self, site_user_id):
        """ Gets a site-user in a site. """
        x = self._get_registered_asset_by_site("user", site_user_id)
        return SiteUser(self.session, x.get('id'), _data=x)

    def get_site_users(self):
        """ Gets all the site-users, in the site. """
        return [SiteUser(self.session, x.get('id'), _data=x) for x in
                self._get_registered_assets_by_site('users')]

    # TODO
    def remove_site_user(self, email):
        raise NotImplementedError

    ###########################################################################
    # Status
    ###########################################################################

    def get_status(self):
        """ Returns the status of the Access Points, Location Beacons, and
        Gateways on the Site by providing the number of 'GREEN', operational
        and 'RED' non-operational units.

        Returns:
            (dict) json object.

        Example:
            ::
                [
                  {
                    "assetType": "LOCATION",
                    "totalCount": 153,
                    "healthStatusCount": {
                      "GREEN": 151,
                      "RED": 2
                    }
                  },
                  {
                    "assetType": "ACCESS_POINT",
                    "totalCount": 95,
                    "healthStatusCount": {
                      "GREEN": 92,
                      "RED": 3
                    }
                  },
                  {
                    "assetType": "GATEWAY",
                    "totalCount": 3,
                    "healthStatusCount": {
                      "GREEN": 2,
                      "RED": 1
                    }
                  }
                ]
        """
        url = '{}/status'.format(self._af_network_asset_url)
        params = {'siteId': self.subject_id}
        return self._get(url, params=params)

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def area_count(self):
        """ Returns the number of Areas within the Site. """
        val = self._md.get('areaCount')
        return int(val) if val else None
