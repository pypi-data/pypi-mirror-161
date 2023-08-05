import pytz
import dateutil.parser
from datetime import datetime
from dateutil.tz import tzutc
from dateutil.tz import tzlocal


def from_iso8601(when=None, tz=pytz.timezone("UTC")):
  _when = dateutil.parser.parse(when)
  if not _when.tzinfo:
    _when = tz.localize(_when)
  if (str(_when.tzinfo) != 'tzutc()'):
    if (str(_when.tzinfo) == 'tzlocal()'):
      #if the local time is UTC convert it
      if tzutc().utcoffset(datetime.now()) == tzlocal().utcoffset(datetime.now()):
        return _when.replace(tzinfo = tzutc())
      else:
        raise Exception('Error - Only conversion of utc times from iso8601 is supported (Local time returned but not equlivant offset to UTC)')
    else:
      raise Exception('Error - Only conversion of utc times from iso8601 is supported')
  return _when


