import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import datetime


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Person(ndb.Model):
	next_agenda = ndb.IntegerProperty()


class Task(ndb.Model):
    task_id = ndb.IntegerProperty()
    title = ndb.StringProperty()
    description = ndb.TextProperty()
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    priority = ndb.IntegerProperty(default=2) # 1 = high, 2 = medium, 3 = low
    due_date = ndb.DateTimeProperty()


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

            query = ndb.gql("SELECT * FROM Task WHERE ANCESTOR IS :1 AND priority <= 3 ORDER BY priority ASC, create_date ASC", parent_key)
            done_query = ndb.gql("SELECT * FROM Task WHERE ANCESTOR IS :1 AND priority > 3 ORDER BY priority ASC, create_date ASC", parent_key)

            template_values = {
            'user_mail': users.get_current_user().email(),
            'agenda': query,
            'done_query': done_query,
            'person': person,
            'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('home.html')
            self.response.out.write(template.render(template_values))

        else:
            self.redirect(self.request.host_url)



class AddTask(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        if user:  # signed in already

            template_values = {
            'user_mail': users.get_current_user().email(),
            'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('add_task.html')
            self.response.out.write(template.render(template_values))

        else:
            self.redirect(self.request.host_url)


    def post(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()

        if person == None:
            person = Person(id=users.get_current_user().email())
            person.next_agenda = 1
            person.put()

        newtask = Task(parent=parent_key, id=str(person.next_agenda))
        newtask.task_id = person.next_agenda
        newtask.title = self.request.get('title')
        newtask.description = self.request.get('desc')
        newtask.priority = int(self.request.get('priority'))

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


class EditTask(webapp2.RequestHandler):
    
    def get(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()
        task_to_edit = Task.get_by_id(id=str(self.request.get('id_to_edit')), parent=parent_key)
        #self.response.write(task_to_edit)

        template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'task_to_edit': task_to_edit,
        }

        template = jinja_environment.get_template('edit_task.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()
        task_to_edit = Task.get_by_id(id=str(self.request.get('id_to_edit')), parent=parent_key)
        #self.response.write(task_to_edit)

        task_to_edit.description = self.request.get('desc')
        task_to_edit.title = self.request.get('title')
        task_to_edit.priority = int(self.request.get('priority'))
        task_to_edit.put()
        person.put()
        self.redirect('/home')

class Done(webapp2.RequestHandler):
    def post(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()
        task_done = Task.get_by_id(id=str(self.request.get('id_done')), parent=parent_key)
        #self.response.write(task_done)

        task_done.priority = task_done.priority + 3
        task_done.put()
        person.put()
        self.redirect('/home')

class NotDone(webapp2.RequestHandler):
    def post(self):
        parent_key = ndb.Key('Person', users.get_current_user().email())
        person = parent_key.get()
        task_notdone = Task.get_by_id(id=str(self.request.get('id_notdone')), parent=parent_key)
        #self.response.write(parent_key) 
        
        task_notdone.priority = task_notdone.priority - 3
        task_notdone.put()
        person.put()
        self.redirect('/home')
        
        



application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', Home),
    ('/addtask', AddTask),
    ('/delete', DeleteTask),
    ('/edit', EditTask),
    ('/done', Done),
    ('/notdone', NotDone),
    ], debug=True)