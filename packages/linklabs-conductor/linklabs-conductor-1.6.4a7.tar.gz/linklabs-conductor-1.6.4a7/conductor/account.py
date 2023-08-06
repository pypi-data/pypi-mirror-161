# TODO: Format Documenation
# TODO: Unittest

import datetime
import logging

from collections import namedtuple
from getpass import getpass

import requests
import requests.auth

from conductor import PRODUCTION
from conductor.asset_group import AssetGroup
from conductor.devices.gateway import Gateway
from conductor.devices.lte_module import LTEmModule
from conductor.devices.module import Module
from conductor.subject import UplinkSubject, DownlinkMessage
from conductor.tokens import NetToken, AppToken
from conductor.util import parse_time, format_time, get_device_type, DeviceType

LOG = logging.getLogger(__name__)

AccountActivity = namedtuple('AccountActivity', ['count',
                                                 'last_seen_time',
                                                 'subject_id'])


class ConductorAccount(UplinkSubject):
    """ This class provides methods for interacting with Conductor for a
    particular account.

    This is the starting point for everything else in this module. Initialize
    with your username and password. If the password is omitted the initializer
    will prompt for one. Optionally provide the account name that you're trying
    to access (if you don't provide the account, the constructor will try to
    figure out which account is linked to your username).
    """

    subject_name = 'accountId'

    def __init__(self, username, instance=PRODUCTION, password=None,
                 account_name=None):
        pwd_prompt = "Conductor password for {} on {}:".format(username,
                                                               instance)
        password = password or getpass(pwd_prompt)
        self.session = requests.Session()
        self.session.auth = requests.auth.HTTPBasicAuth(username, password)
        self.instance = instance

        if account_name:
            # Find account ID for the account name, if given
            account = self._get('{}/accountName/{}'.format(self.access_url,
                                                           account_name))
        else:
            # Look up all the accounts associated with this user
            # and use the first one.
            accounts = self._get_accounts()
            LOG.debug("Got accounts: %s", accounts)
            if len(accounts) == 0:
                raise RuntimeError("No account associated with username")
