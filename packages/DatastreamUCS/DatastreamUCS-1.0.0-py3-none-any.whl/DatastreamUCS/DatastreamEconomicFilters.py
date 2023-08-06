"""
DatastreamEconomicFilters
-------------------------
Datastream provides access to nearly 16 million economic series. With coverage of this extent, it can be difficult to prioritise 
which region, country, sector or industry to analyse and investigate. With this in mind, clients that access the full Datatstream Web Service 
can now poll for the latest changes and corrections to any of the economic series.

Even with polling for changes and corrections, the large number of economic series supported can produce a large number of updates to process each day.
To reduce the number of updates, Datastream provides a global filter, REFINITIVCC_KEYIND_GLOBAL, that comprises the 25K most prominent series. Querying
for updates using this filter can significantly reduce the number of updates reported.

Clients can also create their own custom filters comprising up to 100K series and use these to query for changes and corrections.

This module defines the DatastreamEconomicFilters class and supporting objects that permit clients to manage their custom filters.
"""

import re
import requests
import json
import pytz
from datetime import datetime, timedelta, date
import platform
import configparser
import atexit
import time
from enum import IntEnum

class DSEconomicFiltersLogLevel(IntEnum):
    """
    The module does some basic logging and this enumeration determines the level of logging to report
    LogNone - turn logging off completely
    LogError - log only errors such as exceptions, etc.
    LogWarning - log non-fatal errors
    LogInfo - log major steps such as starting API query and receiving response
    LogTrace - log minor steps such as converting object to JSON, etc.
    LogVerbose -log the full json request content, etc.

    Used in DSEconomicFiltersLogFuncs methods
    Example:
    DSEconomicFiltersLogFuncs.LogLevel = DSEconomicFiltersLogLevel.LogError

    """
    LogNone = 0
    LogError = 1
    LogWarning = 2
    LogInfo = 3
    LogTrace = 4
    LogVerbose = 5

class DSEconomicFiltersLogFuncs:
    """
    DSEconomicFiltersLogFuncs is used to log actions within the DatastreamEconomicFilters methods

    DatastreamEconomicFilters methods call methods here to log processing steps.
    Methods:
    LogException - used to log exceptions returned due to network failure, invalid credentials, etc
    LogError - used to log general error messages
    LogDetail - used to log info with a specified logging level

    These methods call methods LogExcepFunc, LogErrorFunc and LogDetailFunc which can be overridden to implement your own logging.
    By default, LogExcepFunc, LogErrorFunc and LogDetailFunc call internal functions that just call print function

    An example of overriding the implementation:
    def LogDetailOverride(loglevel, moduleName, funcName, commentStr, verboseObj = None):
        # provide override implementation
        print('....')

    #use in built logging with print function
    DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'X', 'Y', 'Z')
    #use custom function LogDetailOverride
    DSEconomicFiltersLogFuncs.LogDetailFunc = LogDetailOverride
    DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'X', 'Y', 'Z')

    """
    LogLevel = DSEconomicFiltersLogLevel.LogNone  # By default we assume no logging required

    @staticmethod
    def __logExcepInternal(moduleName, funcName, commentStr, excep):
        # internal default function for basic logging of exceptions using print method
        print(str(datetime.utcnow()), moduleName, funcName, commentStr, sep=': ')
        print(excep)

    @staticmethod
    def __logErrorInternal(moduleName, funcName, commentStr, verboseObj):
        # internal default function for basic logging of errors using print method
        print(str(datetime.utcnow()), moduleName, funcName, commentStr, sep=': ')
        if verboseObj:
            print(verboseObj)

    @staticmethod
    def __logDetailInternal(loglevel, moduleName, funcName, commentStr, verboseObj):
        # internal default function for basic logging of generic logs using print method
        print(str(datetime.utcnow()), moduleName, funcName, commentStr, sep=': ')
        if verboseObj and DSEconomicFiltersLogFuncs.LogLevel >= DSEconomicFiltersLogLevel.LogVerbose:
            print(verboseObj)

    # function overrides to allow you to redirect the logging to custom handlers. They default to the internal static methods that just perform printing
    LogExcepFunc, LogErrorFunc, LogDetailFunc = __logExcepInternal, __logErrorInternal, __logDetailInternal 

    # the public logging functions used by the economic filter methods
    @staticmethod
    def LogException(moduleName, funcName, commentStr, excep):
        # Used to log exceptions returned due to network failure, invalid credentials, etc
        if DSEconomicFiltersLogFuncs.LogLevel >= DSEconomicFiltersLogLevel.LogError:
            DSEconomicFiltersLogFuncs.LogExcepFunc(moduleName, funcName, commentStr, excep)

    @staticmethod
    def LogError(moduleName, funcName, commentStr, verboseObj = None):
        # Used to log general error messages
        if DSEconomicFiltersLogFuncs.LogLevel >= DSEconomicFiltersLogLevel.LogError:
            DSEconomicFiltersLogFuncs.LogErrorFunc(moduleName, funcName, commentStr, verboseObj)

    @staticmethod
    def LogDetail(loglevel, moduleName, funcName, commentStr, verboseObj = None):
        # Used to log info with a specified logging level
        if DSEconomicFiltersLogFuncs.LogLevel >= loglevel:
            DSEconomicFiltersLogFuncs.LogDetailFunc(loglevel, moduleName, funcName, commentStr, verboseObj)


class DSEconomicFiltersDateFuncs:
    """
    DSEconomicFiltersDateFuncs is used internally to convert datetimes to and from JSON "/Date()" format for comms with the API server
    """
    __epoch_date = datetime(1970, 1, 1, tzinfo=pytz.utc)

    @staticmethod
    def jsonDateTime_to_datetime(jsonDate):
        # Convert a JSON /Date() string to a datetime object
        if jsonDate is None:
            return None
        try:
            match = re.match(r"^(/Date\()(-?\d*)(\)/)", jsonDate)
            if match == None:
                match = re.match(r"^(/Date\()(-?\d*)([+-])(..)(..)(\)/)", jsonDate)
            if match:
                return DSEconomicFiltersDateFuncs.__epoch_date + timedelta(seconds=float(match.group(2))/1000)
            else:
                raise Exception("Invalid JSON Date: " + jsonDate)
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DSEconomicFiltersLogFuncs.jsonDateTime_to_datetime', 'Exception occured:', exp)
            raise

    @staticmethod
    def toJSONdate(inputDate):
        # convert to /Date() object with no of ticks relative to __epoch_date
        if isinstance(inputDate, datetime) or isinstance(inputDate, date):
            inputDate = datetime(inputDate.year, inputDate.month, inputDate.day, tzinfo=pytz.utc)
        elif isinstance(inputDate, str):
            inputDate = datetime.strptime(inputDate, "%Y-%m-%d")
            inputDate = datetime(inputDate.year, inputDate.month, inputDate.day, tzinfo=pytz.utc)
        else: #should not call with unsupported type
            return inputDate
        ticks = (inputDate - DSEconomicFiltersDateFuncs.__epoch_date).total_seconds() * 1000
        jsonTicks = "/Date(" + str(int(ticks)) + ")/"
        return jsonTicks


