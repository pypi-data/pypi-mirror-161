# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division


#from datetime import datetime, timedelta
try:
    from pandas.tseries.resample import TimeGrouper
except ImportError: 
    from pandas.core.resample import TimeGrouper
import pandas as pd
import numpy as np
import isodate
from datetime import datetime, tzinfo, timedelta
from functools import reduce
import calendar


def read_dis(disc):
    """ read a MODFLOW discretzation file """

    with open(disc) as fp:
        lines = fp.readlines()

        #skip set0 & comments
        l = 0
        while lines[l][0] == "#":
            l += 1

        #dataset1
        set1 = lines[l][:lines[l].find("#")].split()
        l += 1
        NLAY = int(set1[0])
        NROW = int(set1[1])
        NCOL = int(set1[2])
        NPER = int(set1[3])
        ITMUNI = int(set1[4])
        LENUNI = int(set1[5])

        #skip set0 & comments
        while lines[l][0] == "#":
            l += 1

        #dataset2
        set2 = lines[l][:lines[l].find("#")].split()
        l += 1
        LAYCB = int(set2[0])

        #skip set0 & comments
        while lines[l][0] == "#":
            l += 1

        #dataset3
        DELR = None
        matrix = []
        if lines[l].find("CONSTANT") >= 0:
            DELR = int(float(lines[l][:lines[l].find("#")].split()[-1]))
            l += 1
        elif lines[l].find("EXTERNAL") >= 0 or lines[l].find("OPEN/CLOSE") >= 0:
            l += 1  # this is not implemented, just skipped
        else:  # includes with or without INTERNAL in format line
            if lines[l].find("INTERNAL") >= 0:
                l += 1
            while DELR is None:
                matrix += lines[l][:lines[l].find("#")].split()
                l += 1
                if len(matrix) >= NCOL:
                    DELR = matrix

        #skip set0 & comments
        while lines[l][0] == "#":
            l += 1

        #dataset4
        DELC = None
        matrix = []
        if lines[l].find("CONSTANT") >= 0:
            DELC = int(float(lines[l][:lines[l].find("#")].split()[-1]))
            l += 1
        elif lines[l].find("EXTERNAL") >= 0 or lines[l].find("OPEN/CLOSE") >= 0:
            l += 1  # this is not implemented, just skipped
        else:  # includes with or without INTERNAL in format line
            if lines[l].find("INTERNAL") >= 0:
                l += 1
            while DELC is None:
                matrix += lines[l][:lines[l].find("#")].split()
                l += 1
                if len(matrix) >= NROW:
                    DELC = matrix

        #skip set0 & comments
        while lines[l][0] == "#":
            l += 1

        #dataset5
        TOP = None
        matrix = []
        if lines[l].find("CONSTANT") >= 0:
            TOP = int(lines[l][:lines[l].find("#")].split()[-1])
            l += 1
        elif lines[l].find("EXTERNAL") >= 0 or lines[l].find("OPEN/CLOSE") >= 0:
            l += 1  # this is not implemented, just skipped
        else:
            if lines[l].find("INTERNAL") >= 0:
                l += 1
            while TOP is None:
                matrix += lines[l][:lines[l].find("#")].split()
                l += 1
                if len(matrix) >= NCOL * NROW:
                    TOP = matrix

        #skip set0 & comments
        while lines[l][0] == "#":
            l += 1

        #dataset6
        BOTM = [None] * (NLAY + LAYCB)
        for i in range(NLAY + LAYCB):
            matrix = []
            if lines[l].find("CONSTANT") >= 0:
                BOTM[i] = int(lines[l][:lines[l].find("#")].split()[-1])
                l += 1
            elif lines[l].find("EXTERNAL") >= 0 or lines[l].find("OPEN/CLOSE") >= 0:
                l += 1  # this is not implemented, just skipped
            else:
                if lines[l].find("INTERNAL") >= 0:
                    l += 1
                while BOTM[i] is None:
                    matrix += lines[l][:lines[l].find("#")].split()
                    l += 1
                    if len(matrix) >= NCOL * NROW:
                        BOTM[i] = matrix

            #skip set0 & comments
            while lines[l][0] == "#":
                l += 1

        #dataset7
        set7 = []  # stress periods length index 0 = SP1
        while l < len(lines):
            set7.append(lines[l][:lines[l].find("#")].split())
            l += 1
        set7c = zip(*set7)

        #print("====")
        #print(set7)
        #print("====")
        #print(set7c)
        #print("====")

        PERLEN = [float(a) for a in set7c[0]]
        NSTP = [int(a) for a in set7c[1]]
        TSMULT = [float(a) for a in set7c[2]]
        SSTR = set7c[3]

        #print(PERLEN)
        return PERLEN


