from zope.component import getAdapter
from zope.app.component.interfaces import ISite

from Products.CMFCore.interfaces import IFolderish

from upfront.foldercontents.interfaces import IFolderContents

def onObjectMoved(ob, event):
    """Catalog / uncatalog in CMF container"""

    # Do nothing if portal_factory is involved
    if 'portal_factory' in ob.getPhysicalPath():
        return

    # If ob is a site do nothing
    if ISite.providedBy(ob):
        return

    # Parent must be a CMF container
    if not IFolderish.providedBy(event.newParent or event.oldParent):
        return

    # Uncatalog object
    if event.oldParent is not None:
        IFolderContents(event.oldParent).unindex(event.oldName)

    # Catalog object. The 'in' check is needed for copying trees of objects.
    if (event.newParent is not None) and (ob.id in event.newParent.objectIds()):
        IFolderContents(event.newParent).index(ob)

def afterTransition(ob, event):
    """Reindex in container"""
    parent = getattr(ob, 'aq_parent', None)
    if parent is None:
        return

    IFolderContents(parent).index(ob)

def onObjectModified(ob, event):
    """Reindex in container"""
    parent = getattr(ob, 'aq_parent', None)
    if parent is None:
        return

    if IFolderish.providedBy(parent):
        IFolderContents(parent).index(ob)
