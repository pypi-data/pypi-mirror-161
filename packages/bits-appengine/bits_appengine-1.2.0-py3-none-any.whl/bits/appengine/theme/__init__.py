# -*- coding: utf-8 -*-
"""Theme class file."""
import datetime
import jinja2
import os
import platform
import sys

from google.cloud import firestore
from flask import redirect, request


class Theme(object):
    """Theme class."""

    def __init__(
            self,
            appengine,
            app_name=None,
            links=None,
            repo=None,
            analytics_tag=None,
            body_class="container",
            extended_footer=None,
            topnav_padding=False,
    ):
        """Initialize a class instance."""
        self.appengine = appengine
        self.app_name = app_name
        self.links = links
        self.repo = repo

        path = '{}/templates'.format(os.path.dirname(os.path.abspath(__file__)))
        self.jinja = jinja2.Environment(
            loader=jinja2.FileSystemLoader(path),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True
        )

        self.analytics_tag = analytics_tag
        self.body_class = body_class
        self.extended_footer = extended_footer
        self.topnav_padding = topnav_padding

        self.now = datetime.datetime.utcnow()
        self.user = self.appengine.user

    def _get_person(self, email):
        """Return a person record from firestore."""
        # get person based on email address
        client = firestore.Client(project=self.appengine.people_project)
        query = client.collection(self.appengine.people_collection).where('emails', 'array_contains', email)
        try:
            results = list(query.stream())
        except Exception as e:
            print(type(e))
            print(e)
            raise e
        if len(results) == 1:
            return results[0].to_dict()
        return {}

    def render_footer(self, repo=None):
        """Render the footer for the main template."""
        major, minor, _ = platform.python_version_tuple()
        version = f"{major}.{minor}"
        template = self.jinja.get_template('footer.html')
        return template.render(
            analytics_tag=self.analytics_tag,
            now=self.now,
            repo=self.repo,
            version=version,
        )

    def render_header(self, page_name=None):
        """Render the header for the main template."""
        template = self.jinja.get_template('header.html')
        return template.render(
            app_name=self.app_name,
            page_name=page_name,
            request=request,
        )

    def render_theme(self, body, page_name=None):
        """Render the main template theme."""
        header = self.render_header(page_name=page_name)
        topnav = self.render_topnav()
        footer = self.render_footer()

        template = self.jinja.get_template('theme.html')
        return template.render(
            # html content
            header=header,
            topnav=topnav,
            body=body,
            footer=footer,
            body_class=self.body_class,
            extended_footer=self.extended_footer,

            # user information
            is_admin=self.user().admin,
            is_dev=self.user().is_dev(),
            user=self.user(),
        )

    def render_topnav(self, repo=None):
        """Render the topnav for the main template."""
        template = self.jinja.get_template('topnav.html')
        if self.topnav_padding:
            topnav_padding = "navbar-fixed-top"
        else:
            topnav_padding = "fixed-top"

        return template.render(
            app_name=self.app_name,
            is_dev=self.user().is_dev(),
            links=self.links,
            request=request,
            user=self.user(),
            topnav_padding=topnav_padding
        )

    # @app.route('/admin/users')
    def admin_users_page(self, page_name=None):
        """Return the admin users page."""
        email = self.user().email
        if not self.user().is_admin():
            print('Unauthorized user visited admin users page: {}'.format(email))
            return redirect('/')
        print('User visited the admin users page: {}'.format(email))

        users = self.user().get_users()

        template = self.jinja.get_template('users.html')
        body = template.render(
            app_name=self.app_name,
            is_dev=self.user().is_dev(),
            users=users,
            user=self.user(),
        )
        return self.render_theme(body, page_name=page_name)

    def admin_users_add_page(self, page_name=None):
        """Return the admin user add page."""
        email = self.user().email
        if not self.user().is_admin():
            print('Unauthorized user visited admin users add page: {}'.format(
                email,
            ))
            return redirect('/')
        print('User visited the admin users add page: {}'.format(email))
        template = self.jinja.get_template('user.html')
        body = template.render(
            type="add",
            user={},
        )
        return self.render_theme(body, page_name=page_name)

    def admin_users_add_user(self):
        """Return the admin user add page."""
        email = self.user().email
        if not self.user().is_admin():
            print('Unauthorized user visited admin users add user: {}'.format(
                email,
            ))
            return redirect('/')
        user_email = request.form.get('email')

        # get person from bitsdb firestore
        person = self._get_person(user_email)

        # get google user_id
        user_id = person.get('google_id')

        # get admin status
        admin = False
        if request.form.get('admin') == 'True':
            admin = True

        # create user record
        user = {'admin': admin, 'email': user_email, 'id': user_id}

        # save user
        self.user().save_user(user)

        print('User {} updated a new user: {} [{}] admin: {}'.format(
            email,
            user_email,
            user_id,
            admin,
        ))
        return redirect('/admin/users')

    # @app.route('/admin/users/<google_id>')
    def admin_users_edit_page(self, google_id, page_name=None):
        """Return the admin user edit page."""
        email = self.user().email
        if not self.user().is_admin():
            print('Unauthorized user visited admin users edit page: {}'.format(
                email,
            ))
            return redirect('/')
        print('User visited the admin users edit page: {}'.format(email))
        user = self.user().get_user(google_id)
        template = self.jinja.get_template('user.html')
        body = template.render(
            google_id=google_id,
            type='edit',
            user=user,
        )
        return self.render_theme(body, page_name=page_name)

    def admin_users_edit_user(self, google_id):
        """Return the admin user edit page."""
        email = self.user().email
        if not self.user().is_admin():
            print('Unauthorized user visited admin users edit user: {}'.format(
                email,
            ), file=sys.stderr)
            return redirect('/')
        user_id, user_email = request.form.get('user').split(':')
        admin = False
        if request.form.get('admin') == 'True':
            admin = True
        user = {'admin': admin, 'email': user_email, 'id': user_id}
        self.user().save_user(user)
        print('User {} updated a new user: {} [{}] admin: {}'.format(
            email,
            user_email,
            user_id,
            admin,
        ))
        return redirect('/admin/users')

    def admin_users_delete(self, google_id):
        """Delete a user and redirect t ousers page.."""
        if not self.user().is_admin():
            return redirect('/')
        self.user().delete_user(google_id)
        return redirect('/admin/users')