def get_startdate(startdate):
    """ convert start date from text to datetime object """
    try:
        ts_parse = datetime.strptime(startdate, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        try:
            import dateutil.parser
            ts_parse = dateutil.parser.parse(startdate).replace(tzinfo=None)
        except:
            raise Exception("'startdate' input value is not correct")
    return ts_parse


def sensors_to_istsos(service, procedure, obspro_sensor, offering="temporary",
                    temporalFilter=None, basic_auth=None,
                    qualityIndex=True, nan_qi=0, how_merge='outer', period=None, time_zone=None,
                    delta=timedelta(days=7), verbose=False, test_only=False):

    """Merge sensors and load data to a procedure on an istsos server instance

    Args:
        service (str): url of the SOS service
        procedure (list): sensor name
        obspro_sensor (dict): dictionary of observed property definition key and OAT sensor value
                              - e.g.:
                              {'urn:x-def:ist:meteo:ait:temparature': trev1,
                               'urn:x-def:ist:meteo:ait:temparature:max': trev_max,}
        offering (str): name of the offering - default value is \'temporary\'
        basic_auth(tuple): touple of username and password - e.g.: ('utente','123')
        qualityIndex (bool): if True istSOS qualityIndex is uploaded to istSOS
        nan_qi (int): values to be used as quality index in case of null values
        how_merge (str): specific merge options: {'left', 'right', 'outer', inner}, default 'outer'
                   * left: use only keys from left frame (SQL: left outer join)
                   * right: use only keys from right frame (SQL: right outer join)
                   * outer: use union of keys from both frames (SQL: full outer join)
                   * inner: use intersection of keys from both frames (SQL: inner join)
       time_zone (str): the time-zone to apply to series, default is UTC or time-zone of first sensor
       delta (timedelta): chunk time size for insert observation requests in datetime.timedelta
                    !warning!: no undo options if a chuck fail! (default 7 days)
        verbose (bool): if True print out the final request for data insert (default False)
        test_only (bool): if True do not upload new data (default False)
    """

    try:
        import requests
        import json
        #from io import StringIO
        import pandas as pd

    except ImportError:
        raise ImportError('<requests> package not installed')

    #prepare useful variables
    service = service.rstrip("/")
    url = "/".join(service.split("/")[:-1])
    instance = service.split("/")[-1]

    if basic_auth:
        if len(basic_auth) == 2:
            sos_auth = requests.auth.HTTPBasicAuth(basic_auth[0], basic_auth[1])
        else:
            raise ValueError('<basic_auth> tuple numerosity is TWO')
    else:
        sos_auth = None

    # Load procedure description and get observedProperties & assignedSensorId
    ###########################################################################
    res = requests.get("%s/wa/istsos/services/%s/procedures/%s" % (
              url,
              instance,
              procedure
              ), auth=sos_auth, verify=False)
    try:
        data = res.json()
    except Exception as e:
        print(res.text)
        raise e

    if data['success'] is False:
        raise Exception("Description of procedure %s can not be loaded: %s" % (procedure, data['message']))

    data = data['data']

    aid = data['assignedSensorId']  # -> sensor id

    op = []  # -> observed properties
    for out in data['outputs']:
        if qualityIndex is True:
            op.append(out['definition'])
        elif not ':qualityIndex' in out['definition']:
            op.append(out['definition'])

    # Load a getobservation request
    ################################
    res = requests.get("%s/wa/istsos/services/%s/operations/getobservation/offerings/%s/procedures/%s/observedproperties/%s/eventtime/last" % (
        url,
        instance,
        'temporary',
        procedure,
        ','.join(op)
        ), auth=sos_auth, verify=False)

    try:
        data = res.json()
    except Exception as e:
        print(res)
        raise e

    if data['success'] is False:
        raise Exception("Last observation of procedure %s can not be loaded: %s" % (procedure, data['message']))

    # print("RES:",data)
    io_data = data['data'][0]

    jsonindex = {}  # definition:index dict in observation
    ordered_obs = []

    for pos, field in enumerate(io_data['result']['DataArray']['field']):
        if not 'iso8601' in field['definition'] and not ':qualityIndex' in field['definition']:
            ordered_obs.append(field['definition'])

        if 'iso8601' in field['definition']:
            jsonindex[field['definition']] = pos
        elif qualityIndex:
            jsonindex[field['definition']] = pos
        elif not qualityIndex and ':qualityIndex' not in field['definition']:
            jsonindex[field['definition']] = pos

    # Manipulate getObservation response to execute an insertObservation
    ######################################################################

    # Get instant of last observation & set measures to an empty array
    io_data['result']['DataArray']['values'] = []

    #adjust component
    io_comp = []
    for k in io_data['observedProperty']['component']:
        if k in list(jsonindex.keys()):
            io_comp.append(k)
    io_data['observedProperty']['component'] = io_comp

    #adjust len CompositePhenomenon
    io_data['observedProperty']['CompositePhenomenon']['dimension'] = "%s" % len(jsonindex)

    #adjust DataArray fields
    io_data['result']['DataArray']['elementCount'] = "%s" % len(jsonindex)
    io_fields = []
    for k in io_data['result']['DataArray']['field']:
        if k['definition'] in list(jsonindex.keys()):
            io_fields.append(k)
    io_data['result']['DataArray']['field'] = io_fields

    #ordered_ts = [None]*int((len(jsonindex)))  # the ordered list of time series
    #ordered_ts = [None]*int((len(jsonindex)-1)/2)  # the ordered list of time series
    ordered_ts = []

    # Check Observed Properties are all avaiable & prepare the list of time series to be merged
    for uri, pos in list(jsonindex.items()):
        if (not 'iso8601' in uri) and (not ':qualityIndex' in uri):
            if not uri in list(obspro_sensor.keys()):
                raise Exception("Mandatory observed property %s is not present in sensor list." % uri)
    for o in ordered_obs:
        if not o in list(obspro_sensor.keys()):
            raise Exception("Mandatory observed property %s is not present in sensor list." % uri)
        if qualityIndex:
            ordered_ts.append(obspro_sensor[o].ts[['data', 'quality']])
        else:
            ordered_ts.append(obspro_sensor[o].ts[['data']])

    # Merge the time series
    df_final = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how=how_merge
        ), ordered_ts
    )

    # print(df_final, ordered_ts)

    #remove nan in df_final along quality index and convert qi column to integer
    if qualityIndex:
        for c in df_final.columns.values:
            if "quality" in c:
                df_final[c].fillna(nan_qi, inplace=True)
                df_final[c] = df_final[c].astype(int)

    if obspro_sensor[list(obspro_sensor.keys())[0]].tz == 0:
        time_zone = "Z"
    else:
        time_zone = obspro_sensor[list(obspro_sensor.keys())[0]].tz

    # Set sampling Time
    # set naive format if not set
    try:
        # first = isodate.parse_datetime(df_final.index.min().to_pydatetime().isoformat() + time_zone)
        # last = isodate.parse_datetime(df_final.index.max().to_pydatetime().isoformat() + time_zone)
        first = df_final.index.min()
        last = df_final.index.max()
    except Exception as e:
        print(df_final)
        raise e
    if period:
        start, end = period.split("/")
        start = isodate.parse_datetime(start)
        end = isodate.parse_datetime(end)
    else:
        start = first
        end = last

    # order by datetime index (probably unnecessary)
    df_final.sort_index(inplace=True, ascending=True)

    # Split in smaller intervals to reduce load size
    if delta:
        for span_start, span_end in datespan(start, end, delta):
            df_span = df_final.loc[str(pd.Timestamp(span_start)): str(pd.Timestamp(span_end))]

            # set sampling time for data insert
            if time_zone in (span_start).isoformat():
                io_data["samplingTime"] = {
                    "beginPosition": (span_start).isoformat(),
                    "endPosition": (span_end).isoformat(),
                }

                print(io_data["samplingTime"])
                # Set observations to be inserted
                io_data['result']['DataArray']['values'] = [
                    f.split(",") for f in df_span.to_csv(
                        header=False,
                        na_rep=-999.9,
                        date_format="%Y-%m-%dT%H:%M:%S%z").split("\n")
                    ]
                if verbose:
                    print("Values: ", io_data['result']['DataArray']['values'])
            else:
                io_data["samplingTime"] = {
                    "beginPosition": (span_start).isoformat() + time_zone,
                    "endPosition": (span_end).isoformat() + time_zone,
                }

                # Set observations to be inserted
                io_data['result']['DataArray']['values'] = [
                    f.split(",") for f in df_span.to_csv(
                        header=False,
                        na_rep=-999.9,
                        date_format="%Y-%m-%dT%H:%M:%S" + time_zone
                        ).split("\n")
                    ]
            
            if len(io_data['result']['DataArray']['values'][-1]) != len(jsonindex):
                io_data['result']['DataArray']['values'].pop()

            # Send the insertObservation request
            if not test_only:
                res = requests.post("%s/wa/istsos/services/%s/operations/insertobservation" % (
                    url,
                    instance),
                    auth=sos_auth,
                    verify=False,
                    data=json.dumps({
                        "ForceInsert": "true",
                        "AssignedSensorId": aid,
                        "Observation": io_data
                    })
                )

            #Debugging POST request
            if verbose:
                print(json.dumps({
                        "ForceInsert": "true",
                        "AssignedSensorId": aid,
                        "Observation": io_data
                    }))

            # out = res.json()
            try:
                out = res.json()
                print('{} - {} success'.format(span_start, span_end))
            except Exception as e:
                print(res)
                raise e

            if out['success'] is False:
                raise Exception("Procedure %s - %s" % (procedure, out['message']))

    return True

