# coding=utf-8

# TODO:0 restore modelc (use cli + config)
# TODO:0 error not always printed !
#        printer must inherit message printing from
# TODO:0 object/evaluation model issuebox not bound to scenario
#        so no error reported when building object message
# TODO:0 chech error/print for main language
# TODO:0 handle use message 'Nothing to do, because file' in merge
#       check with us01scs  without ?0
#       currently the merger generate an empty file
#       is should be enough to first check soil line
#       if not, just compile /use if imported
#       otherwise just print comments
# TODO:1 enable glossary in all models
# TODO:1 add inheritance in cl metamodel
# FIXME:1 display /tmp error in sex/use
#        for metamodels, since composed metamodels are
#        important (e.g. permissoion -> usecase
# TODO:1 add @assertion
# TODO:1 import between cl diagram could be very useful


#

# TODO:2 enable 0package
# TODO:2 check permission analysis
# TODO:3 re parser
# TODO:3 is parser
# TODO:3 oc parser -> cl


# megamodels
# ----------
# * parser
# * summary/metrics
#
# glossaries
# ----------
#
# * metamodel
# * parser
# * integration in other models
# * summary/metrics
#
# usecases
# --------
#
# * summary
# * error checking
# * printer
# * add management of description
# * priority, interface, etc.
# * scm coverage - scm
# * pmm/clm coverage -- pmm ucm
#
# classes
# -------
#
# * refactor associationClass
# * add package statement
# * spec for clm language ?
# * check a few things in the parser
# * check if comment handling is ok
# * add a few test to check result
# * coverage of invariant wrt class model
# * pmm/ucm coverage -- pmm ucm
#
# objects
# -------
#
# * summary/metrics
# * add description
# * add the possibility to include other obm files at the begining
#   (avoid circular dependencies)
# * clm coverage
#
# scenarios
# ---------
#
# * summary/metrics
# * generation of access model
# * add the possibility to include a obm
# * add description
# * spec for scm as own language (while based on soil)
# * implement assertions (inv + query)
# * ucm coverage
# * clm coverage
# * plm coverage
#
# permissions
# -----------
#
# * summary/metrics?
# * improve language
# * pmm/
#
# access
# ------
#
# * define objectives
# * define language
#
