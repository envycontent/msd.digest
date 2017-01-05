from datetime import datetime, timedelta
from zope.interface import implements, Interface
from itertools import groupby
import arrow


from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


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
        self.request.response.setHeader('X-Frame-Options', 'ALLOWALL')
        
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def testcurrententries(self):

        results_set = []
        allItems = []
        params = self.request.form

        #got to create the request string here

        params['from'] = datetime.today().strftime('%Y-%m-%d')
        params['to'] = '2018-12-30'


        if 'list' in params.keys():
            request_string = "https://new.talks.ox.ac.uk/api/collections/id/%s" %(params['list'])
            talksfeed = self.getResults(request_string, params)

            if '_embedded' in talksfeed.keys():

                for talk in talksfeed['_embedded']['talks']:

                    results_set.append(talk)


        request_string = "https://new.talks.ox.ac.uk/api/talks/search"
        talksfeed = self.getResults(request_string, params)

        for talk in talksfeed['_embedded']['talks']:
             results_set.append(talk)


        if results_set is not None:
            
            return "success"


    def currententries(self):

        results_set = []
        allItems = []
        params = self.request.form

        #got to create the request string here
        
        params['from'] = datetime.today().strftime('%Y-%m-%d')
        params['to'] = '2018-12-30'
        

        if 'list' in params.keys():
            request_string = "https://new.talks.ox.ac.uk/api/collections/id/%s" %(params['list'])
            talksfeed = self.getResults(request_string, params)

            if '_embedded' in talksfeed.keys():

                for talk in talksfeed['_embedded']['talks']:

                    results_set.append(talk)

        if 'organising_department' in params.keys():

            request_string = "https://new.talks.ox.ac.uk/api/talks/search"
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
                    venue = ""
                if x.get('series'):
                    series_array = x.get('series','')
                    series = series_array.get('title','')
                    series_id = series_array.get('slug','')
                else:
                    series = ""
                    series_id = ""
                talk_id = x.get('slug','')
                talk_link = 'http://new.talks.ox.ac.uk/talks/id/%s' % talk_id
                talk_ics = 'http://new.talks.ox.ac.uk/api/talks/%s.ics' % talk_id
                speakers_list = []
                speaker = ''

                for entry in x['_embedded']['speakers']:
                    speakers_list.append ((entry['name'] + ', ' + entry['bio']).rstrip(', '))

                speaker = '; '.join(speakers_list)

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
                    'talk_ics': talk_ics,})


            allItems.sort(key=lambda x: x["start_date"], reverse=False)
            slicedItems = allItems[:int(params['count'])]

            groupedItems = [{'startmonth': name, 'talkslist': list(group)} for name, group in groupby(slicedItems, lambda p:p['fm_startmonth'])]


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


