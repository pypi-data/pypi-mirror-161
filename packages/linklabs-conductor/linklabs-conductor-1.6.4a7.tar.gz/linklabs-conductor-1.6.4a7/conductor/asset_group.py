from conductor.devices.module import Module
from conductor.subject import UplinkSubject, DownlinkSubject
from conductor.tokens import AppToken, NetToken


# TODO: Unit test functionality.
# TODO: Format Documenation.

class AssetGroup(UplinkSubject, DownlinkSubject):
    subject_name = 'assetGroup'

    @property
    def name(self):
        return self._data['name']

    @property
    def node_ids(self):
        ret = []
        nodes = self._data["nodes"]
        if not nodes:
            return ret
        for e in nodes:
            ret.append(e["desc"])
        return ret

    @property
    def app_token_ids(self):
        ret = []
        ats = self._data["applicationTokens"]
        if not ats:
            return ret
        for e in ats:
            ret.append(e["desc"])
        return ret

    @property
    def net_token_ids(self):
        ret = []
        nts = self._data["networkTokens"]
        if not nts:
            return ret
        for e in nts:
            ret.append(e["desc"])
        return ret

    def __repr__(self):
        return '{}({}: {})'.format(self.__class__.__name__, self.name, self)

    def __contains__(self, key):
        s_key = str(key)
        return s_key in self.node_ids or \
            s_key in self.app_token_ids or \
            s_key in self.net_token_ids

    def rename(self, new_name):
        """ Rename the user-friendly Asset Group Name.

        Args:
            new_name(str): The new name of the Asset Group.

        Returns:

        """
        url = '{}/{}/{}/{}'.format(self.network_asset_url,
                                   self.subject_name,
                                   self.subject_id,
                                   new_name)
        self._put(url)
        self.update_data()

    def add_node(self, node, name=None):
        """ Add a tag to the asset group.

        Args:
            node(:class:`.Module`): Conductor Address of a node or module.
            name(str): Optional description of node.
        """
        url = '{}/{}/{}/nodes'.format(self.network_asset_url,
                                      self.subject_name,
                                      self.subject_id)
        data = {
            "href": str(node),
            "desc": name
        }
        self._patch(url, json=data)
        self.update_data()

    def remove_node(self, node):
        """ Remove a tag from the Asset Group.

        Args:
            node(:class:`.Module`): Conductor Address of a node or module.
        """
        url = '{}/{}/{}/nodes'.format(self.network_asset_url,
                                      self.subject_name,
                                      self.subject_id)
        data = {
            "href": str(node),
            "desc": node
        }
        self._delete(url, json=data)
        self.update_data()

    def get_nodes(self):
        """ Get a list of tags in the asset group.

        """
        url = '{}/{}/{}/nodes'.format(self.network_asset_url,
                                      self.subject_name,
                                      self.subject_id)
        data = {'subjectId': self.subject_id}
        return [Module(self.session, x['desc'], _data=x)
                for x in self._get(url, json=data)]

    def get_application_tokens(self):
        """ Get the Application Tokens in the Asset Group.

        """
        url = '{}/{}/{}/applicationTokens'.format(self.network_asset_url,
                                                  self.subject_name,
                                                  self.subject_id)
        data = {'subjectId': self.subject_id}
        return [AppToken(self.session, x['desc'], _data=x)
                for x in self._get(url, json=data)]

    def add_application_token(self, appToken):
        """ Add an Application Token to the Asset Group.

        """
        url = '{}/{}/{}/applicationTokens'.format(self.network_asset_url,
                                                  self.subject_name,
                                                  self.subject_id)
        data = {
            "href": appToken,
            "desc": ""
        }
        self._patch(url, json=data)
        self.update_data()

    def remove_application_token(self, appToken):
        """ Remove an Application Token from the Asset Group.

        """
        url = '{}/{}/{}/applicationTokens'.format(self.network_asset_url,
                                                  self.subject_name,
                                                  self.subject_id)
        data = {
            "href": appToken,
            "desc": ""
        }
        self._delete(url, data)
        self.update_data()

    def get_network_tokens(self):
        """ Get the Network Tokens in the Asset Group.

        """
        url = '{}/{}/{}/nodes'.format(self.network_asset_url,
                                      self.subject_name,
                                      self.subject_id)
        data = {'subjectId': self.subject_id}
        return [NetToken(self.session, x['desc'], _data=x)
                for x in self._get(url, json=data)]

    def add_network_token(self, netToken):
        """ Add a Network Token in the Asset Group.

        """
        url = '{}/{}/{}/networkTokens'.format(self.network_asset_url,
                                              self.subject_name,
                                              self.subject_id)
        data = {
            "href": netToken,
            "desc": ""
        }
        self._patch(url, json=data)
        self.update_data()

    def remove_network_tokens(self, netToken):
        """ Remove a Network Token in the Asset Group.

        """
        url = '{}/{}/{}/networkTokens'.format(self.network_asset_url,
                                              self.subject_name,
                                              self.subject_id)
        data = {
            "href": netToken,
            "desc": ""
        }
        self._delete(url, json=data)
        self.update_data()
