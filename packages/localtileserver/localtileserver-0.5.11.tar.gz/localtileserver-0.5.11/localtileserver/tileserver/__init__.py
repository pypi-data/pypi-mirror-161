# flake8: noqa: F401
from flask import Flask
from flask_cors import CORS

from localtileserver.tileserver import rest, urls, views
from localtileserver.tileserver.blueprint import cache, tileserver
from localtileserver.tileserver.data import (
    get_building_docs,
    get_co_elevation_url,
    get_data_path,
    get_elevation_us_url,
    get_oam2_url,
    get_pine_gulch_url,
    get_sf_bay_url,
    str_to_bool,
)
from localtileserver.tileserver.palettes import get_palettes, palette_valid_or_raise
from localtileserver.tileserver.utilities import (
    get_cache_dir,
    get_clean_filename,
    make_vsi,
    purge_cache,
)


def create_app(url_prefix: str = "/", cors_all: bool = False):
    try:
        from localtileserver.tileserver import sentry
    except ImportError:
        pass
    app = Flask(__name__)
    if cors_all:
        cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)
    app.register_blueprint(tileserver, url_prefix=url_prefix)
    app.config.JSONIFY_PRETTYPRINT_REGULAR = True
    app.config.SWAGGER_UI_DOC_EXPANSION = "list"
    return app
