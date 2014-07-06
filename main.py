import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import datetime


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Person(ndb.Model):
	next_agenda = ndb.IntegerProperty()

class Task(ndb.Model):
	task_id = ndb.IntegerProperty()
	description = ndb.TextProperty()
	create_date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.write(template.render())

class Home(webapp2.RequestHandler):
    # Front page for those logged in

    def get(self):
        user = users.get_current_user()

        if user:  # signed in already

            parent_key = ndb.Key('Person', users.get_current_user().email())
            person = parent_key.get()

            query = ndb.gql("SELECT * FROM Task WHERE ANCESTOR IS :1 ORDER BY create_date ASC", parent_key)

            template_values = {
                'user_mail': users.get_current_user().email(),
                'agenda': query,
                'person': person,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('home.html')
            self.response.out.write(template.render(template_values))

        else:
            self.redirect(self.request.host_url)

class AddTask(webapp2.RequestHandler):
	def post(self):
		parent_key = ndb.Key('Person', users.get_current_user().email())
		person = parent_key.get()

		if person == None:
			person = Person(id=users.get_current_user().email())
			person.next_agenda = 1
			person.put()

		newtask = Task(parent=parent_key, id=str(person.next_agenda))
		newtask.task_id = person.next_agenda
		newtask.description = self.request.get('desc')

		person.next_agenda = person.next_agenda + 1
		newtask.put()
		person.put()
		self.redirect('/home')

class DeleteTask(webapp2.RequestHandler):
    def post(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()

        #del_task_key = ndb.Key('Task', str(self.request.get('id_to_delete')), parent=parent_key)
        #dt = del_task_key.get()
        dt = Task.get_by_id(id=str(self.request.get('id_to_delete')), parent=parent_key)
        #self.response.write(dt.key)
        dt.key.delete()

        person.put()
        self.redirect('/home')
        
		

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', Home),
    ('/addtask', AddTask),
    ('/delete', DeleteTask),
], debug=True)