################################################################################
# This script demonstrates using the SharePoint REST API perform CRUD operations
# on a SharePoint list. 
################################################################################
# REST API documentation:
################################################################################
# Import required modules
################################################################################

import datetime
import requests
from requests_toolbelt.utils import dump
import json
from simplecrypt import encrypt, decrypt
from config import strConnectURI, strUsername, strPassword, strContextURI, strListInfoURI

strListDataURI = strListInfoURI + "/items"
strListContentTypeURI = strListInfoURI + "/contenttypes"

# As of 2019-02-08
# Do *NOT* use the PIP version, mods at https://github.com/ljr55555/sharepy/tree/develop required for functionality
import sharepy

################################################################################
# Function definitions
################################################################################
# This function finds the ID of a record
# Input: s -- connection to  SharePoint REST API
#        strListDataURL -- items endpoint for list
#        strAttr -- attribute on which to search
#        strOperator -- ODATA filter operation
#        strValue -- attribute value for search
# Output: JSON of records returned
################################################################################
def findSPRecord(s, strListDataURL, strAttr=None, strOperator=None, strValue=None):
    if strAttr and strOperator and strValue:
        strListContentURL = ("%s?&$filter=%s %s '%s'" % (strListDataURL, strAttr, strOperator, strValue))
    else:
        strListContentURL = strListDataURL
    requestToSP = s.get(strListContentURL)
    jsonReply = json.loads(requestToSP.text)
    return jsonReply['d']['results']

################################################################################
# This function finds the ID of a record uniquely identified 
# by the filter criterion
#  See https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/use-odata-query-operations-in-sharepoint-rest-requests#bk_supported
# Input: s -- connection to  SharePoint REST API
#        strListDataURL -- items endpoint for list
#        strAttr -- attribute on which to search
#        strOperator -- ODATA filter operation
#        strValue -- attribute value for search
# Output: integer item ID
################################################################################
def findSPRecordID(s, strListDataURL, strAttr, strOperator, strValue):
    if strAttr and strOperator and strValue:
        strListContentURL = ("%s?&$filter=%s %s '%s'" % (strListDataURL, strAttr, strOperator, strValue))
    else:
        strListContentURL = strListDataURL
    requestToSP = s.get(strListContentURL)
    jsonReply = json.loads(requestToSP.text)
    jsonListContent = jsonReply['d']

    iItemID = jsonListContent['results'][0].get('ID')
    return iItemID

################################################################################
# This function creates a new record in a SharePoint list
# Input: s -- connection to  SharePoint REST API
#        strContextURL -- contextinfo endpoint for SP Site
#        strListDataURL -- items endpoint for list
#        strBody -- dictionary of data to POST
# Output: integer HTTP response
################################################################################
def writeNewRecord(s, strContextURL, strListDataURL, strBody):
    strContentType = "application/json;odata=verbose"
    
    # Get digest value for use in POST
    requestToSP = s.post(strContextURL)
    jsonDigestRaw = json.loads(requestToSP.text)
    jsonDigestValue = jsonDigestRaw['d']['GetContextWebInformation']['FormDigestValue']
    
    strBody  = json.dumps(strBody)

    postRecord = s.post(strListDataURL,headers={"Content-Length": str(len(json.dumps(strBody))), 'accept': strContentType, 'content-Type': strContentType, "X-RequestDigest": jsonDigestValue}, data=strBody)
    #data = dump.dump_all(postRecord)
    #print("Session data:\t%s" % data.decode('utf-8'))
    #print("HTTP Status Code:\t%s\nResult code content:\t%s" % (postRecord.status_code, postRecord.content))
    return postRecord.status_code

################################################################################
# This function updates an existing record in SharePoint
# Input: s -- connection to  SharePoint REST API
#        strContextURL -- contextinfo endpoint for SP Site
#        strListDataURL -- URI for list items
#        strBody -- dictionary of data to POST
# Output: integer HTTP response
################################################################################
def updateRecord(s, strContextURL,strListDataURL, strBody, iRecordToUpdate):
    strContentType = "application/json;odata=verbose"

    strListItemURL = ("%s(%s)" % (strListDataURL, iRecordToUpdate))

    # Get digest value for use in POST
    requestToSP = s.post(strContextURL)
    jsonDigestRaw = json.loads(requestToSP.text)
    jsonDigestValue = jsonDigestRaw['d']['GetContextWebInformation']['FormDigestValue']

    strBody  = json.dumps(strBody)

    postRecord = s.post(strListItemURL,headers={"Content-Length": str(len(json.dumps(strBody))), 'accept': strContentType, 'content-Type': strContentType, "X-RequestDigest": jsonDigestValue, "IF-MATCH": "*", "X-HTTP-Method": "MERGE"}, data=strBody)
    #data = dump.dump_all(postRecord)
    #print("Session data:\t%s" % data.decode('utf-8'))
    return postRecord.status_code

################################################################################
# This function deletes a record from a SharePoint list
# Input: s -- connection to  SharePoint REST API
#        strContextURL -- contextinfo endpoint for SP Site
#        strListDataURL -- URI for list items
#        iItemID -- ID of item to delete
# Output: integer HTTP response
################################################################################
def deleteRecord(s, strContextURL,strListDataURL, iRecordID):
    # Get digest value for use in POST
    requestToSP = s.post(strContextURL)
    jsonDigestRaw = json.loads(requestToSP.text)
    jsonDigestValue = jsonDigestRaw['d']['GetContextWebInformation']['FormDigestValue']

    strListDataDeletionURL = ("%s(%s)" % (strListDataURL, iRecordID))

    postRecord = s.post(strListDataDeletionURL,headers={"X-RequestDigest": jsonDigestValue, "IF-MATCH": "*", "X-HTTP-Method": "DELETE"})
    #data = dump.dump_all(postRecord)
    #print("Session data:\t%s" % data.decode('utf-8'))
    return postRecord.status_code

################################################################################
# End of functions
################################################################################

strUID = strUsername
strPass = strPassword

spoConnection = sharepy.connect(strConnectURI,strUID,strPass)

## Get ListItemEntityTypeFullName from list
r = spoConnection.get(strListInfoURI)
jsonReply = json.loads(r.text)
strListItemEntityTypeFullName = jsonReply['d']['ListItemEntityTypeFullName']

strListNextContentURI = strListDataURI

data = []
i = 0
while strListNextContentURI:
    i = i + 1
    print(strListNextContentURI)
    r3 = spoConnection.get(strListNextContentURI)
#    print(r3.text)
    jsonReply = json.loads(r3.text)

    jsonListContent = jsonReply['d']
    strListNextContentURI = jsonReply['d'].get('__next',None)
    strResultsContent = jsonListContent['results']

    for strResult in strResultsContent:
        if strResult['Title'] is None:
            print("I would delete record %s with chat count %s" % (strResult['ID'],strResult['dailyTeamChat']))
            iDeletionResult = deleteRecord(spoConnection, strContextURI, strListDataURI, strResult['ID'])
            if iDeletionResult is 200:
                print("Successfully deleted record %s" % strResult['ID'])
            else:
                print("Failed to deleted record %s -- HTTP result %s" % (strResult['ID'], iDeletionResult))

