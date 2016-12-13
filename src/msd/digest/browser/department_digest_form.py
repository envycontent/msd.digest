from datetime import datetime, timedelta
from itertools import groupby
import arrow

from zope.interface import Interface
from zope.schema import TextLine
from zope.schema import Date
from zope.schema import Choice
from zope.schema import List
from zope.i18nmessageid import MessageFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

_ = MessageFactory('department_digest')

from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form, field

import plone.app.z3cform
import plone.z3cform.templates

import requests

class ITableRowSchema(Interface):
    searchParam = Choice(title=u"Search on",
                 required=False,
                 values=("organising_department","list","topic","series"))
    searchValue = TextLine(title=u"Search for",
                   required=False)

class IDepartmentDigestForm(Interface):


    digestTitle = TextLine(
        title=_(u"Title of the Digest"),
        description=_(u"e.g. Medical Sciences Division What's On"),
            )

    dateFrom = Date(
        title=_(u"Start Date"),
        required=False,
            )

    dateTo = Date(
        title=_(u"End Date"),
        required=False
            )

    searchFor = List(title=u"Search",
        value_type=DictRow(title=u"Parameters", schema=ITableRowSchema))

class DepartmentDigestForm(form.Form):

    fields = field.Fields(IDepartmentDigestForm)
    fields['searchFor'].widgetFactory = DataGridFieldFactory

    ignoreContext = True

    output = None

    def updateWidgets(self):
        super(DepartmentDigestForm, self).updateWidgets()

    @button.buttonAndHandler(u'Make Digest')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        self.output = self.lookuptalks(data)
        self.getTitle = data['digestTitle']


        self.status = _(u"Report complete - nothing to report")


    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            "Your digest request was cancelled",
            'info')
        redirect_url = "%s/@@departmentdigest" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)

    def lookuptalks(self, data):

        results_set = []
        allItems = []
        params = {}

        #got to create the request string here
        paramsNum = len(data['searchFor'])
        params['from'] = data['dateFrom'].strftime('%Y-%m-%d')
        params['to'] = data['dateTo'].strftime('%Y-%m-%d')
        params['count'] = '500'

        for x in data['searchFor']:
            params[x['searchParam']]=x['searchValue']

        if 'list' in params.keys() and paramsNum == 1:
            request_string = "https://talks.ox.ac.uk/api/collections/id/%s" %(params['list'])
            talksfeed = self.getResults(request_string, params)

            if '_embedded' in talksfeed.keys():

                for talk in talksfeed['_embedded']['talks']:

                    results_set.append(talk)



        if 'list' not in params.keys():
            request_string = "https://talks.ox.ac.uk/api/talks/search"
            talksfeed = self.getResults(request_string, params)

            for talk in talksfeed['_embedded']['talks']:
                 results_set.append(talk)

        if 'list' in params.keys() and paramsNum > 1:
            request_string = "https://talks.ox.ac.uk/api/collections/id/%s" %(params['list'])
            talksfeed = self.getResults(request_string, params)

            if '_embedded' in talksfeed.keys():
                for talk in talksfeed['_embedded']['talks']:
                    results_set.append(talk)


            request_string = "https://talks.ox.ac.uk/api/talks/search"
            talksfeed = self.getResults(request_string, params)

            for talk in talksfeed['_embedded']['talks']:
                 results_set.append(talk)




        if results_set is not None:

            for x in results_set:
                description = x.get('description','')
                Title = x.get('title_display')
                if x.get('location_summary'):
                    venue = x.get('location_summary','')
                else:
                    venue = x.get('location_details','')
                if x.get('series'):
                    series_array = x.get('series','')
                    series = series_array.get('title','')
                    series_id = series_array.get('slug','')
                else:
                    series = ""
                    series_id = ""
                booking_url = x.get('booking_url','')
                talk_id = x.get('slug','')
                talk_link = 'http://talks.ox.ac.uk/talks/id/%s' % talk_id
                talk_ics = 'http://talks.ox.ac.uk/api/talks/%s.ics' % talk_id
                speakers_list = []
                speaker = ''

                for entry in x['_embedded']['speakers']:
                    speakers_list.append ((entry['name'] + ', ' + entry['bio']).rstrip(', '))
                
                various_speakers = x['_embedded'].get('various_speakers','')
                
                if various_speakers:
                    speaker = 'Various speakers'
                else:                    
                    speaker = '; '.join(speakers_list)

                status = x.get('status','')
                if status == 'cancelled':
                    cancelled = True
                else:
                    cancelled = False
                start_time = x.get('formatted_time','')
                start_date = x.get('start','')
                end_time = x.get('end','')
                special_message = x.get('special_message','')
                fm_startdate = arrow.get(start_date).format('dddd, D MMMM YYYY')
                fm_starttime = arrow.get(start_time,'HH:mm').format('h:mma')
                fm_endtime = arrow.get(end_time).format('h:mma')
                fm_startday = arrow.get(start_date).format('D')
                fm_startmonth = arrow.get(start_date).format('MMMM YYYY')


                allItems.append({'description': description,
                    'Title': Title,
                    'speaker': speaker,
                    'cancelled': cancelled,
                    'venue': venue,
                    'series': series,
                    'series_id': series_id,
                    'talk_id': talk_id,
                    'start_time': start_time,
                    'start_date': start_date,
                    'end_time': end_time,
                    'special_message': special_message,
                    'fm_startdate': fm_startdate,
                    'fm_starttime': fm_starttime,
                    'fm_startday': fm_startday,
                    'fm_startmonth': fm_startmonth,
                    'fm_endtime': fm_endtime,
                    'talk_link': talk_link,
                    'talk_ics': talk_ics,
                    'booking_url': booking_url,})


            allItems.sort(key=lambda x: x["start_date"], reverse=False)

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

DepartmentDigestFormView = plone.z3cform.layout.wrap_form(DepartmentDigestForm, index=FiveViewPageTemplateFile("templates/departmentdigest.pt"))
