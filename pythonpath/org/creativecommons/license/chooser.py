#Author: Ishan Thilina Somasiri
#E-mail: ishan@ishans.info
#Blog: www.blog.ishans.info


import rdflib
from rdflib import plugin
from rdflib.namespace import Namespace

from org.creativecommons.license.store import query
from org.creativecommons.license.unported import Unported
from org.creativecommons.license.license import License

#register the plugins

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')

plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')


class Chooser():
    """
    """
    def __init__(self, ):
        """
        """
        pass

    def __makeLicenseQuery(self, allowRemixing,
                           prohibitCommercialUse,
                           requireShareAlike, jurisdiction):
        """
        Creates the sparql query String for the selectLicense method.
        Arguments:
        - `allowRemixing`:Boolean
        - `prohibitCommercialUse`:Boolean
        - `requireShareAlike`:Boolean
        - `jurisdiction`: Jurisdiction
        """
        #Create the basic query
        queryString = ("SELECT ?license "
        "WHERE {"
        "      ?license cc:requires cc:Attribution . "
        "      ?license cc:permits  cc:Distribution . ")

        optionalQuery =\
           ("OPTIONAL {?license cc:deprecatedOn ?deprecatedDate } . "
        "OPTIONAL {?license dcq:isReplacedBy ?replacedBy } . ")

        extraQuery = ""

        qFilter = "!bound(?deprecatedDate) && !bound(?replacedBy) "

        #add jurisdiction filter
        if ((jurisdiction is None) or (isinstance(jurisdiction, Unported))):
            #limit results to unported
            optionalQuery +=\
            ("OPTIONAL { ?license cc:jurisdiction ?jurisdiction } . ")
            qFilter += "&& !bound(?jurisdiction) "

        else:
            #add a qualifier for the specific jurisdiction
            extraQuery += "?license cc:jurisdiction <" + \
              str(jurisdiction) + "> . "
        #add optional qualifiers
        if allowRemixing:
            extraQuery += "?license cc:permits cc:DerivativeWorks . "

        else:
            #only -nd licenses
            optionalQuery +=\
            "OPTIONAL { ?license ?prohibitsRemixing cc:DerivativeWorks } . "
            qFilter += "&& !bound(?prohibitsRemixing) "

        if prohibitCommercialUse:
            extraQuery += "?license cc:prohibits cc:CommercialUse . "
        else:
            #filter out -nc licenses
            optionalQuery +=\
              "OPTIONAL { ?license ?allowCommercialUse cc:CommercialUse } . "
            qFilter += "&& !bound(?allowCommercialUse) "

        if requireShareAlike:
            extraQuery += "?license cc:requires cc:ShareAlike . "

        else:
            #filter out -sa licenses
            optionalQuery +=\
               "OPTIONAL { ?license ?noShareAlike cc:ShareAlike } . "
            qFilter += "&& !bound(?noShareAlike) "

        #close the query
        queryString += extraQuery + optionalQuery
        queryString += "FILTER(" + qFilter + ")      }"

        return queryString

    def selectLicense(self, allowRemixing, prohibitCommercialUse,
                        requireShareAlike, jurisdiction):
        """Select the Creative Commons license for given parameters.
    Arguments:
    - `allowRemixing`:Boolean-Is remixing allowed
    - `prohibitCommercialUse`:Boolean-Commercial usage
    - `requireShareAlike`:Boolean-Requires  share alike
    - `jurisdiction`:Jurisdiction- Jurisdiction of the license
    """
        #execute a simple query
        queryString = self.__makeLicenseQuery(
            allowRemixing, prohibitCommercialUse,
                                            requireShareAlike, jurisdiction)

        results = query(queryString)
        for uri in results:
            uriStr = str(uri[0])
            if "sampling" in uriStr:
                continue
            return License(uriStr)

        return None

    def __makePDToolQuery(self, ):
        """Create the sparql query String for the selectPDTools() method
        """
        #Create the basic query
        queryString = ("SELECT ?license "
        "WHERE {"
        "      ?license cc:permits  cc:Distribution . "
        "      ?license cc:permits  cc:DerivativeWorks . "
        "      ?license cc:permits  cc:Reproduction . "
        "OPTIONAL {?license cc:deprecatedOn ?deprecatedDate } . "
        "OPTIONAL {?license dcq:isReplacedBy ?replacedBy } . ")

        qFilter = "!bound(?deprecatedDate) && !bound(?replacedBy) "

        #close the query
        queryString += "FILTER(" + qFilter + ")      }"

        return queryString

    def selectPDTools(self, territory, toolType):
        """Select the appropriate public deomain tool from the RDF.

        Arguments:
        - `territory`:String-Selected territory
        - `toolType`:int- Select between CC0(2) or PD(3)
        """
        #execute a simple query
        queryString = self.__makePDToolQuery()

        #Execute the query and obtain results
        results = query(queryString)

        for uri in results.result:
            uriStr = str(uri[0])

            if (toolType == 2):
                if "publicdomain" in uriStr:
                    if "zero" in uriStr:
                        return License(uriStr, territory)

            if (toolType == 3):
                if "publicdomain" in uriStr:
                    if "zero" not in uriStr:
                        return License(uriStr)

        return None
