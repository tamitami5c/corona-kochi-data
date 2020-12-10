import urllib
import os
import json
import csv
import datetime

import requests

def get_file_name(url):
    path=urllib.parse.urlparse(url).path
    return os.path.split(path)[-1]

def download_file(url):
    file_name=get_file_name(url)

    response=requests.get(url)
    if response.status_code!=requests.codes.ok:
        raise Exception("status_code!=200")
    response.encoding=response.apparent_encoding

    with open(file_name,"wb") as f:
        f.write(response.content)
    return file_name

def daterange(start_date,end_date):
    for n in range(int((end_date-start_date).days)):
        yield start_date+datetime.timedelta(n)

def main():
    #高知県のopendata
    url="https://www.pref.kochi.lg.jp/soshiki/111301/files/2020041300141/390003_kochi_covid19_patients.csv"

    file_name=download_file(url)
    #日付とその日の陽性者数をセットしていく
    data={}
    with open(file_name) as f:
        reader=csv.reader(f)
        _=next(reader) #headerは飛ばす
        
        for  row in reader:
            date=datetime.datetime.strptime(row[4],"%Y/%m/%d").date()
            date=date.strftime("%Y-%m-%d") #これってisoformat?
            print(date)

            if date in data:
                data[date]+=1
            else:
                data[date]=1

    #json形式にするためにフォーマット整える
    #初めて陽性者が確認された日から後の日付で、陽性者が確認されていない日は 0を記入する。
    date_list=sorted(data.keys(),key=lambda x: datetime.date.fromisoformat(x))
    first_date=datetime.date.fromisoformat(date_list[0])
    last_date=datetime.date.fromisoformat(date_list[-1])
    print("日付(最初):",first_date)
    print("日付(最後):",last_date)


    result=[]
    for d in daterange(first_date,last_date):
        date=d.isoformat()
        count=data[date] if  (date in data) else 0
        item={
            "date":date,
            "count":count
        }
        result.append(item)

    #jsonに書きだし
    data={
        "data":result
    }
    print(data)

    with open("kochi_data.json","w") as f:
        json.dump(data,f,indent=4)

if __name__ == "__main__":
    main()