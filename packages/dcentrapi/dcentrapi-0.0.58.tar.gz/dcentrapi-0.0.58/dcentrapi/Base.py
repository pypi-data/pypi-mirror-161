from dcentrapi.common import get_dapi_version


class Base:

    def __init__(self, stage, username, key):
        self.username = username
        self.key = key
        self.headers = {'X-API-KEY': self.key}
        self.__version__ = get_dapi_version()

        if stage == 'develop':
            self.url = "https://test-api.dcentralab.com/"
        if stage == 'staging':
            self.url = "https://staging.dcentralab.com/"
        if stage == 'main':
            self.url = "https://api.dcentralab.com/"
