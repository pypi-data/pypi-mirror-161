# Adapted from https://coast.noaa.gov/data/marinecadastre/ais
import time
import math
import datetime
import json
import geojson
from pandas import DataFrame
from logging import getLogger
from typing import List, Dict

LOG = getLogger('transmap')


# subclass JSONEncoder
class DateTimeEncoder(json.JSONEncoder):
    # Override the default method
    # When dumping datetime fields, serialization fails
    # This custom encoder is supposed to fix that issue
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class TrackBuilder():
    def __init__(self, points: List[Dict], max_time: int = 30, max_distance: int = 1):
        self.maxTime = max_time
        self.maxDistance = max_distance
        self.points = points
        self._features = []
        self.idField = 'MMSI'
        self.dtField = 'BaseDateTime'

    @property
    def features(self) -> List[Dict]:
        return self._features

    @features.setter
    def features(self, val):
        self._features = val

    def to_dataframe(self) -> DataFrame:
        return DataFrame(self.features)

    def _convert_to_geojson(self, feature: Dict) -> Dict:
        polyline = {
            'type': 'LineString',
            'coordinates': feature.get('coordinates', [])
        }
        exclude = ['coordinates']
        polyline['properties'] = {k: v for k,
                                  v in feature.items() if k not in exclude}
        return polyline

    def to_geojson(self) -> geojson.FeatureCollection:
        return geojson.loads(json.dumps({
            'type': 'FeatureCollection',
            'features': list(map(self._convert_to_geojson, self.features))
        }, cls=DateTimeEncoder))

    def create_tracks(self):
        """
        Main function that calls all of the other functions.
        Determines which functions are run, based on the user selected parameters.
        """

        # Create Dictionary of broadcast data Key = ID, Value = Dictionary of {DateTime:[x,y,voyageID]}
        dataDicAIS, dataDicAttrs = self.create_data_dict()

        self.add_lines_segmented(dataDicAIS, dataDicAttrs)
        return self

    def create_data_dict(self) -> tuple:
        """
        Process to read through the input point feature class.
        Point information is stored in a Python dictionary in memory.
        Points are read using the Data Access Module search cursor.
        """
        LOG.debug("Reading input point data...")

        a0 = time.time()

        dataDicAIS = {}
        dataDicAttrs = {}

        for row in self.points:
            pnt = row.get('location', None)
            if not pnt:
                continue

            sID = row.get('MMSI', None)
            if not sID:
                continue

            date_time = row.get('BaseDateTime', None)
            if not date_time:
                continue
            if not isinstance(date_time, datetime.datetime):
                date_time = datetime.datetime.strptime(
                    date_time, "%Y-%m-%dT%H:%M:%S")

            dDateTime = date_time
            dataDicAIS[sID] = dataDicAIS.get(sID, {})
            dataDicAIS[sID][dDateTime] = [pnt[0], pnt[1]]

            if dataDicAttrs.get(sID, None) is None:
                dataDicAttrs[sID] = row

        a1 = time.time() - a0
        LOG.debug("CreateDataDict Time: {0}".format(a1/60))
        return dataDicAIS, dataDicAttrs

    def add_lines_segmented(self, dataDicAIS, dataDicAttrs):
        lineArray = []

        t0 = time.time()

        for key in sorted(dataDicAIS.keys()):
            # list of date time dictionary keys
            dtTimes = sorted(dataDicAIS[key].keys())

            dtSegStart = None
            dtSegEnd = None

            # skip MMSI if there is only one point provided
            if len(dtTimes) > 1:
                for i in range(0, len(dtTimes)-1):
                    pnt1 = (dataDicAIS[key][dtTimes[i]][0],
                            dataDicAIS[key][dtTimes[i]][1])

                    pnt2 = (dataDicAIS[key][dtTimes[i+1]][0],
                            dataDicAIS[key][dtTimes[i+1]][1])

                    distance = self.get_distance(pnt1, pnt2)

                    timeDiff = self.get_time_difference(
                        dtTimes[i], dtTimes[i+1])

                    if self._exceeds_threshold(distance, timeDiff):
                        lineArray = []
                        # start and end date variables: start date set with the start of any new line.
                        # end date constantly updated with the second point
                        # so that whenever the line ends the last datetime will already be set.
                        dtSegStart = None
                        dtSegEnd = None
                        continue

                    speed = distance / (timeDiff/60)

                    dtSegStart = dtTimes[i]

                    lineArray.extend([pnt1, pnt2])

                    dtSegEnd = dtTimes[i+1]
                    lineArray = list(set(lineArray))
                    if len(lineArray) > 1:

                        self.features.append(
                            {
                                'coordinates': lineArray,
                                'MMSI': key,
                                'TrackStartTime': dtSegStart,
                                'TrackEndTime': dtSegEnd,
                                'Distance': distance,
                                'Speed': speed,
                                'vessel': dataDicAttrs[key]
                            }
                        )
                        lineArray = []

        t1 = time.time() - t0
        LOG.debug('total Time: {0}'.format(t1 / 60))

    def _exceeds_threshold(self, distance, timeDiff) -> bool:
        # Distance and time thresholds
        beyond_distance_threshold = distance > self.maxDistance
        beyond_time_threshold = timeDiff > self.maxTime
        return beyond_distance_threshold and beyond_time_threshold

    def get_distance(self, point_a: tuple, point_b: tuple) -> float:
        """
        Calculates the distance between two latitude/longitude coordinate pairs,
        using the Vincenty formula for ellipsoid based distances.
        Returns the distance in miles.
        """
        # Vincenty Formula
        # Copyright 2002-2012 Chris Veness
        # http://www.movable-type.co.uk/scripts/latlong-vincenty.html
        prevX, prevY = point_a
        currX, currY = point_b

        a = 6378137
        b = 6356752.314245
        f = 1/298.257223563

        L = math.radians(currX - prevX)
        U1 = math.atan((1-f)*math.tan(math.radians(prevY)))
        U2 = math.atan((1-f)*math.tan(math.radians(currY)))
        sinU1 = math.sin(U1)
        sinU2 = math.sin(U2)
        cosU1 = math.cos(U1)
        cosU2 = math.cos(U2)

        lam = L
        lamP = 9999999999
        iter_count = 0
        while abs(lam-lamP) > 1e-12 and iter_count <= 100:
            sinLam = math.sin(lam)
            cosLam = math.cos(lam)
            sinSigma = math.sqrt((cosU2*sinLam)*(cosU2*sinLam) + (cosU1 *
                                                                  sinU2-sinU1*cosU2*cosLam)*(cosU1*sinU2-sinU1*cosU2*cosLam))

            if sinSigma == 0:
                return 0

            cosSigma = sinU1*sinU2+cosU1*cosU2*cosLam
            sigma = math.atan2(sinSigma, cosSigma)

            sinAlpha = cosU1*cosU2*sinLam/sinSigma
            cosSqAlpha = 1 - sinAlpha*sinAlpha
            if cosSqAlpha == 0:  # catches zero division error if points on equator
                cos2SigmaM = 0
            else:
                cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha

            if cos2SigmaM == None:
                cos2SigmaM = 0

            C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
            lamP = lam
            lam = L+(1-C)*f*sinAlpha*(sigma + C*sinSigma *
                                      (cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))

            iter_count += 1

        uSq = cosSqAlpha*(a*a - b*b)/(b*b)
        A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
        B = uSq/1024*(256+uSq*(-128+uSq*(74-47*uSq)))
        deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM) -
                                                 B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
        s = b*A*(sigma-deltaSigma)
        # a1 = math.atan(cosU2 * sinLam / cosU1 * sinU2 - sinU1 * cosU2 * cosLam)
        # a2 = math.atan(cosU1 * sinLam / -sinU1 *
        #                cosU2 + cosU1 * sinU2 * cosLam)

        # convert s in meters to miles
        s_miles = s*0.0006213712
        return s_miles

    def get_time_difference(self, prevDT, currDT) -> datetime.datetime:
        """Calculates the difference between to date and time variables. The difference is returned in minutes."""
        timeDelta = currDT - prevDT
        totMinutes = (timeDelta.days*1440) + (timeDelta.seconds/60)

        return totMinutes
