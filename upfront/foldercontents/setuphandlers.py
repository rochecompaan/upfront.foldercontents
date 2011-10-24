from Products.CMFCore.utils import getToolByName

def isNotUpfrontDietProfile(context):
    return context.readDataFile("upfrontdiet_marker.txt") is None

def postInstall(context):
    if isNotUpfrontDietProfile(context): return 
    site = context.getSite()

    # Remove all content types from portal_catalog
    # xxx: not working as expected
    '''
    tool = site.archetype_tool
    for type in tool.listRegisteredTypes():
        meta_type = type['meta_type']
        catalogs = tool.getCatalogsByType(meta_type)
        catalogs = [cat for cat in catalogs if cat.id != 'portal_catalog']
        tool.setCatalogsByType(meta_type, catalogs) 
    '''

    '''
    # Remove indexes
    pc = site.portal_catalog
    if not hasattr(pc, '_dieted'):
        setattr(pc, '_dieted', 1)
        whitelist = ('allowedRolesAndUsers', 'SearchableText', 'effective',
            'getObjPositionInParent', 'start', 'Date', 'Subject')
        for id in pc.indexes():
            if id not in whitelist:
                pc.manage_delIndex(id)
    '''                
