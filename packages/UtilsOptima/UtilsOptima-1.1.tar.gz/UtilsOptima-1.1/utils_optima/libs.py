import warnings
from flask_sqlalchemy import SQLAlchemy as FSQLAlchemy

class SQLAlchemy(FSQLAlchemy):
    def apply_driver_hacks(self, app, sa_url, options):
        if not sa_url.drivername.startswith("mysql"):
            super().apply_driver_hacks(app, sa_url, options)
            return

        sa_url.query.setdefault('charset', 'utf8')
        unu = app.config['SQLALCHEMY_NATIVE_UNICODE']
        if unu is None:
            unu = self.use_native_unicode
        if not unu:
            options['use_native_unicode'] = False

        if app.config['SQLALCHEMY_NATIVE_UNICODE'] is not None:
            warnings.warn(
                "The 'SQLALCHEMY_NATIVE_UNICODE' config option is deprecated and will be removed in"
                " v3.0.  Use 'SQLALCHEMY_ENGINE_OPTIONS' instead.",
                DeprecationWarning
            )
        if not self.use_native_unicode:
            warnings.warn(
                "'use_native_unicode' is deprecated and will be removed in v3.0."
                "  Use the 'engine_options' parameter instead.",
                DeprecationWarning
            )
