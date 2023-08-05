import requests
import xmltodict
from xml.parsers.expat import ExpatError


BASE_URL = "https://corpslocks.usace.army.mil/lpwb"


def _parse_xml_rows(raw_xml_text):
    try:
        parsed = xmltodict.parse(raw_xml_text)["ROWSET"]["ROW"]

        if not isinstance(parsed, list):
            data = [parsed]
        else:
            data = [row for row in parsed]

    except ExpatError:
        data = []

    return data


def lock_queue(river_code: str, lock_number: str):
    """Lock Queue Reports (past 24 hours)

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock, e.g. "01"

    Returns:
        List[OrderedDict]: A single object with a list of lock queue reports by vessel

    Sample:
        [{
            "VESSEL_NAME": "VANPORT (TOW)",
            "VESSEL_NO": "0512604",
            "DIRECTION": "U",
            "NUM_BARGES": "6",
            "SOL_DATE": "08/14/20 07:40",
            "ARRIVAL_DATE": "08/14/20 06:26",
            "END_OF_LOCKAGE": "08/14/20 08:44",
            "TIMEZONE": "CST",
            "MMSI": "367306560"
        },..]
    """

    url = f"{BASE_URL}/xml.lockqueue?in_river={river_code}&in_lock={lock_number}"
    r = requests.get(url, verify=False)
    r.raise_for_status()

    return _parse_xml_rows(r.text)


def lock_tonnage(river_code: str, lock_number: str, month: str, year: str):
    """Lock Tonnage Reports By Month

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock, e.g. "01"
        month (str): A numeric string for 2-digit month with leading zeros, e.g. "01" for January
        year (str): A numeric string for 4-digit year

    Returns:
        List[OrderedDict]: A single object with a list of lock Tonnage reports by vessel

    Sample:
        [{
            "COMM_CODE": "10",
            "COMM_DESC": "Coal, Lignite And Coke",
            "DOWNBOUND_TONS": "29.4",
            "TOTAL_TONS": "29.4"
        },..]
    """

    url = f"{BASE_URL}/xml.tonnage?in_river={river_code}&in_lock={lock_number}&in_mon_yr={month}{year}"
    r = requests.get(url, verify=False)
    r.raise_for_status()

    return _parse_xml_rows(r.text)


def lock_traffic(river_code: str, lock_number: str):
    """Lock Traffic Reports (past 30 days)

    Args:
        river (str): The standard abbreviation for a river, e.g. "AL"
            for the Alabama-Coosa Rivers.
        lock (str): A numeric string designating a specific lock, e.g. "01"

    Returns:
        List[OrderedDict]: A single object with a list of lock traffic reports

    Sample:
        [
            {
                "EROC": "B2",
                "RIVER_CODE": "GI",
                "RIVER_NAME": "GULF INTRACOASTAL WATERWAY",
                "LOCK_NO": "01",
                "LOCK_NAME": "PORT ALLEN LOCK",
                "DIRECTION": "U",
                "VESSEL_NO": "0512604",
                "VESSEL_NAME": "VANPORT (TOW)",
                "ARRIVAL_DATE": "08/14/20 06:26",
                "SOL_DATE": "08/14/20 07:40",
                "END_OF_LOCKAGE": "08/14/20 08:44",
                "TIMEZONE": "CST",
                "NUM_BARGES": "6",
                "NUMBER_PROCESSED": "6",
                "HAZARD_CODE": "Y"
            },
            {
                "EROC": "B2",
                "RIVER_CODE": "GI",
                "RIVER_NAME": "GULF INTRACOASTAL WATERWAY",
                "LOCK_NO": "01",
                "LOCK_NAME": "PORT ALLEN LOCK",
                "DIRECTION": "D",
                "VESSEL_NO": "1279277",
                "VESSEL_NAME": "FORT DEFIANCE ( TOW 2017 )",
                "ARRIVAL_DATE": "08/14/20 05:56",
                "SOL_DATE": "08/14/20 06:33",
                "END_OF_LOCKAGE": "08/14/20 07:18",
                "TIMEZONE": "CST",
                "NUM_BARGES": "1",
                "NUMBER_PROCESSED": "1",
                "HAZARD_CODE": "N"
            }
            ,..]
    """

    url = f"{BASE_URL}/xml.traffic?in_river={river_code}&in_lock={lock_number}"
    r = requests.get(url, verify=False)
    r.raise_for_status()

    return _parse_xml_rows(r.text)


def active_stoppages(begin_date: str = None, end_date: str = None):
    """Active or Future Stoppages Report

    Passing no arguments results in all active and future stoppages available over a 30 day period

    Args:
        begin_date (str): Date string formatted as MMDDYYYY
        end_date (str): Date string formatted as MMDDYYYY

    Returns:
        dict: A single object with a list of Active or Future Stoppages Report by vessel

    Sample:
        [
            {
                'erocCode': 'H1',
                'riverCode': 'OH',
                'lockNumber': '21',
                'chamberNumber': '4',
                'beginStopDate': '01/01/2020',
                'endStopDate': '01/31/2020',
                'isScheduled': 'No',
                'reasonCode': 'Operations (run-spill-divert water, flush seals-reserve etc)',
                'numHwCycles': None,
                'year': 2020,
                'refreshDate': '04/25/2020',
                'isTrafficStopped': 'Y'
            },
            {
                'erocCode': 'H3',
                'riverCode': 'TN',
                'lockNumber': '01',
                'chamberNumber': '1',
                'beginStopDate': '02/01/2020',
                'endStopDate': '02/01/2020',
                'isScheduled': 'No',
                'reasonCode': 'Tow staff occupied with other duties',
                'numHwCycles': None,
                'year': 2020,
                'refreshDate': '04/25/2020',
                'isTrafficStopped': 'Y'
            }
        ,..]
    """

    url = f"{BASE_URL}/json.stall_stoppage"

    if begin_date and end_date:
        url += f"?begin_date={begin_date}&end_date={end_date}"

    r = requests.get(url, verify=False)
    r.raise_for_status()

    return r.json()


def lock_delays():
    """Locks with Current Delay Time Report

    Args:
        None

    Returns:
        dict: A single object with a list of Locks with Current Delay Time Report by vessel

    Sample:
        [
            {
                'eroc': 'H4',
                'riverCode': 'AG',
                'lockNumber': '42',
                'fourHourAverageDelayInMinutes': '0'
            },
            {
                'eroc': 'H4',
                'riverCode': 'AG',
                'lockNumber': '43',
                'fourHourAverageDelayInMinutes': '9'
            }
        ,..]
    """

    url = f"{BASE_URL}/json.lock_delay"
    r = requests.get(url, verify=False)
    r.raise_for_status()

    return r.json()
