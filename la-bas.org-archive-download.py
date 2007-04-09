#!/usr/bin/python

from datetime import date, timedelta
from commands import getstatusoutput as run


# Range to download
START_DATE = date(2001, 9, 3)
STOP_DATE  = date.today()
EXTENTION  = "ogg"             # = "mp3"


if __name__ == "__main__":

  def date2str(d):
    """
      Convert date to a "YYDDMM" string pattern.
    """
    return "%s%02d%02d" % (str(d.year)[-2:], d.month, d.day)

  # Download each day within the date range
  stop_date = int(date2str(STOP_DATE))
  current_date = START_DATE
  current_date_str = date2str(current_date)
  while int(current_date_str) <= stop_date:
    # Build media url
    media_url = "http://media.la-bas.org/mp3/%s/%s.%s" % (current_date_str, current_date_str, EXTENTION)
    # Check media existence
    (status, output) = run("wget --spider %s" % media_url)
    # Download it if exist
    if status == 0 and output.find("404 Not Found") == -1:
      run("wget --timestamping --continue --no-directories %s" % media_url)
      result = "DOWNLOADED"
    else:
      result = "   MISSING"

    print "%s - %s" % (result, media_url)

    # Go to next day
    current_date += timedelta(days=1)
    current_date_str = date2str(current_date)