#            elif len(accounts) > 1:
#                LOG.warning("More than one account associated with username")
            account = accounts[0]

        self.account_id = account['id']
        self.account_name = account['name']

        super(ConductorAccount, self).__init__(self.session, self.account_id,
                                               self.instance, _data=account)

    def __str__(self):
        return self.account_name

    ###########################################################################
    # Core Methods.
    ###########################################################################

    def _get_accounts(self):
        """ Gets the accounts associated with this username.

        Returns:
            a list of dictionaries.
        """
        return self._get(''.join([self.access_url, '/accounts']))

    def _get_registered_asset(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the
        Network Asset API.

        Returns:
            Json dictionary.
        """
        return self._get('{}/{}/{}'.format(self.network_asset_url,
                                           subject_name,
                                           subject_id))

    def _get_registered_assets(self, asset_name):
        """ Base function for getting list of registered assets from the
        Network Asset API.

        Returns:
            List of json dictionaries.
        """
        url = '{}/{}'.format(self.network_asset_url, asset_name)
        params = {'accountId': self.account_id, 'lifecycle': 'registered'}
        return self._get(url, params)

    ###########################################################################
    # Gateway Methods.
    ###########################################################################

    def register_gateway(self, gateway, network_token):
        """ Set the Network Token of the Gateway.

        Args:
            network_token (:class:`.NetToken`): The network token to set.
            owner (:class:`.Account`): The owner of the Gateway and Network
                Token.

        Raises:
            FailedAPICall: When the call fails.
        """
        url = '{}/gateways/register'.format(self.network_asset_url)

        if not isinstance(network_token, NetToken):
            network_token = self.get_network_token(network_token)

        data = {
          "account": {
            "href": self._href,
            "desc": ""
          },
          "token": {
            "href": network_token._href,
            "desc": ""
          },
          "nodeAddress": gateway.subject_id
        }
        self._post(url, json=data)

    def get_gateways(self):
        """ Gets all gateway's that the Airfinder Account has access to.

        Returns:
            List of :class:.`Gateway` objects.
        """
        return [Gateway(self.session, x['nodeAddress'], self.instance, _data=x)
                for x in self._get_registered_assets('gateways')]

    def get_gateway(self, gateway_addr):
        """ Opens a gateway by address.

        Returns:
            :class:.`Gateway` object.
        """
        asset = self._get_registered_asset('gateway', gateway_addr)
        return Gateway(self.session, gateway_addr, self.instance, _data=asset)

    ###########################################################################
    # Module (RLP/RXR) Methods.
    ###########################################################################
    def register_module(self, module_addr, app_token):
        """ Creates a Conductor instance of the LTE module. """
        url = '{}/modules/register'.format(self.network_asset_url)
        data = {
            "account": {
                "href": self.account_id,
                "desc": ""
            },
            "token": {
                "href": str(app_token),
                "desc": ""
            },
            "nodeAddress": module_addr
        }

        asset = self._post(url, json=data)
        return Module(self.session, module_addr, self.instance, _data=asset)

    def get_modules(self):
        """ Gets all modules registered to the Conductor Account.

        Returns:
            List of :class:`.Module`
        """
        def is_lte(addr):
            return get_device_type(addr) == DeviceType.MOD_LTE_M

        return [(LTEmModule if is_lte(x['nodeAddress'])
                else Module)(self.session,
                             x['nodeAddress'],
                             self.instance,
                             _data=x)
                for x in self._get_registered_assets('modules')]

    def get_module(self, module_addr):
        """ Gets a module by address.

        Args:
            module_addr(str): The address of the module to recieve.

        Returns:
            :class:'.Module' object """
        asset = self._get_registered_asset('module', module_addr)
        if get_device_type(module_addr) == DeviceType.MOD_LTE_M:
            return LTEmModule(self.session, module_addr,
                              self.instance, _data=asset)
        return Module(self.session, module_addr, self.instance, _data=asset)

    ###########################################################################
    # (LTEm CAT-M1) Module Methods.
    ###########################################################################

    def register_lte_module(self, imei, iccid, zipcode, app_token):
        """ Creates a Conductor instance of the LTE module. """
        url = '{}/lte/register'.format(self.network_asset_url)
        data = {
            "account": {
                "href": self.account_id,
                "desc": ""
            },
            "token": str(app_token),
            "iccId": str(iccid),
            "imei": imei,
            "zipCode": zipcode
        }
        params = {'accountId': self.account_id, 'lifecycle': 'registered'}
        asset = self._post(url, params, data)
        return LTEmModule(self.session, asset['nodeAddress'],
                          self.instance, _data=asset)

    ###########################################################################
    # Application Token Methods.
    ###########################################################################

    def create_application_token(self, name):
        """

        """
        raise NotImplementedError

    def get_application_tokens(self):
        """

        Returns:
            List of :class:`.AppToken` """
        return [AppToken(self.session, x['hash'], self.instance, _data=x)
                for x in self._get_registered_assets('applicationTokens')]

    def get_application_token(self, app_token_hash):
        """ Opens an application token object by hash.

        Returns:
            :class:`.AppToken` object.
        """
        asset = self._get_registered_asset('applicationToken', app_token_hash)
        return AppToken(self.session, app_token_hash,
                        self.instance, _data=asset)

    def delete_applicaiton_token(self, app_token_hash):
        """
        """
        raise NotImplementedError

    ###########################################################################
    # Network Token Methods.
    ###########################################################################

    def create_network_token(self, name):
        """ Creates a Network Token

        Args:
            name (str): The name of the new Network Token.

        Returns:
            :class:`.NetToken` representing the new Network Token.
        """
        raise NotImplementedError

    def get_network_tokens(self):
        """

        Returns:
            List of :class:`.NetToken`.
        """
        return [NetToken(self.session, x['hash'], self.instance, _data=x)
                for x in self._get_registered_assets('networkTokens')]

    def get_network_token(self, net_token_hash):
        """ Opens a network token object by hash.

        Args:
            net_token_hash(str): The Value of the Network Token Hash.

        Returns:
            A `NetToken` object.
        """
        asset = self._get_registered_asset('networkToken', net_token_hash)
        return NetToken(self.session, net_token_hash, _data=asset)

    def delete_network_token(self, network_token):
        """ """
        raise NotImplementedError

    ###########################################################################
    # Asset Group Methods.
    ###########################################################################

    def create_asset_group(self, name):
        """ Create a new Asset Group.

        Args:
            name(str): The name of the new Asset Group.

        Returns:
            Created :class:`.AssetGroup`.
        """
        url = '{}/assetGroups'.format(self.network_asset_url)
        data = {
            "account": {
                "href": self.account_id,
                "desc": ""
            },
            "assetGroupName": name
        }
        asset = self._post(url, json=data)
        return AssetGroup(self.session, asset['id'],
                          self.instance, _data=asset)

    def get_asset_groups(self):
        """

        Returns:
            List of :class:`.AssetGroup`.
        """
        return [AssetGroup(self.session, x['id'], self.instance, _data=x)
                for x in self._get_registered_assets('assetGroups')]

    def get_asset_group(self, asset_group_hash):
        """ Opens an Asset Group Object by hash.

        Returns:
            a 'AssetGroup' object.
        """
        asset = self._get_registered_asset('assetGroup', asset_group_hash)
        return AssetGroup(self.session, asset['id'],
                          self.instance, _data=asset)

    def delete_asset_group(self, asset_group):
        """ """
        raise NotImplementedError

    ###########################################################################
    # Other Useful Methods.
    ###########################################################################

    def get_downlink_message(self, issuance_id):
        """ Opens an issued command.

        Returns:
            a Downlink Message.
        """
        asset = self._get_registered_asset('issuedCommand', issuance_id)
        return DownlinkMessage(self.session, asset['hash'],
                               self.instance, _x=asset)

    def get_event_count(self, start, stop=None):
        """ Gets the event count for this account for the provided time range.

        Args:
            start(:class:`.datetime.datetime`): Start event time.
            stop(:class:`.datetime.datetime`): Optional end event time.

        Returns:
            A list of events by order of last seen time.
        """
        stop = stop or datetime.utcnow()
        url = '{}/activity/account/{}/{}/{}'.format(self.network_asset_url,
                                                    self.account_id,
                                                    format_time(stop),
                                                    format_time(start))
        filtered_data = [d for d in self._get(url) if d.get('lastSeenTime')]

        results = []
        for d in filtered_data:
            ts = d.get('lastSeenTime')
            res = AccountActivity(
                d.get('eventCount'),
                parse_time(ts) if ts else None,
                d.get('subjectId'))
            results.append(res)
        if results:
            return sorted(results, key=lambda e: e.last_seen_time)
        return None
