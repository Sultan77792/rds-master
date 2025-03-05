from flask_caching import Cache
from app import app

cache = Cache(app)

@cache.memoize(timeout=3600)
def get_fire_statistics(region=None, start_date=None, end_date=None):
    from app.models.fire import Fire
    return Fire.get_statistics(region, start_date, end_date)

def clear_cache():
    cache.clear()