def sensorStats(
        oat, stat='mean', frequency='D', qilist=None, min_obs=None,
        nan_data=np.nan, nan_qi=0, closed='left', label='left',
        column_name=None):

    try:
        aggregations = {
            'data': [stat, 'count'],
            'quality': 'min',
        }
        toat = oat.copy()
        if stat == 'mean':
            grouped = toat.ts.dropna(how='any').groupby(
                TimeGrouper(freq=frequency, closed=closed, label=label)
            ).agg(aggregations)
            col_list = ['data','count']
            df1 = pd.DataFrame(data=None, columns=col_list)
            for i in grouped:
                df1['data'] = grouped[(u'data', 'mean')]
                df1['count'] = grouped[(u'data', 'count')]
        else:
            grouped = toat.ts.dropna(how='any').groupby(
                TimeGrouper(freq=frequency, closed=closed, label=label)
            )
            col_list = list(toat.ts.columns.values)
            col_list.append(u'time')
            df1 = pd.DataFrame(data=None, columns=col_list)
            for i in grouped:
                df = i[1]
                df.loc[:, u'time'] = df.index
                if not df.empty:
                    if stat == 'max':
                        df1.loc[i[0]] = df.loc[df['data'].idxmax()]
                    else:
                        df1.loc[i[0]] = df.loc[df['data'].idxmin()]
            toat.ts = df1
    except Exception as e:
        raise e
    else:

        # extract only data & quality
        if stat == 'mean':
            toat.ts = df1[['data','count']]
        else:
            toat.ts = toat.ts[['data', 'quality', 'time']]
        if column_name:
            if stat == 'mean':
                toat.ts.rename(
                    inplace=True,
                    columns={
                        'data': column_name,
                        'count': '{}_COUNT'.format(column_name)
                    }
                )
            else:
                toat.ts.rename(
                    inplace=True,
                    columns={
                        'data': column_name, 'time': 'TIME_' + column_name
                    }
                )
        toat.freq = frequency

        return toat

