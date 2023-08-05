from pydantic.dataclasses import dataclass
from dataclasses import asdict
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta

@dataclass
class BaseDataClass:

    @classmethod
    def _parse_time(cls, value: str) -> int:
        """
        Take a timedelta from a string
        and return an int in seconds

        Parameters
        ----------
        value : str
            timedelta with hour first

        Returns
        -------
        int
            int total seconds

        Raises
        ------
        ValueError
            If parsing fails, report the failed params
        """
        try:
            parsed_time = datetime.strptime(value, "%H:%M:%S")
            total_seconds = timedelta(hours=parsed_time.hour, minutes=parsed_time.minute, seconds=parsed_time.second).total_seconds()

        except Exception:
            params = {"value": value}
            raise ValueError(
                f"Could not parse string value with params: {params}"
            )

        return total_seconds

    def to_dict(self):
        """
        A convenient accessor for external calls to `asdict` on
        this dataclass.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Lock(BaseDataClass):
    rivercode: str
    latitude: float
    longitude: float
    division: str = None
    district: str = None
    rivername: str = None
    lockname: str = None
    lockno: str = None
    rivermile: float = None
    numberofchmbrs: int = None
    length: float = None
    width: float = None
    location: Dict = None

    def __post_init__(self):
        self.location = { 'coordinates': [self.longitude, self.latitude], 'type': 'Point' }

    class Config:
        collection = 'cwbi.lock_metadata'

@dataclass
class LockSummary(BaseDataClass):
    rivercode: str
    lockno: str
    lat: float
    lon: float
    name: str = None
    division: str = None
    district: str = None
    rivername: str = None
    lockname: str = None
    rivermile: float = None
    numberofchmbrs: int = None
    length: float = None
    width: float = None
    status: Dict = None
    current: Dict = None
    upcoming: str = None
    trafficDataInd: int = None
    eroc: str = None
    chamberstatus: List[Dict] = None
    lock_status: Dict = None
    simple_status: str = None
    created_at: datetime = None
    location: Dict = None

    def __post_init__(self):
        self.location = { 'coordinates': [self.lon, self.lat], 'type': 'Point' }
        self.created_at = datetime.now()

    class Config:
        collection = 'cwbi.lock_summary'

@dataclass
class LockCurrentOperations(BaseDataClass):
    rivercode: str
    lockno: str
    lat: float
    lon: float
    name: str = None
    division: str = None
    district: str = None
    news: str = None
    status: Dict = None
    created_at: datetime = None
    location: Dict = None

    def __post_init__(self):
        self.location = { 'coordinates': [self.lon, self.lat], 'type': 'Point' }
        self.created_at = datetime.now()

    class Config:
        collection = 'cwbi.lock_current_operations'

@dataclass
class LockInfo(BaseDataClass):
    lock_name: str
    number_of_chmbrs: int
    beg_shift1: str
    beg_shift2: str
    beg_shift3: str
    river_mile: float

@dataclass
class LockInfoChamber(BaseDataClass):
    lock: LockInfo
    chmbr_no: str
    chmbr_name: str
    chmbr_length: str
    chmbr_width: str
    rivercode: str = None
    lockno: str = None

    class Config:
        collection = 'cwbi.lock_info'

@dataclass
class LockCurrentQueueSummary(BaseDataClass):
    rivercode: str
    lockno: str
    vesselno: str
    vesselname: str = None
    direction: str = None
    seq_no: str = None
    arrivaldate: datetime = None
    delaytime: int = None
    source: str = None
    created_at: datetime = None

    def __post_init__(self):
        self.arrivaldate = datetime.strptime(self.arrivaldate, '%m/%d/%Y %H:%M')
        self.created_at = datetime.now()

    class Config:
        collection = 'cwbi.lock_current_queue_summary'

@dataclass 
class LockCurrentQueue(BaseDataClass): 
    rivercode: str 
    lockno: str 
    vesselno: str 
    source: str
    vesselname: str = None
    direction: str = None
    seq_no: str = None 
    arrivaldate: datetime = None 
    delaytime: int = None 
    created_at: datetime = None 
 
    def __post_init__(self): 
        self.arrivaldate = datetime.strptime(self.arrivaldate, '%m/%d/%Y %H:%M') 
        self.created_at = datetime.now() 
 
    class Config: 
        collection = 'cwbi.lock_current_queue'

@dataclass
class LockDailyCommodities(BaseDataClass):
    timedate: datetime
    commCode: str
    tons: int
    name: str
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.timedate = datetime.strptime(self.timedate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_daily_commodities'

@dataclass
class LockMonthlyCommodities(BaseDataClass):
    name: str
    month: datetime
    commCode: str
    direction: str
    total: int
    tons: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.month = datetime.strptime(self.month, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_monthly_commodities'

@dataclass
class LockCurrentStoppage(BaseDataClass):
    eroc: str
    river_code: str
    lock_no: str
    chmbr_no: str
    scheduled: str
    reason_code: str
    reason_description: str
    beg_stop_date: datetime
    is_traffic_stopped: str
    lat: float
    lon: float
    last_refreshed: datetime
    end_stop_date: datetime = None
    comments: str = None
    location: Dict = None

    def __post_init__(self):
        self.beg_stop_date = datetime.strptime(self.beg_stop_date, '%m/%d/%Y %H:%M')
        self.last_refreshed = datetime.strptime(self.last_refreshed, '%m/%d/%Y %H:%M')
        self.end_stop_date = datetime.strptime(self.end_stop_date, '%m/%d/%Y %H:%M') if self.end_stop_date else None
        self.location = { 'coordinates': [self.lon, self.lat], 'type': 'Point' }

    class Config:
        collection = 'cwbi.lock_current_stoppages'

@dataclass
class LockDailyStoppages(BaseDataClass):
    name: str
    status: List
    eventDate: datetime
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.eventDate = datetime.strptime(self.eventDate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_daily_stoppages'

@dataclass
class LockDailyTrafficQueue(BaseDataClass):
    name: str
    arrivalDate: datetime
    queueToStart: int
    startToSill: int
    sillToEntry: int
    entryToExit: int
    exitToEnd: int
    startToEnd: int
    total: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.arrivalDate = datetime.strptime(self.arrivalDate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_daily_traffic_queue'

@dataclass
class LockTQSum(BaseDataClass):
    queueToStart: int
    startToSill: int
    sillToEntry: int
    entryToExit: int
    exitToEnd: int
    startToEnd: int
    total: int

@dataclass
class LockTQAvg(BaseDataClass):
    queueToStart: int
    startToSill: int
    sillToEntry: int
    entryToExit: int
    exitToEnd: int
    startToEnd: int

@dataclass
class LockTQRollAvg(BaseDataClass):
    queueToEndAvg: int

@dataclass
class LockMonthlyTrafficQueue(BaseDataClass):
    name: str
    types: List
    arrivalDate: datetime
    sum: LockTQSum
    avg: LockTQAvg
    rollAvg: LockTQRollAvg
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.arrivalDate = datetime.strptime(self.arrivalDate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_monthly_traffic_queue'
        
@dataclass
class LockWeeklyTrafficQueue(BaseDataClass):
    name: str
    types: List
    arrivalDate: datetime
    sum: LockTQSum
    avg: LockTQAvg
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.arrivalDate = datetime.strptime(self.arrivalDate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_weekly_traffic_queue'

@dataclass
class LockMonthlyTrafficStats(BaseDataClass):
    name: str
    timedate: datetime
    timeInLock: int
    timeInQueue: int
    minTimeInLock: int
    maxTimeInLock: int
    tripCount: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.timedate = datetime.strptime(self.timedate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_monthly_traffic_stats'

@dataclass
class LockDailyTrafficStats(BaseDataClass):
    name: str
    timedate: datetime
    timeInLock: int
    timeInQueue: int
    minTimeInLock: int
    maxTimeInLock: int
    tripCount: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.timedate = datetime.strptime(self.timedate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_daily_traffic_stats'

@dataclass
class LockDailyTraffic(BaseDataClass):
    name: str
    startdate: datetime
    enddate: datetime
    timeInLock: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.startdate = datetime.strptime(self.startdate, '%m/%d/%Y %H:%M')
        self.enddate = datetime.strptime(self.enddate, '%m/%d/%Y %H:%M')
        self.timeInLock = self._parse_time(self.timeInLock)
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_daily_traffic'

@dataclass
class LockMonthlyStoppages(BaseDataClass):
    name: str
    month: datetime
    days_closed: int
    days_stopped_unplanned: int
    days_stopped_planned: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.month = datetime.strptime(self.month, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_monthly_stoppages'

@dataclass
class LockMonthlyTraffic(BaseDataClass):
    name: str
    month: datetime
    ur_passenger: int = 0
    ur_traffic: int = 0
    dr_passenger: int = 0
    dr_traffic: int = 0
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.month = datetime.strptime(self.month, '%Y-%m-%dT%H:%M:%S.%fZ')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_monthly_traffic'

@dataclass
class LockMovingAverage(BaseDataClass):
    name: str
    types: List
    dateTime: datetime
    type: str
    queueToStart: int
    startToSill: int
    sillToEntry: int
    entryToExit: int
    exitToEnd: int
    startToEnd: int
    queueToEnd: int
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.dateTime = datetime.strptime(self.dateTime, '%Y-%m-%dT%H:%M:%S.%fZ')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_moving_averages'

@dataclass
class LockRecentDelay(BaseDataClass):
    name: str
    vesselname: str
    arrivaldate: datetime
    delaytime: int
    rivercode: str = None
    lockno: str = None
    created_at: datetime = None

    def __post_init__(self):
        self.arrivaldate = datetime.strptime(self.arrivaldate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno
        self.created_at = datetime.now()

    class Config:
        collection = 'cwbi.lock_recent_delays'

@dataclass
class LockRecentStoppage(BaseDataClass):
    name: str
    startDate: datetime
    endDate: datetime
    reasonCode: str
    stoppageReason: str
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.startDate = datetime.strptime(self.startDate, '%m/%d/%Y %H:%M')
        self.endDate = datetime.strptime(self.endDate, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_recent_stoppages'

@dataclass
class LockWeeklyDelay(BaseDataClass):
    name: str
    days_ago: int
    delay_code: int
    delay_count: int
    created_at: datetime = None
    rivercode: str = None
    lockno: str = None

    def __post_init__(self):
        self.created_at = datetime.now()
        river, lockno, *_ = self.name.split("-")
        self.rivercode = river
        self.lockno = lockno

    class Config:
        collection = 'cwbi.lock_weekly_delay'

@dataclass 
class LockMonthlyBudget(BaseDataClass): 
    name: str 
    period: datetime
    expended: float
    unobligated: float
    obligated: float
    rivercode: str = None 
    lockno: str = None 
 
    def __post_init__(self):
        self.period = datetime.strptime(self.period, '%m/%d/%Y %H:%M')
        river, lockno, *_ = self.name.split("-") 
        self.rivercode = river 
        self.lockno = lockno 
 
    class Config: 
        collection = 'cwbi.lock_monthly_budget'

@dataclass 
class LockTrafficHistoricalQueue(BaseDataClass): 
    name: str
    types: List
    type: str 
    time_data: str 
    avg: float 
    rivercode: str = None 
    lockno: str = None 
 
    def __post_init__(self): 
        river, lockno, *_ = self.name.split("-") 
        self.rivercode = river 
        self.lockno = lockno 
 
    class Config: 
        collection = 'cwbi.lock_traffic_historical_queue'