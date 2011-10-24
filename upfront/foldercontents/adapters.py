import types
from hashlib import md5

from Acquisition import aq_inner, aq_base
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import multiunion
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.component import adapts
from zope.index.interfaces import IIndexSearch
from zope.index.keyword.interfaces import IKeywordQuerying
from zope.index.keyword.index import KeywordIndex
from Products.ZCatalog.Lazy import LazyMap

from Products.CMFCore.interfaces import IFolderish, IContentish
from Products.CMFCore.utils import _getAuthenticatedUser, getToolByName
from Products.CMFPlone.CatalogTool import allowedRolesAndUsers

from interfaces import IFolderContents

KEY = '_upfront_foldercontents_indexes'

def str2int(s):
    """ Python's builtin hash function defaults to 64 bit on x86_64.
        This is a workaround.
    """

    return int(int(md5(s).hexdigest(), 16) % 2000000000)

class FolderContents(object):

    implements(IFolderContents)
    adapts(IFolderish)

    __indexes__ = (
        ('allowedRolesAndUsers', KeywordIndex),
    )

    def __init__(self, context):
        self.context = context
        unwrapped = aq_base(context)

        reindex = False
        if not hasattr(unwrapped, KEY):
            setattr(unwrapped, KEY, PersistentDict())
            reindex = True
        
        indexes = getattr(unwrapped, KEY)

        # _folder_id_keys is always present
        if not hasattr(unwrapped, '_folder_id_keys'):
            setattr(unwrapped, '_folder_id_keys', OOBTree())

        # Create indexes
        for tu in self.__indexes__:
            name, klass = tu
            if not indexes.has_key(name):
                indexes[name] = klass()
                reindex = True

        if reindex:
            self.reindex()

    @property
    def indexes(self):
        return getattr(self.context, KEY)

    def reindex(self, clear=False):      
        if clear:
            # Clear indexes
            for index in self.indexes.values():
                index.clear()
            self.context._folder_id_keys.clear()

        for ob in self.context.objectValues():         
            self.index(ob)

    def index(self, obj):
        # Content?
        if not IContentish.providedBy(obj):
            return

        # Some objects are content but should be skipped, eg. most old style 
        # tools.
        portal_types = getToolByName(obj, 'portal_types')
        if obj.portal_type not in portal_types.objectIds():
            return

        uid = str2int(obj.id)
        if not self.context._folder_id_keys.has_key(uid):
            self.context._folder_id_keys[uid] = obj.id
        for name, index in self.indexes.items():            
            func_name = 'index_' + name
            func = getattr(self, func_name, None)
            if func is None:
                raise RuntimeError, "No index method found for %s" % name
            index.index_doc(uid, func(obj))

    def unindex(self, id):
        uid = str2int(id)
        if self.context._folder_id_keys.has_key(uid):
            del self.context._folder_id_keys[uid]
        for name, index in self.indexes.items():            
            index.unindex_doc(uid)

    def contentIds(self, **kwargs):
        sets = []
        for name, index in self.indexes.items():
            # Filter on this index?
            query = kwargs.get(name, None)
            if query is None: 
                if name != 'allowedRolesAndUsers':
                    continue

            # If a custom query method exists then use it, else do a default 
            # search according to index type.
            func_name = 'query_' + name
            if hasattr(self, func_name):
                ints = getattr(self, func_name)(query)

            elif IKeywordQuerying.providedBy(index):
                if isinstance(query,
                        (types.ListType, types.TupleType)):                
                    ints = index.search(query, 'or')
                else:
                    ints = index.search([query], 'or')

            elif IIndexSearch.providedBy(index):
                if not isinstance(query, 
                        (types.ListType, types.TupleType)):                
                    ints = index.apply((query, query))
                else:
                    ints = []
                    for q in query:
                        ints.extend(index.apply((q, q)))

            else:
                raise RuntimeError, "Unknown index type for %s" % name

            sets.append(ints)

        # Find the intersection of all sets
        if len(sets) == 1:
            final = sets[0]
        elif len(sets) == 0:
            final = []
        else:
            # One-liner below is for Python 2.6. Someday...
            #final = set().union(*sets).intersection(*sets)
            final = []
            for s in sets:
                final.extend(s)
            final = set(final)
            for s in sets:
                final = final.intersection(s)

        # Sorting?
        sort_on = kwargs.get('sort_on')
        if sort_on:
            index = self.indexes[sort_on]
            def mysort(a, b):                    
                return cmp(index._rev_index[a], index._rev_index[b])
            final = list(final)
            final.sort(mysort)

        sort_order = kwargs.get('sort_order', '')
        sort_direction = kwargs.get('sort_direction', '')
        if (sort_order == 'reverse') or (sort_direction == 'descending'):
            final.reverse()

        return [self.context._folder_id_keys[i] for i in final]

    def contents(self, **kwargs):
        return LazyMap(self.context._getOb, self.contentIds(**kwargs))

    def index_allowedRolesAndUsers(self, obj):
        return allowedRolesAndUsers(obj)()

    def query_allowedRolesAndUsers(self, query):
        pc = getToolByName(self.context, 'portal_catalog')
        user = _getAuthenticatedUser(self)
        map = pc._listAllowedRolesAndUsers(user) 
        ints = self.indexes['allowedRolesAndUsers'].search(map, 'or')
        return ints