def sensorAggergate(oat, aggregation='mean', frequency='D', qilist=None,
                    min_obs=None, nan_data=np.nan, nan_qi=0, closed='right', label='right'):
    """
    Aggregate OAT.sensor according specified parameters

        Args:
            oat (OAT.sensor): OAT.sensor object to be aggregated
            aggregation (str): specific aggregation options: {'max', 'min', 'mean', 'count'}, default 'mean'
            qilist (list): list of quality Index values to select observations used in aggregation
            min_obs (float): minumum number of non null values recorded in the period to calculate the aggregation
                        (note that this percentage includes only valid qualityIndexed measures)
            nan_data (float): value to assign in aggregation when no or insufficient data are available
            nan_qi (int): value to assign in aggregation when no or insufficient data are available,
            closed (str): which side of bin interval is closed: {‘right’, ‘left’}, default 'right'
            label (str): which bin edge label to label bucket with: {‘right’, ‘left’}, default 'right'
    """
    aggregations = {
        'num': 'count',
        'data': aggregation,
        'quality': 'min'
    }

    toat = oat.copy()
    # print('toat:',toat.ts)
    toat.ts['num'] = 1

    if qilist:
        toat.ts = toat.ts[
                    (
                        toat.ts['quality'].isin(qilist)
                        &
                        toat.ts['quality'].notnull()
                    )
                ].groupby(
                    TimeGrouper(freq=frequency, closed=closed, label=label)).agg(
                        aggregations
                        # num='count',data=aggregation,quality='min'
                    )
    else:
        print(
            toat.ts[
                    (
                        toat.ts['quality'].notnull()
                    )
                ].groupby(
                    TimeGrouper(freq=frequency, closed=closed, label=label)).agg(
                        num=pd.NamedAgg(column='num', aggfunc='count'),
                        data=pd.NamedAgg(column='data', aggfunc=aggregation),
                        quality=pd.NamedAgg(column='quality', aggfunc='min'),
                    )
        )
        toat.ts = toat.ts[
                    (
                        toat.ts['quality'].notnull()
                    )
                ].groupby(
                    TimeGrouper(freq=frequency, closed=closed, label=label)).agg(
                        num=pd.NamedAgg(column='num', aggfunc='count'),
                        data=pd.NamedAgg(column='data', aggfunc=aggregation),
                        quality=pd.NamedAgg(column='quality', aggfunc='min'),
                    )

    a = list(toat.ts.columns.values)
    print(a)

    # assign null to non satisfactory
    a[a.index("num")] = 0
    a[a.index("data")] = nan_data
    a[a.index("quality")] = nan_qi
    toat.ts[toat.ts['num'] < min_obs] = a
    # print('TOAT:',toat.ts)

    # extract only data & quality
    toat.ts = toat.ts[['data', 'quality']]
    toat.freq = frequency

    return toat

