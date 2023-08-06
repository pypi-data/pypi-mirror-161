""" Represents an LTEm CAT M1 Module. """
from collections import namedtuple
from conductor.devices.module import Module
from conductor.subject import UplinkMessage
from conductor.util import Version


class LTEmModuleUplinkMessage(UplinkMessage):

    SignalData = namedtuple('SignalData', ['cell_id', 'cell_tac', 'rsrp',
                                           'rsrq', 'imei'])

    @property
    def signal_data(self):
        vals = self._data.get('value').get('avgSignalMetadata')
        return self.SignalData(int(vals.get('cellId')),
                               int(vals.get('cellTac')),
                               int(vals.get('cellRsrp')),
                               int(vals.get('cellRsrq')),
                               int(vals.get('imei')))

    @property
    def module(self):
        vals = self._data.get('value')
        return LTEmModule(self.session, vals.get('module'), self.instance)


# TODO: Format Documenation.


class LTEmModule(Module):
    """ Represents a single LTE-M Module (end node). """
    subject_name = 'lte'
    msgObj = LTEmModuleUplinkMessage

    def _post_status_update(self, status):
        """" Updates the status of an LTE module. """
        url = '{}/lte/{}/{}'.format(self.network_asset_url, self.subject_id,
                                    status)
        return self._post(url)

    def activate(self):
        """ Activate an LTE device. """
        return self._post_status_update('activate')

    def deactivate(self):
        """ Deactivate an LTE device. """
        return self._post_status_update('deactivate')

    def restore(self):
        """ Restore an LTE device. """
        return self._post_status_update('restore')

    def suspend(self):
        """ Suspend an LTE device. """
        return self._post_status_update('suspend')

    def prepare_fota(self, fw_type: str, version: str, filename: str, size: int, crc: int, fw_url: str):
        """ To send a Supertag FTP Notify message to an LTEm module, FOTA details must be sent to the device. """
        url = "{}/lte/fota/{}/node/{}".format(self.network_asset_url, fw_type, self.subject_id)
        return self._post(url, json={
            "type": fw_type,
            "version": version,
            "filename": filename,
            "size": size,
            "crc": crc,
            "url": fw_url
        })

    # NOTE: No support from backend.
    # def update_fota_details(self, fw_type: str, version: str, filename: str, size: int, crc: int, url: str):
    #     """ To send a Supertag FTP Notify message to an LTEm module, FOTA details must be sent to the device. """
    #     url = "{}/lte/fota/{}/node/{}".format(self.network_asset_url, fw_type, self.subject_id)
    #     return self._put(url, json={
    #         "type": fw_type,
    #         "version": version,
    #         "filename": filename,
    #         "size": size,
    #         "crc": crc,
    #         "url": url
    #     })

    def get_fota_details(self, fw_type: str):
        """ View FOTA details for a given firmware type. """
        url = "{}/lte/fota/{}/node/{}".format(self.network_asset_url, fw_type, self.subject_id)
        return self._get(url)

    def delete_fota_details(self, fw_type):
        url = "{}/lte/fota/{}/node/{}".format(self.network_asset_url, fw_type, self.subject_id)
        return self._delete(url)

    @property
    def cell_data_usage(self):
        """ Returns the cell data usage of the LTEm module. """
        val = self._md.get('cellDataUsage')
        return int(val) if val else None

    @property
    def last_cell_id(self):
        """ Returns the ID of the last cell tower the LTEm module transmitted
        through. """
        val = self._md.get('cellId')
        return int(val) if val else None

    @property
    def last_cell_tac(self):
        """ Returns the TAC of the last cell tower the LTEm module transmitted
        through. """
        val = self._md.get('cellTac')
        return int(val) if val else None

    @property
    def iccid(self):
        """ Returns the ICCID of the LTEm module. """
        val = self._md.get('iccid')
        return int(val) if val else None

    @property
    def imei(self):
        """ Returns the IMEI of the LTEm module. """
        val = self._md.get('imei')
        return int(val) if val else None

    @property
    def ip_address(self):
        """ Returns the IP Address of the LTEm module.  """
        val = self._md.get('ipAddress')
        return val

    @property
    def version(self):
        """ Returns the software version of the LTEm module. """
        val = self._md.get('sw_ver')
        return Version(int(val[2]), int(val[4]), int(val[6])) if val else None

    @property
    def modem_versions(self):
        """ Returns the Sequans versions of the LTEm module as a tuple. """
        val1 = self._md.get('lte_ver1')
        val2 = self._md.get('lte_ver2')
        return val1, val2

    @property
    def provisioned_status(self):
        """ Returns the provisioned status of the LTEm module. """
        val = self._md.get('lteProvStatus')
        return val

    @property
    def mdn(self):
        """ Returns the mdn of the LTEm module. """
        val = self._md.get('mdn')
        return int(val) if val else None

    @property
    def min(self):
        """ Returns the min of the LTEm module."""
        val = self._md.get('min')
        return int(val) if val else None

    @property
    def msisdn(self):
        """ Returns the msisdn of the LTEm module."""
        val = self._md.get('msisdn')
        return int(val) if val else None

    @property
    def last_slot(self):
        """ Returns the last slot of the LTEm module."""
        val = self._md.get('slot')
        return int(val) if val else None
