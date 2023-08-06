from ntpath import join
import requests
import xml.etree.ElementTree as et
import pandas as pd
import pprint
import datetime
from time import time, sleep

def mask (date):
    mask = date.strftime("%m-%d-%Y-%H-%M-%S")
    return mask

def getWf_url(domain,key,wfid,start,end,*args,**kwargs):
    wfr = kwargs.get('wfr',"")
    asset = kwargs.get('asset',"")
    api = "GetWFReports.ashx?"
    userKey = "k=" + key
    sortOrder =  "&sr=" + "1" # 1 or 0
    workflow = "&wf=" + wfid
    startDate = "&s=" + mask(start)
    endDate = "&e=" + mask(end)
    wfReport = "&wfr=" + str(wfr)
    asset = "&a=" + str(asset)
    """
    unused params
    assetClass = "&ac="
    account = "&c="
    """

    urlBuild = domain + api + userKey + sortOrder + asset + wfReport + workflow + startDate + endDate
    #print(urlBuild)
    return urlBuild

def getWf_xml(urlBuild):
    response = requests.get(urlBuild).text
    #pprint.pprint(response)
    
    UC_root = et.fromstring(response)
    #returns <UC> as root tag

    #find headers in first <data> tag
    uc_headers = []
    for header in UC_root[0]:
        uc_headers.append(header.tag)
    
    #get data from within all the other <data> tags
    rows = []
    for data in UC_root[1:]:
        res = []
        for tag in uc_headers:
            res.append(data.find(tag).text)
        rows.append(res)
    #the result is a double array

    #drop the 'uc_' from the headers' text
    trimmed_headers = []
    for header in uc_headers:
        trimmed_headers.append(header[3:])

    wf_dataframe = pd.DataFrame(rows, columns=trimmed_headers)

    try:
        time_column = pd.to_datetime(wf_dataframe['WorkflowDate'])
        wf_dataframe['WorkflowDate'] = time_column
    except:
        pass
    
    #print(wf_dataframe)

    return wf_dataframe

def getWf_headers(urlBuild):
    response = requests.get(urlBuild).text
    
    UC_root = et.fromstring(response)
    #returns <UC> as root tag

    #find headers in first <data> tag and start dict for Dataframe
    uc_headers = []
    for header in UC_root[0]:
        uc_headers.append(header.tag)
    
    #drop the 'uc_' from the headers' text
    trimmed_headers = []
    for header in uc_headers:
        trimmed_headers.append(header[3:])

    #returns as list/array
    return trimmed_headers

def getWf(key,wfid,start,end,*args,**kwargs):
    # unpack optional variables
    wfrid = kwargs.get('wfrid','')
    assetid = kwargs.get('assetid','')
    #interval in days
    interval = kwargs.get('interval',14)
    domain = kwargs.get('domain','https://ucld.us/')
    
    if wfrid == "":
        step_end = end
        url_collections = []
        while step_end > start:
            step_start = step_end - datetime.timedelta(days=interval)
            if step_start < start:
                step_start = start
            temp_df = getWf_url(domain,key,wfid,step_start,step_end,asset=assetid)
            url_collections.append(temp_df)
            step_end = step_start
        
        #get the headers without attributes
        small_offset = end+datetime.timedelta(seconds=1)
        headers_url = getWf_url(domain,key,wfid,end,small_offset)
        headers = getWf_headers(headers_url)
    else:
        url_collections = [getWf_url(domain,key,wfid,start,end,wfr=wfrid,asset=assetid)]
        
    data = []
    time1 = time()
    for url in url_collections:
        time2 = time()
        result = getWf_xml(url)
        try:
            include_attributes = kwargs.get('include_attributes',None)
            if include_attributes == False and wfid != "":
                result = result[headers]
        except:
            pass
        data.append(result)
        time3 = time()
        print(f"{round(time3-time2,2)}s for {interval} day call. - {url}")
        #sleep(5)
    time4 = time()
    #print(f"{round(time4-time1,2)}s for all data.")

    data_clean = [df for df in data if not df.empty]
    
    #join all dataframes together
    try:
        join_data = pd.concat(data_clean,sort=False)
        final_result = join_data.sort_values(by=['WorkflowDate'])
    except:
        final_result = data[0]
        
    return final_result


if __name__ == '__main__':
    ""