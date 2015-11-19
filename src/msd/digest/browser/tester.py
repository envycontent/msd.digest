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
    def dateFrom(self):
        return self.request.dateFrom
