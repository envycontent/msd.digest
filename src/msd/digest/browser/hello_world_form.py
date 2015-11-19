from datetime import datetime, timedelta
from itertools import groupby

from zope.interface import Interface
from zope.schema import TextLine
from zope.schema import Date
from zope.i18nmessageid import MessageFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile

_ = MessageFactory('hello_world')

from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form, field

import plone.app.z3cform
import plone.z3cform.templates

import requests


class IHelloWorldForm(Interface):

    hello_world_name = TextLine(
        title=_(u'Name'),
        description=_(u'Please enter your name.'),
        required=False)

    digestTitle = TextLine(
        title=_(u"Title of the Digest"),
            )

    dateFrom = Date(
        title=_(u"Start Date"),
        required=False,
            )

    dateTo = Date(
        title=_(u"End Date"),
        required=False
            )

    department = TextLine(
        title=_(u"OxPoints Department Code"),
            )

class HelloWorldForm(form.Form):

    fields = field.Fields(IHelloWorldForm)
    ignoreContext = True

    output = None

    def updateWidgets(self):
        super(HelloWorldForm, self).updateWidgets()

    @button.buttonAndHandler(u'Make Digest')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        self.output = self.lookuptalks(data)


        self.status = _(u"Report complete")


    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            "Hello No One",
            'info')
        redirect_url = "%s/@@hello_world_form" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)

    def lookuptalks(self, data):

        #got to create the request string here

        request_string = "https://talks.ox.ac.uk/api/talks/search"
        start = data['dateFrom'].strftime('%d/%m/%y')
        end = data['dateTo'].strftime('%d/%m/%y')
        organising_department = data['department']
        params = {'from':start, 'to':end, 'organising_department':organising_department, 'count':'500'}


        talksfeed = self.getResults(request_string, params)
        results_set = []
        allItems = []


        for talk in talksfeed['_embedded']['talks']:
             results_set.append(talk)

        if results_set is not None:

            for x in results_set:
                description = x.get('description','')
                Title = x.get('title_display')
                if x.get('location_summary'):
                    venue = x.get('location_summary','')
                else:
                    venue = ""
                if x.get('series'):
                    series_array = x.get('series','')
                    series = series_array.get('title','')
                    series_id = series_array.get('slug','')
                else:
                    series = ""
                talk_id = x.get('slug','')
                talk_link = 'http://new.talks.ox.ac.uk/talks/id/%s' % talk_id
                talk_ics = 'http://new.talks.ox.ac.uk/api/talks/%s.ics' % talk_id
                speakers_list = []
                speaker = ''

                for entry in x['_embedded']['speakers']:
                    speakers_list.append ((entry['name'] + ', ' + entry['bio']).rstrip(', '))

                speaker = '; '.join(speakers_list)

                start_time = x.get('start','')
                end_time = x.get('end','')
                special_message = x.get('special_message','')
                fm_startdate = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ').strftime('%A, %d %B %Y').replace(', 0',', ')
                fm_starttime = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ').strftime('%I:%M%p').strip('0').replace(':00','').lower()
                fm_endtime = datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%SZ').strftime('%I:%M%p').strip('0')
                fm_startday = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ').strftime('%d').lstrip('0')
                fm_startmonth = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ').strftime('%B %Y')


                allItems.append({'description': description,
                    'Title': Title,
                    'speaker': speaker,
                    'venue': venue,
                    'series': series,
                    'series_id': series_id,
                    'talk_id': talk_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'special_message': special_message,
                    'fm_startdate': fm_startdate,
                    'fm_starttime': fm_starttime,
                    'fm_startday': fm_startday,
                    'fm_startmonth': fm_startmonth,
                    'fm_endtime': fm_endtime,
                    'talk_link': talk_link,
                    'talk_ics': talk_ics,})


            allItems.sort(key=lambda x: x["start_time"], reverse=False)

            groupedItems = [{'startdate': name, 'talkslist': list(group)} for name, group in groupby(allItems, lambda p:p['fm_startdate'])]


        return groupedItems


    def getResults(self, request_string, params):

        try:
            conn = requests.get(request_string, params, timeout=9)
        except requests.exceptions.ConnectionError:
            conn = None
        except requests.exceptions.Timeout:
            conn = None

        if conn is not None:
            rsp = conn.json()
        else:
            rsp = None

        return rsp

HelloWorldFormView = plone.z3cform.layout.wrap_form(HelloWorldForm, index=FiveViewPageTemplateFile("templates/helloworld.pt"))