class DSEconFilterJsonDateTimeEncoder(json.JSONEncoder):
    """ 
    DSEconFilterJsonDateTimeEncoder is used in the conversion of datetime objects into JSON format. It's passed into json.dumps()

    Example:
    jsonText = json.dumps(reqObject, cls = DSEconFilterJsonDateTimeEncoder)
    """
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return DSEconomicFiltersDateFuncs.toJSONdate(obj)
        # else fall through to json default encoder
        return json.JSONEncoder.default(self, obj)


class DSFilterUpdateActions(IntEnum):
    """
    DatastreamEconomicFilters supports an UpdateFilter method that allows you to modify the contents of an existing filter.
    DSFilterUpdateActions specifies the update action.

    Options:
        CreateFilter: Reserved for internal filter validation checks.
        AppendConstituents: Used to append a list of economic series to existing list of filter constituents. 
        ReplaceConstituents: Used to completely replace the constituents of a filter.
        RemoveConstituents: Used to remove a subset of economic series from the current list of filter constituents.
        UpdateDescription: Used to modify the description for the filter.
        UpdateSharedState: Used to specify whether the filter is private to your Datastream ID or shared with other Datastream IDs belonging to your parent ID.
    """
    CreateFilter = 0
    AppendConstituents = 1
    ReplaceConstituents = 2
    RemoveConstituents = 3
    UpdateDescription = 4
    UpdateSharedState = 5

class DSFilterGetAllAction(IntEnum):
    """
    DatastreamEconomicFilters supports a GetAllFilters method that allows you to query for all the existing filters currently available.
    DSFilterGetAllAction specifies the retrieval options.

    Options:
        PersonalFilters: Use this flag to retrieve only filters created with your Datastream ID
        SharedFilters: Use this flag to retrieve both your personal filters plus any filters shared by other child IDs that share your parent Datastream ID. 
        RefinitivFilters: Use this flag to retrieve just the list Refinitiv global filters available to all clients.
        AllFilters:  Use this flag to retrieve all private, shared or Refinitiv global filters.
    """
    PersonalFilters = 0
    SharedFilters = 1
    RefinitivFilters = 2
    AllFilters = 3

class DSFilterResponseStatus(IntEnum):
    """
    All DatastreamEconomicFilters methods to retrieve or modify filters return a respone object which includes a ResponseStatus property.
    The ResponseStatus property specifies success or failure for the request using a DSFilterResponseStatus value

    Response Values:
        FilterSuccess: The request succeeded and the response object's Filter property should contain the (updated) filter (except for DeleteFilter method).
        FilterPermissions: Users need to be specifically permissioned to create custom filters. This flag is set if you are not currently permissioned.
        FilterNotPresent: Returned if the requested ID does not exist.
        FilterFormatError: Returned if your request filter ID is not in the correct format, or if you try and modify a refinitiv global filter (ID begins REFINITIV*).
        FilterSizeError: Returned if your call to CreateFilter or ModifyFilter contains a list with zero or in excess of the 100K constituents.
        FilterConstituentsError: Returned if your supplied filter constituent list (on CreateFilter) contains no valid economic series. The filter won't be created.
        FilterError:  The generic error flag. This will be set for any error not specified above. Examples are:
            Requested filter ID is not present
            You have reached the maximum permitted number of custom economic filters (maximum 50)
            Requested filter ID (on CreateFilter) already exists
    """
    FilterSuccess = 0
    FilterPermissions = 1
    FilterNotPresent = 2
    FilterFormatError = 3
    FilterSizeError = 4
    FilterConstituentsError = 5
    FilterError = 6



class DSEconomicsFilter:
    """
    DSEconomicsFilter is the base object for retrieval or creating/modifying a filter.

    Properties
    ----------
    FilterID: The filter identifier must be between 5 and 45 characters long and contain only alphanumeric or underscore characters. e.g. MyFilter.
    Description: A string describing the filter. Max 127 alphanumeric characters.
    Constituents: An array of strings, each defining an economic series. Economic series are between 7 and 9 characters in length and contain
                  only alphanumeric characters plus the following special characters $&.%#£,
                  Examples: USGDP...D, USGB10YR, JPEMPA&FP, LBUN%TOT, UKIMPBOPB, USUNRP%DQ
    ConstituentsCount: The number of constituent items.
    Created: a datetime representing when the filter was first created.
    LastModified: a datetime representing when the filter was last modified.
    OwnerId: The Datastream parent ID that owns the filter. This will always be your Datastream parent ID or None if the filter is a Refinitiv global filter.
    Shared: A bool set to True if the filter is shared with all children of your Datastream parent ID. False indicates only your Datastream ID can use the filter.
    """
    def __init__(self, jsonDict = None):
        self.FilterId = None
        self.Description = None
        self.Constituents = None
        self.ConstituentsCount = 0
        self.Created = datetime.utcnow()  # only valid when received as a response. On create or update this field is ignored
        self.LastModified = datetime.utcnow() # only valid when received as a response. On create or update this field is ignored
        self.OwnerId = None
        self.Shared = False
        if jsonDict: # upon a successful response from the API server jsonDict will be used to populate the DSEconomicsFilter object with the response data.
            self.FilterId = jsonDict['FilterId']
            self.Description = jsonDict['Description']
            self.Constituents = jsonDict['Constituents']
            self.ConstituentsCount = jsonDict['ConstituentsCount']
            self.Created = DSEconomicFiltersDateFuncs.jsonDateTime_to_datetime(jsonDict['Created'])
            self.LastModified = DSEconomicFiltersDateFuncs.jsonDateTime_to_datetime(jsonDict['LastModified'])
            self.OwnerId = jsonDict['OwnerId']
            self.Shared = jsonDict['Shared']

    def SetSafeUpdateParams(self):
        """ SetSafeUpdateParams: The following parameters are set only in response when we query for economic filters. 
        This method is called before Create or Update to ensure safe values set prior to JSON encoding"""
        self.Created = datetime.utcnow()  # only valid when received as a response. On create or update this field is ignored
        self.LastModified = datetime.utcnow() # only valid when received as a response. On create or update this field is ignored
        self.ConstituentsCount = len(self.Constituents) if isinstance(self.Constituents, list) else 0 # the server gets the true size by inspecting the Constituents property
        self.Owner = None   # only valid when received as a response. On create or update this field is ignored
        self.Shared = self.Shared if isinstance(self.Shared, bool) else False
        self.Description = self.Description if isinstance(self.Description, str) else None


