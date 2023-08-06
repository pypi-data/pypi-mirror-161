# TODO: Documentation format.
# TODO: See what other functionality can be added.

import logging

from datetime import datetime, timedelta
from collections import namedtuple

from conductor.subject import ConductorSubject
from conductor.util import format_time, parse_time

LOG = logging.getLogger(__name__)


EventRollup = namedtuple('EventRollup', ['count', 'start_time'])


class EventCount(ConductorSubject):
    """ A class for getting event counts for a subset of uplink subjects """

    rollup_params = ['yearly', 'monthly', 'daily', 'hourly', '5minute', '1minute']
    event_type = 'uplinkPayload'

    def get_event_count_time_range(self, start, stop=None):
        """
        Gets a count of messages within a start and stop time.

        The `start` and `stop` arguments must be `datetime.datetime` objects.
        If `stop` is `None`, then the current time will be used.

        Returns an integer count of uplinkPayload events.
        """
        stop = stop or datetime.utcnow()
        url = '{}/activity/{}/{}/{}'.format(self.network_asset_url, self.subject_id,
                                            format_time(stop), format_time(start))

        data = self._get(url)

        event_count = data.get('eventCount')
        return event_count

    def get_recent_event_count(self, mins_back):
        """ Returns the count of messages received in the last `mins_back` minutes. """
        now = datetime.utcnow()
        return self.get_event_count_time_range(now - timedelta(minutes=mins_back))

    def get_event_count_rollup(self, start, stop=None, rollup='hourly'):
        """
        Gets a rolled-up count of events for the provided time frame and interval.
        :param start: start time datetime object
        :param stop: stop time datetime object
        :param rollup: rollup interval
        :return: list of EventRollup namedtuples
        """
        stop = stop or datetime.utcnow()
        url = '{}/activity/{}/{}/{}/{}/rollup?rollup={}'.format(self.network_asset_url, self.subject_id,
                                                                self.event_type, format_time(stop), format_time(start),
                                                                rollup)

        if rollup not in self.rollup_params:
            raise ValueError('{} is not a valid rollup interval, should be one of {}'.format(
                rollup, self.rollup_params
            ))

        data = self._get(url)

        results = []
        for d in data:
            ts = d.get('description')
            results.append(EventRollup(d.get('eventCount'), parse_time(ts) if ts else None))
        if results:
            return sorted(results, key=lambda e: e.start_time)
        return None
