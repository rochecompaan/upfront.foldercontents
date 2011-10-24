from zope.interface import Interface

class IFolderContents(Interface):
    """Interface for adapter which manages indexes on an object """

    def indexes():
        """Return persistent dict containing the indexes"""

    def reindex(clear=False):
        """Iterate over contentish children and index. If clear is true then 
        clear indexes first, and effectively remove stale content."""

    def index(obj):
        """Index an object"""

    def unindex(id):
        """Unindex an object in container identified by id"""

    def contents():
        """Return a list of ids. This list is filtered by the authenticated 
        user's roles."""