class DSEconomicsFault(Exception):
    """
    DSEconomicsFault exception is a representation of the DSFault error returned from the API server.
    DSFaults are returned for the following reasons:
        Invalid credentials
        Empty credentials
        Access blocked due to missuse of the service.

    A DSEconomicsFault will be thrown in the event a DSFault is returned from the server

    Note: Once access is granted, any other errors, such as not being explicity permissioned to use custom economic filters, or requesting an invalid filter
    returns a DSFilterResponseStatus error flag (e.g. DSFilterResponseStatus.FilterPermissions) in the ResponseStatus property of the returned DSEconomicsFilterResponse
    or DSEconomicsFilterGetAllResponse object. The response's ErrorMessage property will specify the error condition
    """
    def __init__(self, jsonDict):
        super().__init__(jsonDict['Message'])
        self.Code = jsonDict['Code']
        self.SubCode = jsonDict['SubCode']


class DSEconomicsFilterResponse:
    """
    DSEconomicsFilterResponse is the object returned for the GetFilter, CreateFilter, UpdateFilter and DeleteFilter methods.

    Properties
    ----------
    Filter: Upon a successful response, the Filter property will contain a valid DSEconomicsFilter object. For a successful DeleteFilter call the value will be None.
    ResponseStatus: This property will contain a DSFilterResponseStatus value. DSFilterResponseStatus.FilterSuccess represents a successful response.
    ErrorMessage: If ResponseStatus is not DSFilterResponseStatus.FilterSuccess this status string will provide a description of the error condition.
    ItemErrors: When calling CeateFilter or UpdateFilter (AppendConstituents or ReplaceConstituents. Any supplied constituents which have an invalid format,
                or do not exist in the supported dataset (~16M economic series), will be returned as an array in this property.
    Properties: Not currently used and will currently always return None.

    """
    def __init__(self, jsonDict = None):
        self.Filter = None
        self.ResponseStatus = DSFilterResponseStatus.FilterSuccess
        self.ErrorMessage = None
        self.ItemErrors = None
        self.Properties = None
        if jsonDict: # upon a successful response from the API server jsonDict will be used to populate the DSEconomicsFilterResponse object  with the response data.
            self.ResponseStatus = DSFilterResponseStatus(jsonDict['ResponseStatus'])
            self.ErrorMessage = jsonDict['ErrorMessage']
            self.ItemErrors = jsonDict['ItemErrors']
            if jsonDict['Filter']:
                self.Filter = DSEconomicsFilter(jsonDict['Filter'])


class DSEconomicsFilterGetAllResponse:
    """
    DSEconomicsFilterGetAllResponse is the object returned for the GetAllFilters request only.

    Properties
    ----------
    Filters: Upon a successful response, the Filters property will contain a collection of DSEconomicsFilter objects.
    FilterCount: The number of filters returned in the Filters property.
    ResponseStatus: This property will contain a DSFilterResponseStatus value. DSFilterResponseStatus.FilterSuccess represents a successful response.
    ErrorMessage: If ResponseStatus is not DSFilterResponseStatus.FilterSuccess this status string will provide a description of the error condition.
    Properties: Not currently used and will currently always return None.

    Note: The returned filters will not have any constituents returned in the Constituents property. The ConstituentsCount property will tell you
    how many constituents there are in the filter. However, you will need to query for the individual filter to retrieve the list of constituents.

    """
    def __init__(self, jsonDict = None):
        self.Filters = None
        self.FilterCount = 0
        self.ResponseStatus = DSFilterResponseStatus.FilterSuccess
        self.ErrorMessage = None
        self.Properties = None
        if jsonDict:
            self.ResponseStatus = DSFilterResponseStatus(jsonDict['ResponseStatus'])
            self.ErrorMessage = jsonDict['ErrorMessage']
            self.FilterCount = jsonDict['FilterCount']
            if jsonDict['Filters'] is not None:
                self.Filters = [DSEconomicsFilter(jsonFilter) for jsonFilter in jsonDict['Filters']] 


class DSEconomicUpdateFrequency(IntEnum):
    """
    The GetEconomicChanges method can return a collection of DSEconomicChangeCorrection objects, each defining an economic series that has been updated.
    DSEconomicUpdateFrequency is a property of DSEconomicChangeCorrection which specifies the update frequency of the series.

    The values should be self explanatory. Note: at the time of writing, just 55 series exist with a frequency of SemiAnnually. These are all in the 
    Algerian market and sourced from Banque d’ Algerie.
    """
    Daily = 0
    Weekly = 1
    Monthly = 2
    Quarterly = 3
    SemiAnnually = 4
    Annually = 5


class DSEconomicChangeCorrection:
    """
    DSEconomicChangeCorrection is the class defining each economic series returned in the Updates property of the DSEconomicChangesResponse item
    returned in GetEconomicChanges queries.

    Properties
    ----------
    Series: The Datastream mnemonic for the economic series that has updated. e.g. 'JPTFMFLBF', 'USGDP...D', 'UKXRUSD.'
    Frequency: A DSEconomicUpdateFrequency enum describing the update frequency of the series.
    Updated: The update time in UTC when the notification of the change was received by Datastream.
    """
    def __init__(self, jsonDict):
        self.Series = jsonDict['Series']
        self.Frequency = DSEconomicUpdateFrequency(jsonDict['Frequency'])
        self.Updated = DSEconomicFiltersDateFuncs.jsonDateTime_to_datetime(jsonDict['Updated'])


