from osuca.model.analytics import Analytics
from pkg_resources import resource_string as resource_bytes
import requests

analytics = None

def init_app(data_source):
    global analytics  # declare as global to assign value
    reviews = None
    # Let's use the static file if there is no configuration parameter passed.
    if data_source is None:
        print('Using static data source.')
        reviews = resource_bytes('osuca.static', 'reviews.csv').decode('utf-8')
    else:
        reviews = requests.get(data_source)
        if reviews:
            print('Successfully retrieved %s.' % data_source)
        else:
            print('An error has occurred while retrieving %s.' % data_source)
    analytics = Analytics(reviews.text)
    get_db()

def get_db():
    return analytics
