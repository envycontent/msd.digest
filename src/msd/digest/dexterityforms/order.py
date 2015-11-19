from plone.autoform.form import AutoExtensibleForm
from zope import interface
from zope import schema
from zope import component
from z3c.form import form, button

from Products.statusmessages.interfaces import IStatusMessage

from msd.digest import _


class OrderFormSchema(interface.Interface):

    digestTitle = schema.TextLine(
            title=_(u"Title of the Digest"),
        )

    dateFrom = schema.Date(
            title=_(u"Start Date"),
            required=False,
        )

    dateTo = schema.Date(
            title=_(u"End Date"),
            required=False
        )

    department = schema.TextLine(
            title=_(u"OxPoints Department Code"),
        )


class OrderFormAdapter(object):
    interface.implements(OrderFormSchema)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.digestTitle = None
        self.dateFrom = None
        self.dateTo = None
        self.department = None



class OrderForm(AutoExtensibleForm, form.Form):
    schema = OrderFormSchema
    form_name = 'order_form'

    label = _(u"Create your Talks Digest")
    description = _(u"This will create a plain page to copy and paste")

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)

        # call the base class version - this is very important!
        super(OrderForm, self).update()

    @button.buttonAndHandler(_(u'Order'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Handle order here. For now, just print it to the console. A more
        # realistic action would be to send the order to another system, send
        # an email, or similar

        print u"Order received:"
        print u"  Customer: ", data['digestTitle']
        print u"  Telephone:", data['dateFrom']
        print u"  Address:  ", data['dateTo']
        print u"            ", data['department']
        print u""

        # Redirect back to the front page with a status message

        IStatusMessage(self.request).addStatusMessage(
                _(u"Thank you for your order. We will contact you shortly"),
                "info"
            )

        redirect_url = "%s/@@tester" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)


    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