class Zone(tzinfo):
    """
    Return the tzinfo associated with a string timezone offset - e.g.: '+02:30'
    Example: print datetime.now(Zone('-02:00',False,'GMT'))
    """
    def __init__(self, str_offset, isdst, name):
        """ """
        if str_offset and str_offset != "Z":
            hm = str_offset.split(":")
            if len(hm) == 2:
                self.offset_h = int(str_offset.split(":")[0])
                self.offset_m = int(str_offset.split(":")[1])
            elif len(hm) == 1:
                self.offset_h = int(str_offset.split(":")[0])
                self.offset_m = 0
        else:
            self.offset_h = self.offset_m = 0
        self.isdst = isdst
        self.name = name

    def utcoffset(self, dt):
        """ """
        return timedelta(hours=self.offset_h, minutes=self.offset_m) + self.dst(dt)

    def dst(self, dt):
        """ """
        return timedelta(hours=1) if self.isdst else timedelta(0)

    def tzname(self, dt):
        """ """
        return self.name

    import datetime, calendar

def datedelta(startdate, enddate, no_of_ranges):
    """Find the delta between two dates based on a desired number of ranges

    Args:
        startdate (datetime): start date
        enddate (datetime): end date
        no_of_ranges (int): number of ranges

    Returns:
        timedelta: the timedelta to fit the number of ranges in the period (start-end)
    """    
    start_epoch = calendar.timegm(startdate.timetuple())
    end_epoch = calendar.timegm(enddate.timetuple())

    date_diff = end_epoch - start_epoch

    step = date_diff / no_of_ranges

    return datetime.timedelta(seconds=step)

def datespan(startdate, enddate, delta=timedelta(days=7)):
    """return an iterable of intervals of given delta from start to end

    Args:
        startdate (datetime): start date
        enddate (datetime): end date
        delta (timedelta): desired time span of intervals. Defaults to timedelta(days=7).

    Returns:
        list: an iterable of intervals

    Yields:
        _type_: _description_
    """    
    currentdate = startdate
    while currentdate < enddate:
        todate = (currentdate + delta)
        if todate > enddate:
            todate = enddate
        yield currentdate, todate
        currentdate += delta
        currentdate.replace(hour=0, minute=0,second=0)

def get_istSOS_Procedures(server, service, user=None, pwd=None):
    """Return a list of procedures with basic infos of a set istSOS instance

    Args:
        server (string): the istSOS server url
        service (string): the service instance name
        user (string, optional): The user name. Defaults to None.
        pwd (string, optional): The user password. Defaults to None.

    Returns:
        dict: list of sensors infos
    """    
    try:
        import requests
        import json
    except ImportError as error:
        raise error

    uri = f'{server}/wa/istsos/services/{service}/procedures/operations/getlist'
    try:
        if user and pwd:
            r = requests.get(uri, auth=(user, pwd))
        else:
            r = requests.get(uri)
        if r.status_code == 200:
            r_json = json.loads(r.text)
            return r_json['data']
        else:
            print(r.status_code)
    except Exception as e:
        raise e