class DSEconomicChangesResponse:
    """
    DSEconomicChangesResponse is the object returned for the GetEconomicChanges request only.

    Properties
    ----------
    NextSequenceId: Upon a successful response, the NextSequenceId property will identify the next sequence to request. If the UpdatesPending property
                    is True, it indicates there are more updates available to be retrieved using the value in this field to request the subsequent updates. 
                    If the UpdatesPending property is False, it indicates that there are currently no more updates available and the returned NextSequenceId
                    value identifies the ID that will be assigned to the next update when it becomes available. This should be used in a periodic query 
                    (ideally every 10 minutes or more) for any new updates.
    FilterId: This field simply returns the ID of the optional custom filter used in the query.
    UpdatesCount: If the GetEconomicChanges request succeeds in returning updates, this field will contain the number of updates in the current response.
    Updates: If the GetEconomicChanges request succeeds in returning updates, this field will contain the collection of DSEconomicChangeCorrection objects
             defining the update details for each economic series.
    UpdatesPending: A GetEconomicChanges response contains a maximum of 10K updates. If the query detected that there were more than 10K items that updated
                    later than the requested sequence ID, UpdatesPending will be set True to indicate a subsequent request for the later updates should be
                    made using the ID specified in the returned NextSequenceId field. If set False, there are currently no more updates pending and NextSequenceId
                    identifies the ID that will be assigned to the next update when it becomes available.
    PendingCount:   If UpdatesPending is set True, this field identifies how many more updates are pending retrieval.
    ResponseStatus: This property will contain a DSFilterResponseStatus value. DSFilterResponseStatus.FilterSuccess represents a successful response.
    ErrorMessage: If ResponseStatus is not DSFilterResponseStatus.FilterSuccess this status string will provide a description of the error condition.
    Properties: Not currently used and will currently always return None.
    """

    def __init__(self, jsonDict = None):
        self.NextSequenceId = 0
        self.FilterId = None
        self.UpdatesCount = 0
        self.Updates = None
        self.UpdatesPending = False
        self.PendingCount = 0
        self.ResponseStatus = DSFilterResponseStatus.FilterSuccess
        self.ErrorMessage = None
        self.Properties = None
        if jsonDict:
            self.NextSequenceId = jsonDict['NextSequenceId']
            self.FilterId = jsonDict['FilterId']
            self.ResponseStatus = DSFilterResponseStatus(jsonDict['ResponseStatus'])
            self.ErrorMessage = jsonDict['ErrorMessage']
            self.UpdatesCount = jsonDict['UpdatesCount']
            if jsonDict['Updates'] is not None:
                self.Updates = [DSEconomicChangeCorrection(jsonUpdate) for jsonUpdate in jsonDict['Updates']] 
            self.UpdatesPending = jsonDict['UpdatesPending']
            self.PendingCount = jsonDict['PendingCount']


