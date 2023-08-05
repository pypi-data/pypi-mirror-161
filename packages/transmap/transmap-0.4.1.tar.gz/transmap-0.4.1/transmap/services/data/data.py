import requests
import pandas as pd
class data:
    def fetch_by_title(title:str, bbox = [], start_date:str = "", end_date:str = "", offset:int = 0):
        api_url = "https://oak.cast.uark.edu/metadata-api/Data/GetDataByTitle"
        headers={
            'Content-type':'application/json-patch+json',
            'Accept':'text/plain'
        }
        if start_date == "" or end_date == "":
            request = {"title": title, "bbox": bbox, "offset": offset}
        else:
            request ={"title": title,"bbox": bbox,"startDate": start_date, "endDate": end_date, "offset": offset}

        response = requests.post(api_url, json=request, headers=headers)
        json_response = response.json()
        code = response.status_code
        df = pd.json_normalize(json_response['data']['features'])
        return df

    def fetch_by_id(id:str, bbox = [], start_date:str = "", end_date:str = "", offset:int = 0):
        api_url = "https://oak.cast.uark.edu/metadata-api/Data/GetDataById"
        headers={
            'Content-type':'application/json-patch+json',
            'Accept':'text/plain'
        }
        if start_date == "" or end_date == "":
            request = {"id": id, "bbox": bbox, "offset": offset}
        else:
            request ={"id": id,"bbox": bbox,"startDate": start_date, "endDate": end_date, "offset": offset}

        response = requests.post(api_url, json=request, headers=headers)
        json_response = response.json()
        code = response.status_code
        df = pd.json_normalize(json_response['data']['features'])
        return df

    # test0 = fetch_by_id(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], start_date= "8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM", offset = 0)
    # test1 = fetch_by_id(id= "6255d6681a1205e8b86623f0", start_date= "8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM", offset = 0)
    # test2 = fetch_by_id(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], offset = 0)
    # test3 = fetch_by_id(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364],start_date= "8/29/2003 12:00:00 AM", offset = 0)
    # test4 = fetch_by_id(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], end_date="8/31/2003 12:00:00 AM", offset = 0)
    # test5 = fetch_by_id(id= "6255d6681a1205e8b86623f0", offset = 0)
    # test6 = fetch_by_id(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], start_date= "8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM", offset = 100)
    #
    # test0b = fetch_by_title(title="COE Dredge Location", bbox=[-95.774704, 35.995683, -89.098843, 40.61364],start_date="8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM", offset=0)
    # test1b = fetch_by_title(title="COE Dredge Location", start_date="8/29/2003 12:00:00 AM",end_date="8/31/2003 12:00:00 AM", offset=0)
    # test2b = fetch_by_title(title="COE Dredge Location", bbox=[-95.774704, 35.995683, -89.098843, 40.61364], offset=0)
    # test3b = fetch_by_title(title="COE Dredge Location", bbox=[-95.774704, 35.995683, -89.098843, 40.61364],start_date="8/29/2003 12:00:00 AM", offset=0)
    # test4b = fetch_by_title(title="COE Dredge Location", bbox=[-95.774704, 35.995683, -89.098843, 40.61364],end_date="8/31/2003 12:00:00 AM", offset=0)
    # test5b = fetch_by_title(title="COE Dredge Location", offset=0)
    # test6b = fetch_by_title(title="COE Dredge Location", bbox=[-95.774704, 35.995683, -89.098843, 40.61364],start_date="8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM", offset=100)
