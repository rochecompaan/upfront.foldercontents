import unittest, doctest

from DateTime.DateTime import DateTime
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, \
    setupPloneSite
setupPloneSite(extension_profiles=['upfront.diet:default'])

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

def addMember(self, username, fullname="", email="", roles=('Member',), last_login_time=None):
    self.portal.portal_membership.addMember(username, 'secret', roles, [])
    member = self.portal.portal_membership.getMemberById(username)
    member.setMemberProperties({'fullname': fullname, 'email': email,
                                'last_login_time': DateTime(last_login_time),})

def setUp(self):
    addMember(self, 'member1', 'Member one')

def test_suite():    
    tests = (
        Suite(
            'docs/foldercontents.txt', 
            package="upfront.foldercontents",
            setUp=setUp,
            optionflags=optionflags,
            test_class=FunctionalTestCase
        ),
    )    
    return unittest.TestSuite(tests)
