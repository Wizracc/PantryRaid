# Configuration settings, e.g. database login and environment variables to set
import os


class Config(object):
    """Class to hold configuration details for the deployed application.

    Attributes
    ----------
    TESTING : bool
        Indicates whether this configuration is used for testing.

    CONNECTION_URL : string
        MongoDB URI used to connect to the database. Should include authentication details if applicable.

    SECRET_KEY : string
        Secret key to prevent CSRF.
    """
    TESTING = False
    CONNECTION_URL = os.environ['MONGODB_PROD']
    SECRET_KEY = os.environ['PANTRY_KEY']


class TestConfig(object):
    """Class to hold configuration details for testing the application.
    To ensure a stable testing environment, a static test database might be
    used, rather than the production database.

    Attributes
    ----------
    TESTING : bool
        Indicates whether this configuration is used for testing.

    CONNECTION_URL : string
        MongoDB URI used to connect to the database. Should include authentication details if applicable.

    SECRET_KEY : string
        Secret key to prevent CSRF.
    """
    TESTING = True
    CONNECTION_URL = os.environ['MONGODB_TEST']
    SECRET_KEY = os.environ['PANTRY_KEY']
    WTF_CSRF_METHODS = []
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
