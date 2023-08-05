from .models import (
    Lock,
    LockSummary,
    LockCurrentOperations,
    LockInfoChamber,
    LockCurrentQueueSummary,
    LockCurrentQueue,
    LockDailyCommodities,
    LockMonthlyCommodities,
    LockCurrentStoppage,
    LockDailyStoppages,
    LockDailyTrafficQueue,
    LockMonthlyTrafficQueue,
    LockWeeklyTrafficQueue,
    LockMonthlyTrafficStats,
    LockDailyTrafficStats,
    LockDailyTraffic,
    LockMonthlyStoppages,
    LockMonthlyTraffic,
    LockMovingAverage,
    LockRecentDelay,
    LockRecentStoppage,
    LockWeeklyDelay,
    LockMonthlyBudget,
    LockTrafficHistoricalQueue,
)
import pandas as pd
import requests


cwbi_url = "https://navdata-test.ops.usace.army.mil/data"


def metadata(division=None, district=None, river=None):
    """Get information about river locks.

    With no arguments, this retrieves a list of all locks. You can filter
    by any or all of the named arguments.

    Args:
        division (str): The standard abbreviation for a division, e.g. "SAD"
            for the Atlantic Division.
        district (str): The EROC code for a district, e.g. "B1" for the
            Mephis District.
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.

    Returns:
        A list of dicts, one for each lock matching the given arguments.
        An example dict::

            {
                "division": "SAD",
                "district": "K5",
                "rivername": "ALABAMA-COOSA RIVERS",
                "rivercode": "AL",
                "lockname": "CLAIBORNE LOCK AND DAM",
                "lockno": "11",
                "rivermile": 117.5,
                "numberofchmbrs": 1,
                "length": 600,
                "width": 84,
                "latitude": 31.614100999999998,
                "longitude": -87.55005899999999,
            }
    """
    # API Issues:
    #
    # - Their examples show using ``lock`` and ``chamber`` arguments, but the
    #   API seems to ignore those, as well as ``lockno``.
    #
    # - Their examples show a ``eroc`` parameter, but the ``district``
    #   parameter is specified using the EROC code, which makes the ``eroc``
    #   parameter redundant, and in any case, providing an ``eroc`` argument
    #   seems to always return an empty list.

    args = locals().copy()
    url = cwbi_url + "/metadata/locks/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    for item in r.json()["data"]:
        try:
            lock = Lock(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(lock)
        except Exception:
            continue
            
       
    return data


def metadata_df(division=None, district=None, river=None):
    """Return metadata for locks as a Pandas dataframe."""
    list_result = metadata(division, district, river)
    return pd.DataFrame(list_result)


def monthly_budget(river=None, lock=None):
    """Get budget information about river locks.

    With no arguments, get budget information for all locks. You can filter
    by any or all of the named arguments.


    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each lock. An example::

            {
                "name": "AL-12",
                "data": [
                    {
                        "period": "01/01/2015 00:00",
                        "expended": 3684954.98,
                        "unobligated": 4002719.78,
                        "obligated": 3126894.62,
                    }
                ],
            }
    """
    # So, here's the strange thing:
    #
    # 1. When you call this API with a ``river`` argument and only a river
    #    argument, e.g. ``[url]/[resource]?river=AL``, you'll get one item per
    #    lock on that river, named "AL-11", "AL-12", and "AL-13".
    #
    # 2. When you call this API with a ``river`` and a ``lock`` argument, e.g.
    #    ``[url]/[resource]?river=AL&lock=11``, you'll the one item that
    #    matches, but its name will be "AL-11-1". I have no idea what the third
    #    number is.
    #
    # 3. When you call with no arguments, you get all locks, with names as
    #    described in 2.
    #
    # 4. Sometimes, the names will be missing the third parameter, e.g. a name
    #    will be "XX-NN-".
    #
    # 5. If you call this with a division argument, you get only one item, with
    #    the total budget of all locks in the division.
    #
    # 6. If you call with a division and a river, you get only one item, with
    #    the total budget of all locks in that division, on that river.
    #
    # 7. The ``district`` and ``eroc`` parameters seem non-functional.
    #
    # With this in mind, I made two choices:
    #
    # 1. Since supplying a division argument changes the behavior of the
    #    API, I've wrapped that as a seperate function.
    #
    # 2. I decided to split the name field, and always expose it as river and
    #    lock, so that users of the wrapper get consistent results.

    args = locals().copy()
    url = cwbi_url + "/locks/budget/time/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    budgets = []
    for item in r.json()["data"]:
        for budget in item["data"]:
            budget["name"] = item["name"]
            budgets.append(budget)

    for item in budgets:
        try:
            log = LockMonthlyBudget(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(log)
        except Exception:
            continue
            
       
    return data


def monthly_division_budget(division, river=None):
    """Get monthly budgets for divisions.

    Args:
        division (str): The standard abbreviation for a division, e.g. "SAD"
            for the Atlantic Division.
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers. Specifying this argument shows
            the division budget only for this river.

    Returns:
        A dictionary, for example::

            {
                "period": "01/01/2015 00:00",
                "expended": 84792509.4,
                "unobligated": 50577917.9,
                "obligated": 61060892.7
            }
    """
    # See ``monthly_budget`` for a discussion of this API.
    args = locals().copy()
    url = cwbi_url + "/locks/budget/time/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    return r.json()["data"][0]["data"][0]


def info(river, lock):
    """Get info about a lock.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A dict, e.g.::

        {
            "lock": {
                "lock_name": "CLAIBORNE LOCK AND DAM",
                "number_of_chmbrs": 1,
                "beg_shift1": "0801",
                "beg_shift2": "1601",
                "beg_shift3": "0001",
                "river_mile": 117.5
            },
            "data": [
                {
                    "chmbr_no": "1",
                    "chmbr_name": "CLAIBORNE LOCK AND DAM",
                    "chmbr_length": "0600",
                    "chmbr_width": "0084"
                }
            ]
        }

        Note that, for each chamber in the lock, there will be one dict in
        the ``data`` field.
    """
    # The API seems to expect that you specify both arguments; specifying one
    # or neither will return a single object with all matching chambers in
    # the ``data`` field, but only one lock's info in the ``lock`` field.
    args = locals().copy()
    url = cwbi_url + "/locks/info"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    lock_info = r.json().copy()
    
    data = []
    chambers = []
    for chamber in lock_info["data"]:
        chamber["lock"] = lock_info["lock"]
        chamber["rivercode"] = args["river"]
        chamber["lockno"] = args["lock"]
        chambers.append(chamber)

    for chamber in chambers:
        try:
            lock_chamber = LockInfoChamber(**chamber)
        except Exception as exc:
            failed_validation.append(chamber)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(lock_chamber)
        except Exception:
            continue
       
    return data


def summary(river=None, lock=None, eroc=None, district=None, division=None):
    """Get a summary of lock data.

    With no arguments, get budget information for all locks. You can filter
    by any or all of the named arguments.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.

    Returns:
        A list of dicts, with one dict for each matching lock, e.g.::

            {
                "name": "AL-11",
                "rivername": "ALABAMA-COOSA RIVERS",
                "rivercode": "AL",
                "lockname": "CLAIBORNE LOCK AND DAM",
                "lockno": "11",
                "lat": 31.614454,
                "lon": -87.550027,
                "length": 0,
                "width": 0,
                "numberofchmbrs": 1,
                "status": {
                    "open": 1
                },
                "current": {
                    "waiting": -1,
                    "traveled": -1,
                    "total": -1,
                    "avg_delay": -1,
                    "avg_current_wait": -1
                },
                "upcoming": "No Upcoming Events",
                "trafficDataInd": 1,
                "eroc": "K5",
                "district": "SAM",
                "division": "SAD",
                "rivermile": 117.5,
                "chamberstatus": [
                    {
                        "type": "MAIN",
                        "status": "OPEN"
                    }
                ],
                "lock_status": {
                    "OPEN": [
                        1,
                        0,
                        0,
                        0
                    ]
                },
                "simple_status": "OPEN"
            }

            Note that you probably want to use this together with the
            ``info`` function.
    """
    # API Notes
    #
    # - Unlike many of the other API calls, the ``eroc`` and ``district``
    #   parameters both work. As far as I can tell, they are redundant, e.g.
    #   EROC of "K5" and district of "SAM" are both specifying the same
    #   district.
    #
    # - The ``dd`` and ``keyflag`` parameters of the API are mysterious. I
    #   don't know exactly what they do, or what arguments are valid, so I
    #   left them off the wrapper for now.
    #
    # - Many fields are clearly invalid, or mysterious in purpose.
    #
    # - The ``geojson`` argument changes the format of the returned values,
    #   so I'm splitting it into a seperate function.
    args = locals().copy()

    url = cwbi_url + "/locks/current/summary"
    r = requests.get(url, params=args)
    r.raise_for_status()

    failed_validation = []
    failed_exceptions = []

    data = []
    for item in r.json()["data"]:
        try:
            summary = LockSummary(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(summary)
        except Exception:
            continue
            
       
    return data


def summary_geojson(river=None, lock=None, eroc=None, district=None, division=None):
    """Get a summary of lock info in geojson format.

    With no arguments, get budget information for all locks. You can filter
    by any or all of the named arguments.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.

    Returns:
        A single geojson-style object with list of ``features``, one for
        each lock matching the arguments.
    """
    # See the ``summary`` function for more details.
    args = locals().copy()
    args["format"] = "geojson"

    url = cwbi_url + "/locks/current/summary"
    r = requests.get(url, params=args)
    r.raise_for_status()
    return r.json()


def current_operations(division=None, district=None, eroc=None, river=None, lock=None):
    """Get current operations for one or more locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments. You can specify a max of one of ``division`` or
    ``district``.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        geojson (bool): If true, return dict is in a different format
            compatible with geojson.

    Returns:
        A list of dicts, one for each lock that matches the given arguments
        and has current operations. Each dict is e.g.::

            {
                "name": "GI-01",
                "division": "MVD",
                "district": "MVN",
                "rivercode": "GI",
                "lockno": "01",
                "lat": 30.431002999999997,
                "lon": -91.20857,
                "news": "The ELISSA (TOW) has entered PORT ALLEN LOCK on the \
                         GULF INTRACOASTAL WATERWAY",
                "status": {}
            }
    """
    # API Notes
    #
    # - This is a fun one. The ``region`` parameter can take a district
    #   abbreviation (e.g. "MVN") OR a division abbreviation (e.g. "MVD").
    #   You can ALSO specifiy a district using the EROC code (e.g. "B2").
    #
    # - I still don't know what the ``keyflag`` parameter does.
    #
    # - The ``format`` parameter changes the returned data, so I split it
    #   into a seperate function.
    args = locals().copy()

    if args["district"] and args["division"]:
        raise RuntimeError("You can only use one of district and division")
    if args["district"]:
        args["region"] = args["district"]
        del args["district"]
    elif args["division"]:
        args["region"] = args["division"]
        del args["division"]

    url = cwbi_url + "/locks/current/operations"
    r = requests.get(url, params=args)
    r.raise_for_status()

    failed_validation = []
    failed_exceptions = []

    data = []
    for item in r.json()["data"]:
        try:
            operation = LockCurrentOperations(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(operation)
        except Exception:
            continue
            
       
    return data


def current_operations_geojson(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get current operations for one or more locks as geojson.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments. You can specify a max of one of ``division`` or
    ``district``.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A single geojson-style object with list of ``features``, one for
        each matching lock with current operations.
    """
    # See ``current_operations`` for discussion.
    args = locals().copy()

    if args["district"] and args["division"]:
        raise RuntimeError("You can only use one of district and division")
    if args["district"]:
        args["region"] = args["district"]
        del args["district"]
    elif args["division"]:
        args["region"] = args["division"]
        del args["division"]

    args["format"] = "geojson"

    url = cwbi_url + "/locks/current/operations"
    r = requests.get(url, params=args)
    r.raise_for_status()
    return r.json()


def all_stoppages():
    """Get all stoppages.

    API Broken! Currently returns::

        Error 500: Internal Server Error
        {
            "status": 500,
            "message": "Error querying DB",
            "detailed_message": "ORA-00942: table or view does not exist"
        }
    """
    raise NotImplementedError


def current_queue_summary(river=None, lock=None):
    """Get current information about vessels queued at locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each queued vessel in locks matching the given
        arguments.
    """
    # This is one of the most reasonable-seeming functions in the whole API.
    # The return value has no bogus fields, is self-explanatory, and the
    # parameters all work as expected.
    args = locals().copy()

    url = cwbi_url + "/locks/current/queue-summary"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    for item in r.json()["data"]:
        try:
            queue_summary = LockCurrentQueueSummary(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(queue_summary)
        except Exception:
            continue
            
       
    return data


def current_queue_summary_df(river=None, lock=None):
    """Get current queue information as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = current_queue_summary(river, lock)
    return pd.DataFrame(list_result)


def current_queue(river=None, lock=None, completed=None):
    """Get current and recent information about vessels queued at locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    When ``completed`` is false, this API function seems to be identical to
    current_queue_summary.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        completed (bool): If true, get all queue information from the past
            24 hours.

    Returns:
        A list of dicts, one for each queued vessel in locks matching the given
        arguments. Vessels not currently queued (only returned if ``completed``
        is true will have some ``null`` fields.
    """
    # I'm not sure what values count as true in the API, but certainly both
    # "true" and "false" work.
    args = locals().copy()
    if args["completed"]:
        args["completed"] = "true"

    url = cwbi_url + "/locks/current/queue"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    for item in r.json()["data"]:
        try:
            queue = LockCurrentQueue(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(queue)
        except Exception:
            continue
            
       
    return data


def current_queue_df(river=None, lock=None, completed=None):
    """Get current and recent information as a Pandas dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    When ``completed`` is false, this API function seems to be identical to
    current_queue_summary.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        completed (bool): If true, get all queue information from the past
            24 hours.

    Returns:
        A pandas dataframe.
    """
    list_result = current_queue(river, lock, completed)
    return pd.DataFrame(list_result)


def daily_commodities(division=None, district=None, eroc=None, river=None, lock=None):
    """Return commodity reports for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a list of dicts e.g.::

            {
                "timedate": "06/11/2012 00:00",
                "commCode": "7",
                "tons": 1877
            }

        The PDF linked in the README has a table of commodity codes; but codes
        in the responses aren't all in that document (which is from 1985). A
        quick google search doesn't turn up additional hints.
    """
    # As always, the ``chamber`` argument seems to have no effect.
    args = locals().copy()

    url = cwbi_url + "/locks/commodity/daily/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    commodities = []

    for item in r.json()["data"]:
        for commodity in item["data"]:
            commodity["name"] = item["name"]
            commodities.append(commodity)

    for commodity in commodities:
        try:
            daily_commodity = LockDailyCommodities(**commodity)
        except Exception as exc:
            failed_validation.append(commodity)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(daily_commodity)
        except Exception:
            continue
            
       
    return data


def daily_commodities_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Return commodity reports as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe, e.g.::

                       timedate commCode     tons     name
            0  01/01/2012 00:00        0      0.0  AG-42-1
            1  01/01/2012 00:00        1  12000.0  AG-42-1
            2  01/02/2012 00:00        0      0.0  AG-42-1
            3  01/02/2012 00:00        1  12000.0  AG-42-1
            4  01/03/2012 00:00        0      0.0  AG-42-1
    """
    list_result = daily_commodities(division, district, eroc, river, lock)
    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of commodities. Each item in that list gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    
    return pd.DataFrame(list_result)


def monthly_commodities(division=None, district=None, eroc=None, river=None, lock=None):
    """Return commodity reports for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a list of dicts e.g.::

            {
                "month": "01/01/2012 00:00",
                "commCode": "0",
                "direction": "D",
                "total": 31,
                "tons": 0
            }

        The PDF linked in the README has a table of commodity codes; but codes
        in the responses aren't all in that document (which is from 1985). A
        quick google search doesn't turn up additional hints.
    """
    # As always, the ``chamber`` argument seems to have no effect.
    args = locals().copy()

    url = cwbi_url + "/locks/commodity/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    commodities = []

    for item in r.json()["data"]:
        for commodity in item["data"]:
            commodity["name"] = item["name"]
            commodities.append(commodity)

    for commodity in commodities:
        try:
            monthly_commodity = LockMonthlyCommodities(**commodity)
        except Exception as exc:
            failed_validation.append(commodity)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(monthly_commodity)
        except Exception:
            continue
            
       
    return data


def monthly_commodities_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Return commodity reports as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe, e.g.::

                       month    commCode    direction     tons      total     name
            0  01/01/2012 00:00        0    U           0.0     694900      AG-42-1
            1  01/01/2012 00:00        1    U       12000.0       3000      AG-42-1
            2  01/02/2012 00:00        0    D           0.0      18800      AG-42-1
            3  01/02/2012 00:00        1    U       12000.0      10700      AG-42-1
            4  01/03/2012 00:00        0    D           0.0      38100      AG-42-1
    """
    list_result = monthly_commodities(division, district, eroc, river, lock)
    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of commodities. Each item in that list gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    
    return pd.DataFrame(list_result)


def current_stoppages(division=None, district=None, eroc=None, river=None, lock=None, recent=None):
    """Get current lock stoppage info.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        recent (str): Only shows stoppage in last period of time, if entry
            is d(ay) for stoppages beginning in the last day,
            w(eek) for 7 days, m(onth) for 30 days, y(ear) for 365 days,
            enter a number for an explicit number of days eg. recent=w, recent=23..

    Returns:
        A list of dicts, one for each stoppage e.g.::

            {
                "eroc": "B5",
                "river_code": "MI",
                "lock_no": "22",
                "chmbr_no": "1",
                "scheduled": "Y",
                "reason_code": "EE",
                "reason_description": "Repair lock or lock hardware",
                "beg_stop_date": "02/16/2021 08:00",
                "end_stop_date": "02/26/2021 16:00",
                "comments": "Scheduled closure for repairing upper miter gates.",
                "is_traffic_stopped": "Y",
                "lat": 39.635545,
                "lon": -91.248831,
                "last_refreshed": "02/18/2021 21:00"
            },
    """
    args = locals().copy()
    url = cwbi_url + "/locks/stoppage/current/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []

    for item in r.json()["data"]:
        try:
            stoppage = LockCurrentStoppage(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(stoppage)
        except Exception:
            continue
            
       
    return data


def current_stoppages_df(
    division=None, district=None, eroc=None, river=None, lock=None, recent=None
):
    """Get monthly lock stoppage info as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        recent (str): Only shows stoppage in last period of time, if entry
            is d(ay) for stoppages beginning in the last day,
            w(eek) for 7 days, m(onth) for 30 days, y(ear) for 365 days,
            enter a number for an explicit number of days eg. recent=w, recent=23..

    Returns:
        A pandas dataframe.
    """
    list_result = current_stoppages(division, district, eroc, river, lock, recent)
    return pd.DataFrame(list_result)


def daily_stoppages(division=None, district=None, eroc=None, river=None, lock=None):
    """Return stoppage information for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a (possibly empty) list of events, e.g::

            {
                "eventDate": "02/19/2008 00:00",
                "status": [
                    "UNPLANNED"
                ]
            }
    """
    # As always, the ``chamber`` argument seems to have no effect.
    args = locals().copy()

    url = cwbi_url + "/locks/stoppage/daily/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    stoppages = []

    for item in r.json()["data"]:
        for stoppage in item["data"]:
            stoppage["name"] = item["name"]
            stoppages.append(stoppage)

    for stoppage in stoppages:
        try:
            daily_stoppage = LockDailyStoppages(**stoppage)
        except Exception as exc:
            failed_validation.append(stoppage)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(daily_stoppage)
        except Exception:
            continue
            
       
    return data


def daily_traffic_queue(division=None, district=None, eroc=None, river=None, lock=None):
    """Return reports about queuing time for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a list of dicts e.g.::

            {
                "arrivalDate": "01/01/2012 05:20",
                "queueToStart": 88,
                "startToSill": 21,
                "sillToEntry": 34,
                "entryToExit": 31,
                "exitToEnd": 43,
                "startToEnd": 0,
                "total": 217
            }
    """
    # As always, the ``chamber`` argument seems to have no effect.
    args = locals().copy()

    url = cwbi_url + "/locks/traffic/time/daily/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    queues = []

    for item in r.json()["data"]:
        for queue in item["data"]:
            queue["name"] = item["name"]
            queues.append(queue)

    for queue in queues:
        try:
            traffic_queue = LockDailyTrafficQueue(**queue)
        except Exception as exc:
            failed_validation.append(queue)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_queue)
        except Exception:
            continue
            
       
    return data


def daily_traffic_queue_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Return daily traffic queue information as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = daily_traffic_queue(division, district, eroc, river, lock)

    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of commodities. Each item in that list gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    return pd.DataFrame(list_result)


def monthly_traffic_queue(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Return reports about queuing time for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a list of dicts, one for each month, e.g.::

            {
                "arrivalDate": "01/01/2019 00:00",
                "sum": {
                    "queueToStart": 926,
                    "startToSill": 6,
                    "sillToEntry": 24,
                    "entryToExit": 23,
                    "exitToEnd": 46,
                    "startToEnd": 0,
                    "total": 1025
                },
                "avg": {
                    "queueToStart": 463,
                    "startToSill": 3,
                    "sillToEntry": 12,
                    "entryToExit": 12,
                    "exitToEnd": 23,
                    "startToEnd": 0
                },
                "rollAvg": {
                    "queueToEndAvg": 106
                }
            }
    """
    # As always, the ``chamber`` argument seems to have no effect.
    args = locals().copy()

    url = cwbi_url + "/locks/traffic/time/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    queues = []

    for item in r.json()["data"]:
        for queue in item["data"]:
            queue["name"] = item["name"]
            queue["types"] = item["types"]
            queues.append(queue)

    for queue in queues:
        try:
            traffic_queue = LockMonthlyTrafficQueue(**queue)
        except Exception as exc:
            failed_validation.append(queue)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_queue)
        except Exception:
            continue
            
       
    return data


def monthly_traffic_queue_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Return monthly traffic queue data as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that this API function can return far more information that most;
    there's no documented way of restricting the time interval of the results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = monthly_traffic_queue(division, district, eroc, river, lock)

    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of commodities. Each item in that list gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    #
    # Repeated columns are qualified, e.g. there are "sum.startToEnd" and
    # "avg.startToEnd" columns.
    return pd.DataFrame(list_result)


def weekly_traffic_queue(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get weekly queueing information.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    It appears that this API function is limited to returning 10000 results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each lock has a ``data``
        field with a list of dicts e.g.::
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/time/weekly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    queues = []

    for item in r.json()["data"]:
        for queue in item["data"]:
            queue["name"] = item["name"]
            queue["types"] = item["types"]
            queues.append(queue)

    for queue in queues:
        try:
            traffic_queue = LockWeeklyTrafficQueue(**queue)
        except Exception as exc:
            failed_validation.append(queue)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_queue)
        except Exception:
            continue
            
       
    return data


def weekly_traffic_queue_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get weekly queueing information as a pandas dataframe

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    It appears that this API function is limited to returning 10000 results.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A dataframe with one row per weekly entry per lock.
    """
    list_result = weekly_traffic_queue(division, district, eroc, river, lock)

    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of commodities. Each item in that list gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    #
    # Repeated columns are qualified, e.g. there are "sum.startToEnd" and
    # "avg.startToEnd" columns.
    return pd.DataFrame(list_result)


def monthly_traffic_stats(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get monthly traffic statistics for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each dict has a "data"
        key with a list of dicts, one per month, e.g.::

            {
                "timedate": "05/01/2012 00:00",
                "timeInLock": 1483,
                "timeInQueue": 343,
                "minTimeInLock": 1200,
                "maxTimeInLock": 2100,
                "tripCount": 7
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/stats/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    stats = []

    for item in r.json()["data"]:
        for stat in item["data"]:
            stat["name"] = item["name"]
            stats.append(stat)

    for stat in stats:
        try:
            traffic_stat = LockMonthlyTrafficStats(**stat)
        except Exception as exc:
            failed_validation.append(stat)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_stat)
        except Exception:
            continue
            
       
    return data


def monthly_traffic_stats_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get monthly traffic statistics as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A Pandas dataframe
    """
    list_result = monthly_traffic_stats(division, district, eroc, river, lock)

    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of monthly statistics. Each month gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    return pd.DataFrame(list_result)


def daily_traffic_stats(division=None, district=None, eroc=None, river=None, lock=None):
    """Get daily traffic statistics for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each dict has a "data"
        key with a list of dicts, one per day, e.g.::

            {
                "timedate": "05/01/2012 00:00",
                "timeInLock": 1483,
                "timeInQueue": 343,
                "minTimeInLock": 1200,
                "maxTimeInLock": 2100,
                "tripCount": 7
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/stats/daily/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    stats = []

    for item in r.json()["data"]:
        for stat in item["data"]:
            stat["name"] = item["name"]
            stats.append(stat)

    for stat in stats:
        try:
            traffic_stat = LockDailyTrafficStats(**stat)
        except Exception as exc:
            failed_validation.append(stat)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_stat)
        except Exception:
            continue
            
       
    return data


def daily_traffic_stats_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get daily traffic statistics as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A Pandas dataframe
    """
    list_result = daily_traffic_stats(division, district, eroc, river, lock)

    # Each item in the list is a lock. Each lock has a "data" item with a list
    # of monthly statistics. Each month gets its own row in the dataframe.
    # Repeat the name of the lock in each row.
    return pd.DataFrame(list_result)


def daily_traffic(district=None, eroc=None, river=None, lock=None):
    """Get daily traffic for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each dict has a "data"
        key with a list of dicts, one per day, e.g.::

            {
                "startdate": "05/11/2012 11:10",
                "enddate": "05/11/2012 11:30",
                "timeInLock": "00:20:00"
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/daily/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    traffic = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            traffic.append(log)

    for log in traffic:
        try:
            traffic_log = LockDailyTraffic(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_log)
        except Exception:
            continue
            
       
    return data


def daily_traffic_df(district=None, eroc=None, river=None, lock=None):
    """Get daily traffic for the specified locks as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each dict has a "data"
        key with a list of dicts, one per day, e.g.::

            {
                "startdate": "05/11/2012 11:10",
                "enddate": "05/11/2012 11:30",
                "timeInLock": "00:20:00"
            }
    """
    list_result = daily_traffic(district, eroc, river, lock)
    return pd.DataFrame(list_result)


def monthly_stoppages(division=None, district=None, eroc=None, river=None, lock=None):
    """Get monthly lock stoppage info.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock, each having a "data" field
        with a list of entries, one per month, e.g.::

            {
                "month": "02/01/2008 00:00",
                "days_closed": 0,
                "days_stopped_unplanned": 1,
                "days_stopped_planned": 0
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/stoppage/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    stoppages = []

    for item in r.json()["data"]:
        for stoppage in item["data"]:
            stoppage["name"] = item["name"]
            stoppages.append(stoppage)

    for item in stoppages:
        try:
            stoppage = LockMonthlyStoppages(**item)
        except Exception as exc:
            failed_validation.append(item)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(stoppage)
        except Exception:
            continue
            
       
    return data


def monthly_stoppages_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get monthly lock stoppage info as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = monthly_stoppages(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)


def monthly_traffic(division=None, district=None, eroc=None, river=None, lock=None):
    """Get monthly lock traffic info.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock, each having a "data" field
        with a list of entries, one per month, e.g.::

            {
                "month": "2012-03-01T00:00:00.000Z",
                "ur_passenger": 11,
                "ur_traffic": 15,
                "dr_passenger": 14,
                "dr_traffic": 18
            }
    # As always, the ``chamber`` argument seems to have no effect.
    Null values will default to 0 for passenger and traffic fields
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/monthly/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    traffic = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            traffic.append(log)

    for log in traffic:
        try:
            traffic_log = LockMonthlyTraffic(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(traffic_log)
        except Exception:
            continue
            
       
    return data


def monthly_traffic_df(division=None, district=None, eroc=None, river=None, lock=None):
    """Get monthly lock traffic info as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = monthly_traffic(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)


def moving_average(division=None, district=None, eroc=None, river=None, lock=None):
    """Get moving averages of various lock statistics.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, on per matching lock, each with a "data" field with a
        a list of dicts, e.g.::

            {
                "dateTime": "2000-01-15T00:00:00.000Z",
                "type": "day",
                "queueToStart": 0,
                "startToSill": 300,
                "sillToEntry": 600,
                "entryToExit": 900,
                "exitToEnd": 600,
                "startToEnd": 0,
                "queueToEnd": 2400
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/time/movingaverage"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    averages = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            log["types"] = item["types"]
            averages.append(log)

    for log in averages:
        try:
            averages_log = LockMovingAverage(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(averages_log)
        except Exception:
            continue
            
       
    return data


def moving_average_df(division=None, district=None, eroc=None, river=None, lock=None):
    """Get moving averages of various lock statistics as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = moving_average(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)


def nearby_navigation_notices():
    """Get live navigation notices within 10 miles of the lock.

    API Broken! Currently returns::

        Error 500: Internal Server Error
        {
            "status": 500,
            "message": "Error querying DB",
            "detailed_message": "ORA-13226: interface not supported without a
            spatial index\nORA-06512: at \"MDSYS.MD\", line 1723\nORA-06512: at
            \"MDSYS.MDERR\", line 8\nORA-06512: at \"MDSYS.SDO_3GL\", line
            1096"
        }
    """
    raise NotImplementedError


def recent_delays(river=None, lock=None, minDelayMin=None):
    """Get recent delays at specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that the API does not specify what "recent" means.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        minDelayMin (str): A numeric string with the minimum delay in minutes
            for a vessel to be considered delayed. Defaults to 60.

    Returns:
        A list of dicts, one per delayed vessel, e.g.::

            {
                "name": "TN-02",
                "vesselname": "HARLEY HALL",
                "arrivaldate": "08/18/2020 17:10",
                "delaytime": 2670
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/delays/recent"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []

    for vessel in r.json()["data"]:
        try:
            vessel_delay = LockRecentDelay(**vessel)
        except Exception as exc:
            failed_validation.append(vessel)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(vessel_delay)
        except Exception:
            continue
            
       
    return data


def recent_delays_df(river=None, lock=None, minDelayMin=None):
    """Get recent delays at specified locks as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that the API does not specify what "recent" means.

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.
        minDelayMin (str): A numeric string with the minimum delay in minutes
            for a vessel to be considered delayed. Defaults to 60.

    Returns:
        A pandas dataframe.
    """
    list_result = recent_delays(river, lock, minDelayMin)
    return pd.DataFrame(list_result)


def recent_stoppages(division=None, district=None, eroc=None, river=None, lock=None):
    """Get recent stoppage and shutdown events for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that the API documentation does not define "recent."

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one per matching lock. Each dict has a "data" field with
        a list of dicts, one per stoppage, e.g.::

            {
                "startDate": "07/17/2013 09:00",
                "endDate": "07/17/2013 14:30",
                "reasonCode": "T",
                "stoppageReason": "Maintaining lock or lock equipment"
            }
    """
    # This API includes the ``chamber`` parameter that seems inoperative, and
    # the ``dd`` and ``keyflag`` pararmeters with unknown effects.
    args = locals().copy()
    url = cwbi_url + "/locks/stoppage/recent"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    stoppages = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            stoppages.append(log)

    for log in stoppages:
        try:
            stoppages_log = LockRecentStoppage(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(stoppages_log)
        except Exception:
            continue
            
       
    return data


def recent_stoppages_df(division=None, district=None, eroc=None, river=None, lock=None):
    """Get recent stoppage and shutdown events as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Note that the API documentation does not define "recent."

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = recent_stoppages(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)


def traffic_historical_queue(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get historical queueing data for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one per matching lock. Each dict has a "data" field with
        a list of dicts, e.g.::

            {
                "type": "day",
                "time_data": "1",
                "avg": 35.35
            }
    """
    args = locals().copy()
    url = cwbi_url + "/locks/traffic/time/aggregate"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []
    data = []
    queue = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            log["types"] = item["types"]
            queue.append(log)

    for log in queue:
        try:
            queue_log = LockTrafficHistoricalQueue(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(queue_log)
        except Exception:
            continue
            
       
    return data


def traffic_historical_queue_df(
    division=None, district=None, eroc=None, river=None, lock=None
):
    """Get historical queueing data for the specified locks as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = traffic_historical_queue(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)


def weekly_delay(division=None, district=None, eroc=None, river=None, lock=None):
    """Get weekly delay information for the specified locks.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A list of dicts, one for each matching lock. Each dict has a field
        "data" with a list of dict, one per day with delays, e.g.::

            {
                "days_ago": 4,
                "delay_code": 0,
                "delay_count": 1
            }
    """
    # It's unclear what the ``dd`` and ``keyflag`` parameters of the API do.
    args = locals().copy()
    url = cwbi_url + "/locks/current/delay/week/"
    r = requests.get(url, params=args)
    r.raise_for_status()
    failed_validation = []
    failed_exceptions = []

    data = []
    delays = []

    for item in r.json()["data"]:
        for log in item["data"]:
            log["name"] = item["name"]
            delays.append(log)

    for log in delays:
        try:
            delays_log = LockWeeklyDelay(**log)
        except Exception as exc:
            failed_validation.append(log)
            failed_exceptions.append(exc)
            continue

        try:
            data.append(delays_log)
        except Exception:
            continue
            
       
    return data


def weekly_delay_df(division=None, district=None, eroc=None, river=None, lock=None):
    """Get weekly delay information as a dataframe.

    With no arguments, get operations for all locks. You can filter by any or
    all of the named arguments.

    Args:
        division (str): A division abbreviation, e.g. "SAD" for the South
            Atlantic Division.
        district (str): A district abbreviation, e.g. "SAM" for the Mobile
            District.
        eroc (str): An EROC code for a district, e.g. "K5" for the Mobile
            District.
        river (str): The standard abbreviation for a river, e.g. "AL" for the
            Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock.

    Returns:
        A pandas dataframe.
    """
    list_result = weekly_delay(division, district, eroc, river, lock)
    return pd.DataFrame(list_result)
