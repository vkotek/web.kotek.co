from blueprints.lunchscraper.views import lunchScraper

from datetime import datetime
import dateutil.parser

@lunchScraper.context_processor
def datetime_processor():
    def pretty_datetime(dt):
        foo = dateutil.parser.parse(dt)
        return datetime.strftime( foo, '%Y-%m-%d %H:%M')
    return dict(pretty_datetime=pretty_datetime)
