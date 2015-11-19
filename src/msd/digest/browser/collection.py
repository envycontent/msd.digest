from datetime import datetime, timedelta
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from msd.digest import  _

# from urllib2 import *
import requests
# import json

class IoxtalksCollection(Interface):
    """
    oxtalks view interface
    """

    def test():
        """ test method"""


class oxtalksCollection(BrowserView):
    """
    oxtalks browser view
    """
    implements(IoxtalksCollection)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
         return self.context.Title


    def getResults(self, request_string):

        try:
            conn = requests.get(request_string, timeout=9)
        except requests.exceptions.ConnectionError:
            conn = None
        except requests.exceptions.Timeout:
            conn = None

        if conn is not None:
            rsp = conn.json()
        else:
            rsp = None

        return rsp

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def currententries(self):
        """
        test method
        """
        feeds = self.context['feeds']
        limitNum = self.context['limitNum']
        allItems = []
        results_set = []
        start_date = datetime.strptime('01/01/00','%d/%m/%y')
        end_date = datetime.strptime('01/01/30','%d/%m/%y')

        if 'start' in self.request:
            start_date = datetime.strptime(self.request['start'],'%d/%m/%y')
        if 'end' in self.request:
            end_date = datetime.strptime(self.request['end'],'%d/%m/%y') + timedelta(1)

        for item in feeds:
           talksfeed = self.getResults(item)
           for talk in talksfeed['_embedded']['talks']:

               talk_start_date = datetime.strptime(talk['start'],'%Y-%m-%dT%H:%M:%SZ')

               if start_date < talk_start_date < end_date:
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

        return allItems
