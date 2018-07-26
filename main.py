import webapp2
import jinja2
import os
import logging
import time

from google.appengine.ext import ndb
from google.appengine.api import users

class Person(ndb.Model):
    name = ndb.StringProperty()
    biography = ndb.StringProperty()
    birthday = ndb.DateProperty()
    email = ndb.StringProperty()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        #1. read the request
        current_user = users.get_current_user()

        #2. read and write from the database
        people = Person.query().fetch()
        if current_user:
            current_email = current_user.email()
            current_person = Person.query().filter(Person.email == current_email).get()
        else:
            current_person = None

        #3. render a response

        logout_url = users.create_logout_url('/')

        login_url = users.create_login_url('/')

        templateVars = {
            'people': people,
            'current_user': current_user,
            'login_url': login_url,
            'logout_url': logout_url,
            'current_person': current_person,
        }
        template = env.get_template('/templates/home.html')
        self.response.write(template.render(templateVars))

class Profile(webapp2.RequestHandler):
    def get(self):
        #1. get info from the request
        urlsafe_key = self.request.get('key')

        #2. read or write from the database
        key = ndb.Key(urlsafe=urlsafe_key)
        person = key.get()

        #3. render a response
        templateVars = {
            'person': person,
        }
        template = env.get_template('/templates/profile.html')
        self.response.write(template.render(templateVars))


class Create(webapp2.RequestHandler):
    def post(self):
        #1. get info from the request
        name = self.request.get('name')
        biography = self.request.get('biography')
        current_user = users.get_current_user()
        email = current_user.email()

        #2. read or write from the database
        person = Person(name=name, biography=biography, email=email)
        person.put()

        #3. render a response
        time.sleep(2)
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/profile', Profile),
    ('/create', Create),


], debug=True)
