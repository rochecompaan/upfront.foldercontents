import urllib

from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ATContentTypes.interface import IATTopic
from Products.CMFPlone.utils import safe_unicode
from plone.app.content.browser import foldercontents
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.tableview import Table
from plone.memoize import instance

from upfront.foldercontents.interfaces import IFolderContents

class LazyDict(dict):
    """A dictionary that only sets all its items on the first 
    access of any key."""

    def __init__(self, func, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.func = func
        self._initialized = False

    def __getitem__(self, key):
        if not self._initialized:
            self._initialized = True
            self.update(self.func(self))
        return dict.__getitem__(self, key)            

class FolderContentsView(foldercontents.FolderContentsView):
    """
    """    
    implements(IFolderContentsView)

    def contents_table(self):
        table = FolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

class FolderContentsTable(foldercontents.FolderContentsTable):

    def folderitems(self):
        """
        """
        context = aq_inner(self.context)

        # ATTopic object must come from a catalog, so revert to superclass
        if IATTopic.providedBy(context):
            return foldercontents.FolderContentsTable.folderitems.fget(self)
        
        results = []
        for i, id in enumerate(IFolderContents(context).contentIds()):
          
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            results.append(
                LazyDict(
                    self._lazy_dict_func, id=id, table_row_class=table_row_class
                )
            )

        return results

    def _lazy_dict_func(self, di):
        """Fetch object. Build a dictionary containing metadata for object 
        and return it."""
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = context.browserDefault()

        obj = self.context._getOb(di['id'])

        url = obj.absolute_url()
        path = "/".join(obj.getPhysicalPath())

        icon = plone_view.getIcon(obj);
       
        type_class = 'contenttype-' + plone_utils.normalizeString(obj.portal_type)

        try:
            review_state = portal_workflow.getInfoFor(obj, 'review_state')
        except WorkflowException:
            review_state = ''
        state_class = 'state-' + plone_utils.normalizeString(review_state)

        relative_url = obj.absolute_url(relative=True)

        portal_type = obj.portal_type
        type_title_msgid = portal_types[portal_type].Title()
        url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                context=self.request),
                                      safe_unicode(obj.Description()))

        modified = plone_view.toLocalizedTime(
            obj.ModificationDate(), long_format=1)

        obj_type = obj.Type()
        if obj_type in use_view_action:
            view_url = url + '/view'
        elif obj.restrictedTraverse('@@plone').isStructuralFolder():
            view_url = url + "/folder_contents"              
        else:
            view_url = url

        is_browser_default = len(browser_default[1]) == 1 and (
            obj.id == browser_default[1][0])
        
        di.update(dict(
            url = url,
            url_href_title = url_href_title,
            id = obj.getId(),
            quoted_id = urllib.quote_plus(obj.getId()),
            path = path,
            title_or_id = obj.pretty_title_or_id(),
            obj_type = obj_type,
            size = obj.getObjSize(),
            modified = modified,
            icon = icon.html_tag(),
            type_class = type_class,
            wf_state = review_state,
            state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                       obj_type),
            state_class = state_class,
            is_browser_default = is_browser_default,
            folderish = obj.restrictedTraverse('@@plone').isStructuralFolder(),
            relative_url = relative_url,
            view_url = view_url,
            is_expired = context.isExpired(obj),
        ))
        return di

class FolderContentsKSSView(foldercontents.TableKSSView):
    table = FolderContentsTable
