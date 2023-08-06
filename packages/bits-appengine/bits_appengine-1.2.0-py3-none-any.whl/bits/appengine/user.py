# -*- coding: utf-8 -*-
"""App Engine User class file."""

import os
import logging
import sys

from flask import request
from google.cloud import datastore
from google.cloud import firestore


class User(object):
    """Uses class."""

    def __init__(
        self,
        appengine=None,
        collection='users',
        database='firestore',
        debug_user=None,
        project=None
    ):
        """Initialize a class instance."""
        self.appengine = appengine
        self.collection = collection
        self.database = database
        self.debug_user = debug_user
        self.project = project

        if self.database == 'datastore':
            self.client = datastore.Client(project=self.project)
        elif self.database == 'firestore':
            self.client = firestore.Client(project=self.project)
        else:
            logging.error('Unsupported database: {}'.format(self.database))
            sys.exit()

        self.admin = False
        self.email = None
        self.id = None

        # get the logged-in user
        if self.debug_user and self.is_dev():
            # get the debug user
            self.get_debug_user()
        else:
            # get the current logged-in user from headers
            self.get_current_user()

        # get stored user from the database
        self.stored_user = self.get_stored_user()

        # set user as a dict
        self.user = {'email': self.email, 'id': self.id}

    def __getitem__(self, key):
        """Return the value of the given attribute."""
        return self.__dict__[key]

    def __str__(self):
        """Return the string representation."""
        return 'User: {} [{}]'.format(self.email, self.id)

    def get(self, key):
        """Return the value of the given attribute."""
        return self.__getitem__(key)

    def get_current_user(self):
        """Return the current user."""
        # define headers
        user_email_header = 'x-goog-authenticated-user-email'
        user_id_header = 'x-goog-authenticated-user-id'

        # get Google IAP user's email and id from headers
        self.email = request.headers.get(user_email_header, '').replace('accounts.google.com:', '')
        self.id = request.headers.get(user_id_header, '').replace('accounts.google.com:', '')

    def get_debug_user(self):
        """Return the debug user."""
        self.email = self.debug_user.get('email')
        self.id = self.debug_user.get('id')

    def is_admin(self):
        """Return true if the user is an admin."""
        if self.admin:
            return True

    def is_dev(self):
        """Return true if we are in the dev environment."""
        if os.getenv('GAE_ENV', '').startswith('standard'):
            return False
        return True

    def role(self):
        """Return the user's role."""
        role = 'user'
        if self.is_admin():
            role = 'admin'
        return role

    #
    # Datastore Users
    #
    def delete_datastore_user(self, user_id):
        """Delete a user from datastore.."""
        client = datastore.Client(project=self.project)
        return client.key(self.collection, user_id).delete()

    def get_datastore_user(self, user_id):
        """Return the user info from datastore."""
        client = datastore.Client(project=self.project)
        return client.get(client.key(self.collection, user_id))

    def get_datastore_users(self):
        """Return a list of users from datastore."""
        client = datastore.Client(project=self.project)
        query = client.query(kind=self.collection)
        return list(query.fetch())

    def get_stored_datastore_user(self):
        """Return the user info from datastore."""
        if not self.id:
            return
        user = self.get_datastore_user(self.id)
        if user and user.get('admin'):
            self.admin = True
        return user

    def save_datastore_user(self, user):
        """Save a user in datastore."""
        client = datastore.Client(project=self.project)
        user_id = user.get('id')
        if not user_id:
            return
        key = client.key(self.collection, user_id)
        entity = datastore.Entity(key)
        entity.update(user)
        return client.put(entity)

    #
    # Firestore Users
    #
    def delete_firestore_user(self, user_id):
        """Delete a user from firestore."""
        client = firestore.Client(project=self.project)
        return client.collection(self.collection).document(user_id).delete()

    def get_firestore_user(self, user_id):
        """Return the user info from firestore."""
        client = firestore.Client(project=self.project)
        return client.collection(self.collection).document(user_id).get().to_dict()

    def get_firestore_users(self):
        """Return a list of users from firestore."""
        client = firestore.Client(project=self.project)
        users = []
        for doc in client.collection(self.collection).stream():
            user = doc.to_dict()
            if 'id' not in user:
                user['id'] = doc.id
            users.append(user)
        return users

    def get_stored_firestore_user(self):
        """Return the user info from firestore."""
        if not self.id:
            return
        user = self.get_firestore_user(self.id)
        if user and user.get('admin'):
            self.admin = True
        return user

    def save_firestore_user(self, user):
        """Save a user in firestore."""
        client = firestore.Client(project=self.project)
        user_id = user.get('id')
        if not user_id:
            return
        return client.collection(self.collection).document(user_id).set(user)

    #
    # Generic User Functions
    #
    def delete_user(self, user_id):
        """Delete a user from the database."""
        if self.database == 'firestore':
            return self.delete_firestore_user(user_id)
        elif self.database == 'datastore':
            return self.delete_datastore_user(user_id)

    def get_stored_user(self):
        """Return the user info from the database."""
        if self.database == 'firestore':
            return self.get_stored_firestore_user()
        elif self.database == 'datastore':
            return self.get_stored_datastore_user()

    def get_user(self, user_id):
        """Return the user info from the database."""
        if self.database == 'firestore':
            return self.get_firestore_user(user_id)
        elif self.database == 'datastore':
            return self.get_datastore_user(user_id)

    def get_users(self):
        """Return a list of users from the database."""
        if self.database == 'firestore':
            return self.get_firestore_users()
        elif self.database == 'datastore':
            return self.get_datastore_users()

    def save_user(self, user):
        """Save a user in the database."""
        if self.database == 'firestore':
            return self.save_firestore_user(user)
        elif self.database == 'datastore':
            return self.save_datastore_user(user)
