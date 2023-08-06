import requests
from pkg_resources import resource_string as resource_bytes

from osuca.model.analytics import Analytics

analytics = None


def init_app(data_source):
    # Declare analytics as global to assign value to it later
    global analytics
    reviews = None
    # Let's use the static file if there is no configuration parameter passed.
    if data_source is None:
        print('Using static data source.')
        reviews = resource_bytes('osuca.static', 'reviews.csv').decode('utf-8')
        analytics = Analytics(reviews)
    else:
        reviews = requests.get(data_source)
        if reviews:
            print('Successfully retrieved %s.' % data_source)
        else:
            print('An error has occurred while retrieving %s.' % data_source)
        analytics = Analytics(reviews.text)

def get_db():
    return analytics