def get_istSOS_Geo_Procedures(server, service, user=None, pwd=None, epsg=4326):
    try:
        import requests
        import json
    except ImportError as error:
        raise error

    uri = uri = f"{server}/wa/istsos/services/{service}/procedures/operations/geojson?epsg={epsg}"
    try:
        if user and pwd:
            r = requests.get(uri, auth=(user, pwd))
        else:
            r = requests.get(uri)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print(r.status_code)
    except Exception as e:
        raise e

def filter_procedures(procedures,field,operator,value):
    """return a list of procedures matching the filter"""
    operators = ['=','>','>=','<','<=','!=']
    if operator == '=':
        return list(filter(lambda x: x[field] == value, procedures))
    elif operator == '>':
        return list(filter(lambda x: x[field] > value, procedures))
    elif operator == '>=':
        return list(filter(lambda x: x[field] >= value, procedures))
    elif operator == '<':
        return list(filter(lambda x: x[field] < value, procedures))
    elif operator == '<=':
        return list(filter(lambda x: x[field] <= value, procedures))
    elif operator == '!=':
        return list(filter(lambda x: x[field] != value, procedures))
    else:
        raise ValueError(f'operator not in {operators}')

# def sensor_to_sta(service, sensor, properties=None, location=None, uom=None):
#     """Push a sensor to SensorThingsAPI service

#     Args:
#         service (string): the SensorThingsAPI endpoint url
#         thing (dict): a dict with 
#         properties (dict): a dict of sensor characteristics. Default is None
#         location (dict): location a dict with keys (name,description)
#         uom (dict): unit of measure dict with keys (name, symbol, definition)
#     """    
#     """
#     """
#     stadict = {}
#     # Thing
#     stadict['name'] = sensor.name
#     stadict['description'] = sensor.desc
#     if properties:
#         stadict['properties'] = properties
#     # location
#     if location:
#         stadict['Locations'] = [{
#             "name": location['name'],
#             "description": location['description'],
#             "encodingType": "application/vnd.geo+json",
#             "location": {
#                 "type": "Point",
#                 "coordinates": [sensor.lat, sensor.lon, sensor.alt]
#             }
#         }]
#     else:
#         stadict['Locations'] = [{
#             "name": f"{sensor.name}",
#             "description": f"Location of the {sensor.name}",
#             "encodingType": "application/vnd.geo+json",
#             "location": {
#                 "type": "Point",
#                 "coordinates": [sensor.lat, sensor.lon]
#             }
#         }]
#     # datastream
#     datastream = {}
#     datastream['name'] = sensor.name + '_stream'
#     datastream['description'] = f"The {sensor.prop} at {sensor.name}"
#     # uom
#     datastream['unitOfMeasurement'] = {}
#     if uom:
#         datastream['unitOfMeasurement']['name'] = uom.name
#         datastream['unitOfMeasurement']['symbol'] = uom.symbol
#         datastream['unitOfMeasurement']['definition'] = uom.definition
#     else:
#         datastream['unitOfMeasurement']['name'] = sensor.unit.encode('utf-8')
#         datastream['unitOfMeasurement']['symbol'] = sensor.unit.encode('utf-8')
#         datastream['unitOfMeasurement']['definition'] = sensor.unit.encode('utf-8')
#     # sensor
#     datastream['sensor'] = {}
#     datastream['sensor']['name'] = sensor.name
#     datastream['sensor']['description'] = sensor.desc
#     datastream['sensor']['encodingType'] = "application/pdf"
#     datastream['sensor']['metadata'] = "https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf"
#     # observedProperty
#     datastream['ObservedProperty'] = {}
#     datastream['ObservedProperty']['name'] = sensor.prop
#     datastream['ObservedProperty']['definition'] = {}
#     datastream['ObservedProperty']['description'] = {}


#     sensor.prop




#     stadict['Datastreams'] = []
#     "name": "Temperature Living Room",
# 			"description": "The temperature in my living room",
# 			"observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
# 			"unitOfMeasurement": {
# 				"name": "Centigrade",
# 				"symbol": "C",
# 				"definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCentigrade"
# 			},
# 			"Sensor": {
# 				"name": "DHT22/Temperature",
# 				"description": "Temperature sensor of a DHT22",
# 				"encodingType": "application/pdf",
# 				"metadata": "https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf"
# 			},
# 			"ObservedProperty": {
# 				"name": "Temperature",
# 				"definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#ThermodynamicTemperature",
# 				"description": "The temperature."
# 			},
    
    

