import requests as r
import time,os,wget,random
def let_me_see_see(number,var="sort=r18&size=original&type=json"):
    count = 0
    data1 = r.get(F"https://moe.jitsu.top/img/?{var}&num={number}")
    data2 = data1.json()
    for data3 in data2["pic"]:
        count += 1
        wget.download(data3,out=os.path.join(os.getcwd(),str(count)+".jpg"))
        time.sleep(1)