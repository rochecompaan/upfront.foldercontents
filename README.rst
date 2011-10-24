Introduction
============

upfront.foldercontents is a folder contents implementation that does not
depend on the portal_catalog. It adapts IFolderish content to a folder
implementation that indexes allowedRolesAndUsers directly on the
container and iterate directly over the objects in the container.

Once you use the foldercontents adapter provided by this package you no
longer depend on the portal_catalog to list the content of a folder. No
indexes are removed from the catalog however since it is not the
responsibility of this package to do so.

Currently it does not support sorting inside a folder and does not have
an index that is equivalent to getObjectPositionInParent. You are
encouraged to subclass and extend the existing adapter if you want this
functionality.

Compatibility
=============

So far it has only been tested on Plone 3.x.

Installation
============

Simply add the egg to your buildout configuration.

