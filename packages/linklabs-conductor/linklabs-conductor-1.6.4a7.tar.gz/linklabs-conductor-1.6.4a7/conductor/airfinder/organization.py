""" Manages Airfinder Organizational Structures """

from conductor.airfinder.base import AirfinderSubject
from conductor.airfinder.site import Site, SiteUser


class Organization(AirfinderSubject):

    subject_name = "organization"

    @property
    def version(self):
        return NotImplementedError()

    @property
    def name(self):
        return self._make_prop(str, "name")

    @property
    def area_count(self):
        return self._make_prop(int, "areaCount")

    def _get_org_assets(self, asset_name):
        """ """
        url = '{}/{}/{}/{}'.format(self._af_network_asset_url, self.subject_name, self.subject_id, asset_name)
        return self._get(url)

    def get_users(self):
        """ """
        return [SiteUser(self.session, x.get('id'), self.instance, _data=x)
                for x in self._get_org_assets('users')]

    def get_sites(self):
        """ """
        return [Site(self.session, x.get('id'), self.instance, _data=x)
                for x in self._get_org_assets('sites')]
