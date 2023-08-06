# -*- coding: utf-8 -*-
"""Example class file."""

from bits.appengine.config import Config
from bits.appengine.user import User


class AppEngine(object):
    """AppEngine class."""

    def __init__(
        self,
        config_collection='settings',
        config_database='firestore',
        config_project=None,
        debug_user=None,
        people_collection='people_people',
        people_project='broad-bitsdb-firestore',
        user_collection='users',
        user_database='firestore',
        user_project=None,
    ):
        """Initialize an Example class instance."""
        self.config_collection = config_collection
        self.config_database = config_database
        self.config_project = config_project
        self.debug_user = debug_user
        self.people_collection = people_collection
        self.people_project = people_project
        self.user_collection = user_collection
        self.user_database = user_database
        self.user_project = user_project

    def config(self):
        """Return a Config instance."""
        return Config(
            appengine=self,
            collection=self.config_collection,
            database=self.config_database,
            project=self.config_project,
        )

    def user(self):
        """Return a User instance."""
        return User(
            appengine=self,
            collection=self.user_collection,
            database=self.user_database,
            debug_user=self.debug_user,
            project=self.user_project,
        )
