"""
trionyx.conf
~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import os
import importlib
import logging

logger = logging.getLogger(__name__)

ENVIRONMENT_VARIABLE = "XENOPS_SETTINGS"


class Settings:
    """Settings wrapper class"""

    def __init__(self):
        """Init setting and load settings from project"""
        self.IS_PROJECT = False
        self._settings = {}

        project_settings = os.environ.get(ENVIRONMENT_VARIABLE)
        if project_settings:
            self._settings = importlib.import_module(project_settings)
            self.IS_PROJECT = True

    def __getattr__(self, name):
        """Get setting value"""
        if hasattr(self._settings, name):
            return getattr(self._settings, name, None)

    def get(self, key, default=None):
        """
        Get settings with default

        :param str key:
        :param default:
        :return:
        """
        if hasattr(self._settings, key):
            return getattr(self._settings, key, None)
        return default


settings = Settings()