class DatastreamEconomicFilters:
    """
    DatastreamEconomicFilters is the client class that manages the connection to the API server on your behalf.
    It allows you to query for all your custom filters and create/modify new filters.

    Methods Supported
    -----------------
    GetAllFilters: Allows you to query for all the current filters available for your use
    GetFilter: Allows you to download a specific filter and examine the current constituent economic series assigned to the filter.
    CreateFilter: Allows you to create a new economic changes and corrections filter with up to 100K constituent series.
    UpdateFilter: Allows you to update an existing filter, replacing, appending or removing constituent items.
    DeleteFilter: Allows you to remove an existing filter.
    GetEconomicChanges: Allows you to query for any economic changes and corrections using an optional filter.

    Note: You need a Datastream ID which is permissioned to access the Datastream APIs. 
          In addition, this ID also needs to be permissioned to access the custom economic filters service.
          Attempting to access this service without these permissions will result in a permission denied error response.

    Example usage:
    # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
    econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
    # query for all your filters
    filtersResp = econFilterClient.GetAllFilters(DSFilterGetAllAction.AllFilters)
    if filtersResp:
        if filtersResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
            # Your Datastream Id might not be permissioned for managing economic filters on this API
            print('GetAllFilters failed with error ' + filtersResp.ResponseStatus.name + ': ' + filtersResp.ErrorMessage)
        elif filtersResp.Filters and filtersResp.FilterCount > 0:
            # You do have access to some filters
            filters = [[filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.ConstituentsCount, 
                        filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description] for filter in filtersResp.Filters]
            df = pd.DataFrame(data=filters, columns=['FilterId', 'OwnerId', 'Shared', 'Constituents', 'LastModified', 'Description'])
            print(df.to_string(index=False))
        else:
            # You do not have any filters with the specified filter type. Try DSFilterGetAllAction.AllFilters which should return
            # the REFINITIVCC_KEYIND_GLOBAL global filter available for download 
            print('GetAllFilters returned zero filters for the authenticated user with the specified DSFilterGetAllAction')

    # sample filter creation
    newFilter = DSEconomicsFilter()
    newFilter.FilterId = 'MyTestFilter'
    newFilter.Constituents = ['CTES85FTA','EOES85FTA','ESES85FTA', 'FNES85FTA']
    newFilter.Description = 'MyTestFilter for testing'
    reqResp = econFilterClient.CreateFilter(newFilter)
    if reqResp:
        if reqResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
            print('GetFilter failed for filter REFINITIVCC_KEYIND_GLOBAL with error ' + reqResp.ResponseStatus.name + ': ' + reqResp.ErrorMessage)
        elif reqResp.Filter != None:
            filter = reqResp.Filter
            names = ['FilterId', 'OwnerId', 'Shared?', 'LastModified', 'Description', 'No. of Constituents']
            data = [filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description, filter.ConstituentsCount]
            df = pd.DataFrame(data, index=names)
            print(df)
            print('Constituents:')
            df = pd.DataFrame(filter.Constituents)
            print(df, end='\n\n')

    """

    def __init__(self, config = None, username = None, password = None, proxies = None, sslCer = None):
        """
        Constructor: user details can be supplied from a config file or passed directly as parameters in constructor

        1) Using ini file (e.g. config.ini) with format

        [credentials]
        username=YourID
        password=YourPwd

        [proxies]
        # of the form: { 'http' : proxyHttpAddress,  'https' : proxyHttpsAddress } See https://docs.python-requests.org/en/latest/user/advanced/
        proxies=ProxyDetails   

        [cert]
        sslCertFile=YourCertFile
        # only read if no sslCertFile entry
        sslCertPath=YourCertPath  

        # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
        econFilterClient = DatastreamEconomicFilters('config.ini')

        2) Bypassing a config file and using your credentials directly:

        econFilterClient = DatastreamEconomicFilters(None, 'YourId', 'YourPwd')

        """

        # Properties
        self.url = "https://product.datastream.com" # Warning: Only override the url for the API service if directed to by Refinitiv.
        self.username = None
        self.password = None
        self.token = None # when you logon your token for subsequent queries is stored here
        self.tokenExpiry = None # tokens are typically valid for 24 hours. The client will automatically renew the token if you make request within 15 minutes of expiry
        self._proxies = None
        self._sslCert = None
        self._certfiles = None
        # some settings that allow us to track version usage on our servers.
        self._reqSession = requests.Session()
        self._buildVer = '1.0.1'
        self._appID = 'DatastreamEconomicFiltersPy-' + self._buildVer
        self._timeout = 180
        self._reqSession.headers['User-Agent'] = self._reqSession.headers['User-Agent'] + ' DatastreamEconomicFiltersPy/' + self._buildVer

        # Load windows certificates to a local file for Windows platform
        pf = platform.platform()
        if pf.upper().startswith('WINDOWS'):
           import wincertstore
           cfile = wincertstore.CertFile()
           cfile.addstore('CA')
           cfile.addstore('ROOT')
           cfile.addstore('MY')
           self._certfiles = cfile.name
           atexit.register(cfile.close)
        else:
            self._certfiles = requests.certs.where()
        

        # you can use a config file to specify the user credentials, ssl certificate file, path, etc.
        if (config): 
            parser = configparser.ConfigParser()
            parser.read(config)

            # Warning: Only override the url for the API service if directed to by Refinitiv.
            if parser.has_section('url'):
                self.url = self.url if parser.get('url', 'path').strip() == '' else parser.get('url', 'path').strip()
                self.url = self.url.lower()
                if self.url:  # we only support https on the API
                    if re.match("^http:", self.url):
                        self.url = self.url.replace('http:', 'https:', 1)

            # you can override the web query timeout value
            if parser.has_section('app'):
                self._timeout = 180 if parser.get('app', 'timeout').strip() == '' else int(parser.get('app', 'timeout').strip())

            # You can optionally provide the Datastream credentials from your config file, or optionally override from the constructor
            if parser.has_section('credentials'):
                self.username = None if parser.get('credentials', 'username').strip() == '' else parser.get('credentials', 'username').strip()
                self.password = None if parser.get('credentials', 'password').strip() == '' else parser.get('credentials', 'password').strip()

            # Optionally provide the proxies details and certfile from the config file also
            if parser.has_section('proxies'):
                configProxies = None if parser.get('proxies','proxies').strip() == '' else parser.get('proxies', 'proxies').strip()
                if configProxies:
                    self._proxies = configProxies

            # Optionally specify a specific cert file from the config, or alternatively an override for the cert path
            if parser.has_section('cert'):
                configCert = None if parser.get('cert','sslCertFile').strip() == '' else parser.get('cert', 'sslCertFile').strip()
                if configCert:
                    self._sslCert = configCert
                else:
                    configPath = None if parser.get('cert','sslCertPath').strip() == '' else parser.get('cert', 'sslCertPath').strip()
                    if configPath: #override system root certificates path
                        self._certfiles = configPath


        # set the full reference to the API service from the supplied hostname
        self.url = self.url +'/DSWSClient/V1/DSEconomicsFilterService.svc/rest/'

        # You can also override any config by specifying your user credentials, proxy or ssl certificate as parameters in the constructor
        # proxy input must be of the form:
        # proxies = { 'http' : proxyHttpAddress,  'https' : proxyHttpsAddress } # see https://docs.python-requests.org/en/latest/user/advanced/
        if proxies:
            self._proxies = proxies
        if sslCer: # option to specify specific ssl certificate file in constructor
            self._sslCert = sslCer

        # any user credentials loaded from the config file can be over-ridden from credentials supplied as constructor parameters
        if username:
            self.username = username
        if password:
            self.password = password

        # with the given user credentials, we try and logon to the API service to retrieve a token for use with all subsequent queries
        # Must be some credentials supplied and not the stub credentials
        if isinstance(self.username, str) and len(self.username) > 0 and self.username != 'YourID' and isinstance(self.password, str) and len(self.password) > 0:
            self._get_Token()
        else:
            raise Exception("You must supply some user credentials.")


    def _get_Token(self):
        """
        _get_Token uses you credentials to try and obtain a token to be used in subsequent request for data. The returned token is valid for 24 hours
        """
        try:
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_Token', 'Requesting new token.')
            token_url = self.url + 'GetToken'
            tokenReq = { "Password" : self.password,
                         "Properties" : [{ "Key" : "__AppId", "Value" : self._appID}],
                         "UserName" : self.username}
            #Post Token Request
            json_Response = self._get_json_Response(token_url, tokenReq)
            self.tokenExpiry = DSEconomicFiltersDateFuncs.jsonDateTime_to_datetime(json_Response['TokenExpiry'])
            self.token = json_Response['TokenValue']
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_Token', 'New token received.')
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_Token', 'Exception occured.', exp)
            raise exp

    def IsValid(self):
        return isinstance(self.token, str) and len(self.token) > 0 and isinstance(self.tokenExpiry, datetime)

    def Check_Token(self):
        if not self.IsValid():
            raise Exception("You are not logged on. Please recreate the DatastreamEconomicFilters client supplying valid user credentials.")
        # A function called before every query to check and renew the token if within 15 minutes of expiry time or later
        timeRenew = datetime.utcnow() + timedelta(minutes = 15) # curiously utcnow() method doesn't set the time zone to utc. We need to do so to compare with token.
        timeRenew = datetime(timeRenew.year, timeRenew.month, timeRenew.day, timeRenew.hour, timeRenew.minute, timeRenew.second, 0, tzinfo=pytz.utc)
        if self.tokenExpiry <= timeRenew : 
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogTrace, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.Check_Token', 'Token has expired. Refrefreshing')
            self._get_Token()


    def _json_Request(self, reqObject):
        # An internal method to convert the request object into JSON for sending to the API service
        try:
            #convert the dictionary (raw text) to json text first, encoding any datetimes as json /Date() objects
            jsonText = json.dumps(reqObject, cls = DSEconFilterJsonDateTimeEncoder)
            byteTemp = bytes(jsonText,'utf-8')
            byteTemp = jsonText.encode('utf-8')
            #convert the json Text to json formatted Request
            jsonRequest = json.loads(byteTemp)
            return jsonRequest
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._json_Request', 'Exception occured:', exp)
            raise exp


    def _get_Response(self, reqUrl, raw_request):
        # An internal method to perform a request against the API service.
        #convert raw request to json format before post
        jsonRequest = self._json_Request(raw_request)

        # post the request
        DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogTrace, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_Response', 'Starting web request:', raw_request)
        if self._sslCert:  # user supplied a specific certificate file
            http_Response = self._reqSession.post(reqUrl, json = jsonRequest,  proxies = self._proxies, cert = self._sslCert, timeout = self._timeout)
        else:
            http_Response = self._reqSession.post(reqUrl, json = jsonRequest,  proxies = self._proxies, verify = self._certfiles, timeout = self._timeout)
        return http_Response

        
    def _get_json_Response(self, reqUrl, raw_request):
        # This method makes the query and does some basic error handling
        try:
            # convert the request to json and post the request
            httpResponse = self._get_Response(reqUrl, raw_request)

            # check the response
            if httpResponse.ok:
                json_Response = dict(httpResponse.json())
                DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogTrace, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_json_Response', 'Web response received:', json_Response)
                return json_Response
            elif httpResponse.status_code == 400 or httpResponse.status_code == 403:
                # possible DSFault exception returned due to permissions, etc
                try:
                    tryJson = json.loads(httpResponse.text)
                    if 'Message' in tryJson.keys() and 'Code' in tryJson.keys():
                        faultDict = dict(tryJson)
                        DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_json_Response', 'API service returned a DSFault:', 
                                                            faultDict['Code'] + ' - ' + faultDict['Message'])
                        raise DSEconomicsFault(faultDict)
                except json.JSONDecodeError as jdecodeerr:
                    pass
            # unexpected response so raise as an error
            httpResponse.raise_for_status()
        except json.JSONDecodeError as jdecodeerr:
            DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_json_Response', 'JSON decoder Exception occured:', jdecodeerr.msg)
            raise
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters._get_json_Response', 'Exception occured:', exp)
            raise
 

    def __CheckConstituents(self, constituents, updateAction):
        # We perform some basic sanity checks on the constituents sent to the service
        if updateAction < DSFilterUpdateActions.UpdateDescription: # must have some constituents for create, append, replace or delete
            if constituents == None or not isinstance(constituents, list):
                return 'The filter Constituents property must be a list containing at least one economic series with a maximum limit of 100K items.'
            if len(constituents) == 0 or len(constituents) > 100000:
                return 'The filter Constituents property must contain at least one economic series with a maximum limit of 100K items.'
        elif constituents != None and not isinstance(constituents, list): #update description or share type must provide None or at least a list of series (ignored)
           return 'The filter Constituents property must be a list object.'
        return None

       
    def __CheckFilterId(self, filterId):
        # The requested filter ID must match the specification of between 5 and 45 alphanumeric or underscore characters
        if filterId == None or not re.match('^[A-Z0-9_]{5,45}$', filterId, re.I):
            return 'The filter identifier must be between 5 and 45 characters long and contain only alphanumeric or underscore characters.'
        return None #valid

          
    def __VerifyEconomicFilter(self, econFilter, updateAction, isCreate):
        # must be a DSEconomicsFilter and the filer ID and constituents must be valid
        if not isinstance(econFilter, DSEconomicsFilter):
            return 'DatastreamEconomicFilters CreateFilter or ModifyFilter methods require a valid DSEconomicsFilter instance.'
        if not isCreate and (not isinstance(updateAction, DSFilterUpdateActions) or updateAction == DSFilterUpdateActions.CreateFilter):
            return 'DatastreamEconomicFilters ModifyFilter cannot be called with the CreateFilter flag.'

        # must have valid Id and some constituents
        resp = self.__CheckFilterId(econFilter.FilterId)
        if resp is None:
            ## check constituents if appending replacing or removing
            resp = self.__CheckConstituents(econFilter.Constituents, updateAction)

        # finally ensure other fields which are only set on returning a response are valid defaults for the subsequent web query
        if resp is None:
            econFilter.SetSafeUpdateParams()
        return resp  # will contain an error message if invalid params else None


    def GetAllFilters(self, getType = DSFilterGetAllAction.AllFilters):
        """ GetAllFilters returns all the current filters you can use in queries for economic changes and corrections

            Example usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            # query for all your filters
            filtersResp = econFilterClient.GetAllFilters(DSFilterGetAllAction.AllFilters)
            if filtersResp:
                if filtersResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    # Your Datastream Id might not be permissioned for managing economic filters on this API
                    print('GetAllFilters failed with error ' + filtersResp.ResponseStatus.name + ': ' + filtersResp.ErrorMessage)
                elif filtersResp.Filters and filtersResp.FilterCount > 0:
                    # You do have access to some filters
                    filters = [[filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.ConstituentsCount, 
                                filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description] for filter in filtersResp.Filters]
                    df = pd.DataFrame(data=filters, columns=['FilterId', 'OwnerId', 'Shared', 'Constituents', 'LastModified', 'Description'])
                    print(df.to_string(index=False))
                else:
                    # You do not have any filters with the specified filter type. Try DSFilterGetAllAction.AllFilters which should return
                    # the REFINITIVCC_KEYIND_GLOBAL global filter available for download 
                    print('GetAllFilters returned zero filters for the authenticated user with the specified DSFilterGetAllAction')
        """

        try:
            if not isinstance(getType, DSFilterGetAllAction):
                resp = DSEconomicsFilterGetAllResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterFormatError
                resp.ErrorMessage = 'DatastreamEconomicFilters GetAllFilters method requires a valid DSFilterGetAllAction type.'
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetAllFilters', 'Error: ' + resp.ErrorMessage)
                return resp

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetAllFilters', 'GetAllFilters requested.')
            self.Check_Token() # check and renew token if within 15 minutes of expiry
            allFilters_url = self.url + 'GetAllFilters'
            raw_request = { "GetTypes" : getType,
                            "Properties" : None,
                            "TokenValue" : self.token}
            json_Response = self._get_json_Response(allFilters_url, raw_request)
            response = DSEconomicsFilterGetAllResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetAllFilters', 'GetAllFilters returned response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetAllFilters', 'Exception occured.', exp)
            raise exp


    def GetFilter(self, filterId):
        """ GetFilter returns the details for an individual filter

            Example usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            filterResp = econFilterClient.GetFilter('REFINITIVCC_KEYIND_GLOBAL')
            if filterResp:
                if filterResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('GetFilter failed for filter REFINITIVCC_KEYIND_GLOBAL with error ' + filterResp.ResponseStatus.name + ': ' + filterResp.ErrorMessage)
                elif filterResp.Filter != None:
                    filter = filterResp.Filter
                    names = ['FilterId', 'OwnerId', 'Shared?', 'LastModified', 'Description', 'No. of Constituents']
                    data = [filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description, filter.ConstituentsCount]
                    df = pd.DataFrame(data, index=names)
                    print(df)

                    print('Constituents:')
                    df = pd.DataFrame(filter.Constituents)
                    print(df, end='\n\n')
        """
        try:
            # check validity of requested filter Id
            filterchk = self.__CheckFilterId(filterId)
            if filterchk is not None:
                resp = DSEconomicsFilterResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterFormatError
                resp.ErrorMessage = filterchk
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetFilter', 'Error: ' + filterchk)
                return resp

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetFilter', 'Requesting filter ' + filterId)
            self.Check_Token() # check and renew token if within 15 minutes of expiry
            filter_url = self.url + 'GetFilter'
            raw_request = { "TokenValue" : self.token,
                            "FilterId" : filterId,
                            "Properties" : None}
            json_Response = self._get_json_Response(filter_url, raw_request)
            response = DSEconomicsFilterResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetFilter', 'Filter ' + filterId + ' returned a response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetFilter', 'Exception occured.', exp)
            raise exp


    def CreateFilter(self, newFilter):
        """ CreateFilter allows you to create a custom filter

            Example usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            newFilter = DSEconomicsFilter()
            newFilter.FilterId = 'MyTestFilter'
            newFilter.Constituents = ['CTES85FTA','EOES85FTA','ESES85FTA', 'FNES85FTA']
            newFilter.Description = 'MyTestFilter for testing'
            filterResp = econFilterClient.CreateFilter(newFilter)
            if filterResp:
                if filterResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('CreateFilter failed with error ' + filterResp.ResponseStatus.name + ': ' + filterResp.ErrorMessage)
                elif filterResp.Filter != None:
                    filter = filterResp.Filter
                    names = ['FilterId', 'OwnerId', 'Shared?', 'LastModified', 'Description', 'No. of Constituents']
                    data = [filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description, filter.ConstituentsCount]
                    df = pd.DataFrame(data, index=names)
                    print(df)

                    print('Constituents:')
                    df = pd.DataFrame(filter.Constituents)
                    print(df, end='\n\n')

                    if filterResp.ItemErrors and len(filterResp.ItemErrors):
                    print('Some constituents were not added due to invalid format or they do not exist :')
                    df = pd.DataFrame(filterResp.ItemErrors)
                    print(df, end='\n\n')
        """
        try:
            #pre check the validity of the filter that needs to be created
            filterchk = self.__VerifyEconomicFilter(newFilter, DSFilterUpdateActions.CreateFilter, True)
            if filterchk is not None:
                resp = DSEconomicsFilterResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterFormatError
                resp.ErrorMessage = filterchk
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.CreateFilter', 'Error: ' + filterchk)
                return resp

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.CreateFilter', 'Creating filter ' + newFilter.FilterId)
            self.Check_Token() # check and renew token if within 15 minutes of expiry

            create_url = self.url + "CreateFilter"
            raw_request = { "Filter" : newFilter.__dict__,
                            "Properties" : None,
                            "TokenValue" : self.token,
                            "UpdateAction" : DSFilterUpdateActions.CreateFilter}
            json_Response = self._get_json_Response(create_url, raw_request)
            response = DSEconomicsFilterResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.CreateFilter', 'Filter ' + newFilter.FilterId + ' returned a response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.CreateFilter', 'Exception occured.', exp)
            raise exp


    def UpdateFilter(self, filter, updateAction):
        """ UpdateFilter allows you to update an existing custom filter

            Example usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            newFilter = DSEconomicsFilter()
            newFilter.FilterId = 'MyTestFilter'  # assumes the filter already exists
            newFilter.Constituents = ['FRES85FTA', 'GRES85FTA', 'HNES85FTA', 'POES85FTA']
            filterResp = econFilterClient.UpdateFilter(newFilter, DSFilterUpdateActions.AppendConstituents)
            if filterResp:
                if filterResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('UpdateFilter failed with error ' + filterResp.ResponseStatus.name + ': ' + filterResp.ErrorMessage)
                elif filterResp.Filter != None:
                    filter = filterResp.Filter
                    names = ['FilterId', 'OwnerId', 'Shared?', 'LastModified', 'Description', 'No. of Constituents']
                    data = [filter.FilterId, filter.OwnerId, 'Yes' if bool(filter.Shared) else 'No', filter.LastModified.strftime('%Y-%m-%d %H:%M:%S'), filter.Description, filter.ConstituentsCount]
                    df = pd.DataFrame(data, index=names)
                    print(df)

                    print('Constituents:')
                    df = pd.DataFrame(filter.Constituents)
                    print(df, end='\n\n')

                    if filterResp.ItemErrors and len(filterResp.ItemErrors):
                    print('Some constituents were not added due to invalid format or they do not exist :')
                    df = pd.DataFrame(filterResp.ItemErrors)
                    print(df, end='\n\n')
        """
        try:
            #pre check the validity of the filter that needs to be created
            filterchk = self.__VerifyEconomicFilter(filter, updateAction, False)
            if filterchk is not None:
                resp = DSEconomicsFilterResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterFormatError
                resp.ErrorMessage = filterchk
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.UpdateFilter', 'Error: ' + filterchk)
                return resp

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.UpdateFilter', 'Updating filter ' + filter.FilterId)
            self.Check_Token() # check and renew token if within 15 minutes of expiry

            update_url = self.url + 'UpdateFilter'
            raw_request = { "Filter" : filter.__dict__,
                            "Properties" : None,
                            "TokenValue" : self.token,
                            "UpdateAction" : updateAction}
            json_Response = self._get_json_Response(update_url, raw_request)
            response = DSEconomicsFilterResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.UpdateFilter', 'Filter ' + filter.FilterId + ' returned a response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.UpdateFilter', 'Exception occured.', exp)
            raise exp

    
    def DeleteFilter(self, filterId):
        """ DeleteFilter allows you to delete an existing custom filter

            Example usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            filterResp = econFilterClient.DeleteFilter('MyTestFilter') # assumes the filter already exists
            if filterResp:
                if filterResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('DeleteFilter failed with error ' + filterResp.ResponseStatus.name + ': ' + filterResp.ErrorMessage)
                else: # No filter object will be returned
                    print('The filter was successfully deleted.')
        """
        try:
            # check validity of requested filter Id
            filterchk = self.__CheckFilterId(filterId)
            if filterchk is not None:
                resp = DSEconomicsFilterResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterFormatError
                resp.ErrorMessage = filterchk
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.DeleteFilter', 'Error: ' + filterchk)
                return resp

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.DeleteFilter', 'Deleting filter ' + filterId)
            self.Check_Token() # check and renew token if within 15 minutes of expiry

            delete_url = self.url + 'DeleteFilter'
            raw_request = { "FilterId" : filterId,
                            "Properties" : None,
                            "TokenValue" : self.token}

            json_Response = self._get_json_Response(delete_url, raw_request)
            response = DSEconomicsFilterResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.DeleteFilter', 'DeleteFilter (' + filterId + ') returned a response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.DeleteFilter', 'Exception occured.', exp)
            raise exp


    def GetEconomicChanges(self, startDate = None, sequenceId = 0, filter = None):
        """ GetEconomicChanges allows you to query for any economic changes and corrections, returning a DSEconomicChangesResponse if successful.

        There are two modes of usage:
        1) Get sequence ID for changes on or after a given date. The service supports querying for changes from a given date up to 28 days in the past.
           Supplying a timestamp will query for the sequence ID to use in subsequent queries to retrieve any changes. The query returns a boolean property
           indicating if there are any updates available and also returns the number of outstanding updates available using the returned sequence ID 
           in the PendingCount property of the response.

           The earliest sequence returned will always be a maximum of 28 days in the past. If you supply no datetime, and the sequenceID is left as 0 (default),
           then the returned sequence ID will represent the first update from midnight on the prior working weekday (e.g. request on a Monday, and the 
           startDate will be assumed to be 00:00:00 on the prior Friday). Request with a date in the future will return the sequence ID for the next update 
           that will occur in the future.

           Example Usage:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            # supplying no datetime will search for updates from the start of the prior working (week)day.
            updatesResp = econFilterClient.GetEconomicChanges() # Get sequence ID for any updates beginning the previous working weekday
            # alternatively requesting sequence for any changes that occurred from 5 days ago
            updatesResp = econFilterClient.GetEconomicChanges(datetime.today() - timedelta(days=5)) # Get sequence ID starting 5 days ago

            # the above should tell us the start sequence ID for updates from the given start datetime and how many updates we have pending
            sequenceId = 0
            if updatesResp:
                if updatesResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('GetEconomicChanges failed with error ' + updatesResp.ResponseStatus.name + ': ' + updatesResp.ErrorMessage)
                else:
                    print('GetEconomicChanges returned the first update sequence as {}.'.format(updatesResp.NextSequenceId))
                    print('You have {} updates pending starting from {}.'.format(updatesResp.PendingCount, updatesResp.NextSequenceId))
                    sequenceId = updatesResp.NextSequenceId

        2) With a given sequence ID, retrieve all the series that updated after the given sequence ID. Note the supplied startDate must be None. This will return a chain
           of responses with each response containing up to 10K updates and the next sequence in the chain to request. Whilst each response returns UpdatesPending
           as True, there are more updates to be requested. When UpdatesPending is returned as False it indicates that the given response is the last response with
           updates. The NextSequenceId property in the final update is the next ID that will be assigned on any subsequent new updates occurring. It should be used in 
           polling for updates at a minimum frequency of every 10 minutes.

           The request also accepts an optional custom filter to restrict the list of returned updates to just the series that comprise the constituents of the filter.

            Example usage without a filter:
            # first logon with your credentials. Creating a DatastreamEconomicFilters instance with your credentials automatically logs on for you 
            econFilterClient = DatastreamEconomicFilters(None, 'YourID', 'YourPwd')
            # using a sequence ID retrieved using the first mode of requesting GetEconomicChanges
            updatesResp = econFilterClient.GetEconomicChanges(None, sequenceId)
            if updatesResp:
                if updatesResp.ResponseStatus != DSFilterResponseStatus.FilterSuccess:
                    print('GetEconomicChanges failed with error ' + updatesResp.ResponseStatus.name + ': ' + updatesResp.ErrorMessage)
                else:
                    # You have some updates; process them.
                    print ('You have {} new updates:'.format(updatesResp.UpdatesCount))
                    updates = [[update.Series, update.Frequency.name, update.Updated.strftime('%Y-%m-%d %H:%M:%S')] for update in updatesResp.Updates]
                    df = pd.DataFrame(data=updates, columns=['Series', 'Frequency', 'Updated'])
                    print(df, end='\n\n')
                    if updatesResp.UpdatesPending:
                        print ('You still have {} updates pending starting from new sequence ID {}.'.format(updatesResp.PendingCount, updatesResp.NextSequenceId))
                    else:
                        print ('You have no more updates pending. Use the new sequence {} to poll for future updates.'.format(updatesResp.NextSequenceId))

            Example usage with a filter which will return a smaller refined subset of updates restricted to the constituents of the filter
            updatesResp = econFilterClient.GetEconomicChanges(None, sequenceId, 'REFINITIVCC_KEYIND_GLOBAL')
            # and process as above

        """
        try:
            reqCheck = None
            # check validity of inputs
            if startDate is not None:
                if not (isinstance(startDate, date) or isinstance(startDate, datetime)):
                    reqCheck = 'startDate, if supplied, must be a date or datetime object.'
            elif sequenceId is not None:
                if not isinstance(sequenceId, int):
                    reqCheck = 'sequenceId, if supplied, must be an integer specifying the start sequence for updates.'
                elif sequenceId > 0 and (filter is not None) and not isinstance(filter, str):
                    reqCheck = 'filter, if supplied, must be a string specifying the filter of constituents to check for updates against.'
            # return an error response if we encountered any invalid inputs
            if reqCheck is not None:
                resp = DSEconomicChangesResponse()
                resp.ResponseStatus = DSFilterResponseStatus.FilterError
                resp.ErrorMessage = reqCheck
                DSEconomicFiltersLogFuncs.LogError('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetEconomicChanges', 'Error: ' + reqCheck)
                return resp

            stringReq = None
            if startDate is not None:
                stringReq = 'Requesting sequence ID for updates from ' + startDate.strftime('%Y-%m-%d %H:%M:%S') + '.'
            elif isinstance(sequenceId, int) and sequenceId > 0:
                stringReq = 'Requesting updates from sequence ID {}'.format(sequenceId)
                if isinstance(filter, str) and len(filter) > 0:
                    stringReq = stringReq + ' with filter {}.'.format(filter)
                else:
                    stringReq = stringReq + '.'
            else: # no parameters at all requests the default
                stringReq = 'Requesting default updates sequence (from prior working day).'

            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetEconomicChanges', stringReq)
            self.Check_Token() # check and renew token if within 15 minutes of expiry

            filter_url = self.url + 'GetEconomicChanges'
            raw_request = { "TokenValue" : self.token,
                            "StartDate" : startDate,
                            "SequenceId" : sequenceId if (startDate is None) and isinstance(sequenceId, int) else 0,
                            "Filter" : filter if (startDate is None) and isinstance(sequenceId, int) and sequenceId > 0 else None,
                            "Properties" : None}

            json_Response = self._get_json_Response(filter_url, raw_request)
            response = DSEconomicChangesResponse(json_Response)
            DSEconomicFiltersLogFuncs.LogDetail(DSEconomicFiltersLogLevel.LogInfo, 'DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetEconomicChanges', 'GetEconomicChanges request returned a response.')
            return response
        except Exception as exp:
            DSEconomicFiltersLogFuncs.LogException('DatastreamEconomicFilters.py', 'DatastreamEconomicFilters.GetEconomicChanges', 'Exception occured.', exp)
            raise exp

            




