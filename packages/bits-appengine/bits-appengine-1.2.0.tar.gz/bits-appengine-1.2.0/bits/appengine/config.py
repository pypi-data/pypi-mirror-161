# -*- coding: utf-8 -*-
"""App Engine Config class file."""

import logging
from google.cloud import datastore
from google.cloud import firestore


class Config(object):
    """Config class."""

    def __init__(
        self,
        appengine=None,
        collection='settings',
        database='firestore',
        project=None,
    ):
        """Initialize a class instance."""
        self.appengine = appengine
        self.database = database
        self.collection = collection
        self.project = project

        # get the configuration settings from the database
        self.config = self.get_config()

    def get_config(self, name=None):
        """Return the configuration settings as a dict."""
        if self.database == 'firestore':
            return self.get_config_from_firestore(name=name)
        elif self.database == 'datastore':
            return self.get_config_from_datastore(name=name)
        else:
            logging.error('Unsupported database: {}'.format(self.database))
        return {}

    def get_config_from_datastore(self, name=None):
        """Return the config from Datatstore as a dict."""
        db = datastore.Client(project=self.project)
        config = {}
        for entity in db.query(kind=self.collection).fetch():
            key = entity.key.name
            config[key] = dict(entity)
        if name:
            return config.get(name, {})
        return config

    def get_config_from_firestore(self, name=None):
        """Return the config from Firestore as a dict."""
        db = firestore.Client(project=self.project)
        config = {}
        for doc in db.collection('settings').stream():
            config[doc.id] = doc.to_dict()
        if name:
            return config.get(name, {})
        return config
