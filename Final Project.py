import json
import unittest
import os
import requests

api_key = "aa22fc25508e6ebea46f7992e6395391"

def request_url(company_name):
    url = "https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&limit=3&apikey=989b7d0dacf40d04a9e654615aa9cafe"
    final_url = url.format(company_name)
    return final_url 

def get_etf_company(etf): 
    result = [] 
    url = "https://financialmodelingprep.com/api/v3/etf-holder/{}?apikey=989b7d0dacf40d04a9e654615aa9cafe"
    final_url = url.format(etf)
    r = requests.get(final_url)
    try:
        k = json.loads(r.text) 
        for i in k: 
            if i["asset"] != None :
                result.append(i["asset"])  
        return result 
    except:
        print("Error")
        return None 
    
    
def get_data_json(company_name):
    url = request_url(company_name)
    r = requests.get(url)
    k = json.loads(r.text)  
    try: 
        result = []
        for i in k: 
            info = {} 
            info["quarter"] = i["date"]
            info["revenue"] = i["revenue"]
            info['grossProfit'] = i["grossProfit"]
            info['grossProfitRatio'] = i["grossProfitRatio"]
            result.append(info)
        return result 
    except:
        print("Error")
        return None 



def main(): 
    final_data = {}
    eft = "XRT"
    company_names = get_etf_company(eft)
    for company_name in company_names: 
        a = get_data_json(company_name)
        final_data[company_name] = a
    json_data = json.dumps(final_data)
    print(json_data)


    


if __name__ == "__main__":
    main()

