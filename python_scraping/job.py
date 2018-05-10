from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import DataFrame
import time
import datetime

# set the scraping shell
def p_range():
    start_page = input('請輸入開始頁數:')
    end_page = input('請輸入結束頁數:')
    global key_word
    key_word = input('請輸入關鍵字:')
    p_r = range(int(start_page), int(end_page) + 1)
    global full
    full = []
    for p in p_r :
        try:
            url = 'https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007001000&keyword=' + key_word + '&area=6001001000&order=1&asc=0&page=' + str(p) + '&mode=s&jobsource=n104bank1'
            html_job = urlopen(url)
            bsObj_job = BeautifulSoup(html_job, "lxml")

            jobName = []
            companyName = []
            temp = []
            place = []
            year = []
            school = []
            prop = []
            salary = []
            desc_empty = []
            special = []
            size = [] 
            
            # 職稱與公司名稱
            def jobCompany():
                name_list = bsObj_job.findAll('a', {'target':'_blank'})
                for elem in name_list:
                    if 'class' in elem.attrs:
                        if elem.attrs['class'][0] == 'js-job-link':
                            jobName.append(elem.get_text())
                    elif 'title' in elem.attrs:
                        companyName.append(elem.get_text())
            #地點、經歷、學歷
            def mix():        
                mix_list = bsObj_job.findAll('ul', {'class':'b-list-inline b-clearfix job-list-intro b-content'})
                for num in range(len(mix_list)):
                    k = mix_list[num].findAll('li')
                    for i in range(len(k)):
                        if i == 0: 
                            place.append(k[i].get_text())
                        elif i == 1:
                            year.append(k[i].get_text())
                        elif i == 2:
                            school.append(k[i].get_text())
                            
            #薪資、公司特殊性質、公司規模(一)
            def collectProperties():                 
                full_list = bsObj_job.findAll('article') #取出總表
                for num_ in range(len(full_list)):
                    severalProp = [] #建立複數屬性的預設陣列
                    temProp = full_list[num_].findAll('span', {'class':"b-tag--default"}) #取出複數屬性
                    for l in range(len(temProp)):
                        severalProp.append(temProp[l].get_text()) #塞進預設空陣列
                    prop.append(severalProp) #將陣列塞進大陣列形成二維陣列
                empty_n = 0
                for i in prop:
                    if i == []:
                        empty_n += 1
                for t in range(empty_n):
                    prop.pop() # 清除空陣列
            
            #薪資、公司特殊性質、公司規模(二)
            def seperateProperties():
                #薪資
                def sal():
                    for j in range(len(prop)):
                        for k in prop[j]:
                            if k == '面議' or re.match(".*(萬|元).*", k) is not None or k == '依公司規定':
                                salary.append(k)
                                break
                #公司特殊性質
                def spec():    
                    for j_ in range(len(prop)):
                        if '外商公司' in prop[j_]:
                            special.append('外商公司')
                        elif '上市上櫃' in prop[j_]:
                            special.append('上市上櫃')
                        else:
                            special.append('') #不符合則塞進空值
                #公司規模
                def siz():
                    for j__ in range(len(prop)):
                        tes = 0
                        for t in prop[j__]:            
                            if re.match(".*(員工).*", t) is not None:
                                size.append(t)
                            else:
                                tes += 1
                                if tes == len(prop[j__]):
                                    size.append('')

                def executeSep():
                    sal()
                    spec()
                    siz()
                executeSep()
            #工作說明
            def description():
                full_list = bsObj_job.findAll('article') #取出總表
                for num__ in range(len(full_list)-3):
                    desc = full_list[num__].find('p', {'class':'job-list-item__info b-clearfix b-content'})
                    if desc!= None:
                        desc_empty.append(desc.get_text())
                    else:
                        desc_empty.append('')
            #呼叫函示並將資料放入字典
            def summarize(): 
                jobCompany()
                mix()
                collectProperties()
                seperateProperties()
                description()
                global data
                data = {'jobName':jobName, 'companyName':companyName, 'place':place,'experience':year,
                        'school':school, 'salary':salary, 'special':special, 'companySize':size, 'description':desc_empty}   
            summarize()
            
            #轉成df形式
            scra_job = DataFrame(data)
            full.append(scra_job)
            print("目前頁面: 第" + str(p) + '頁')
            time.sleep(1)
            
        #except ValueError:
            #print('ValueError: arrays must all be same length')
        except AttributeError:
            print('AttributeError')
        #except Exception:
            #print('Unknown Exception')
p_range()
all_list = pd.concat(full)
cols = ['jobName','companyName','salary','experience','place',
        'companySize','special','school','description']
all_list = all_list[cols]
print(all_list.head())
dt = datetime.datetime.now()
today = str(dt.year)+'-'+str(dt.month)+'-'+str(dt.day)
name = 'scraJob_' + key_word + '_' + today + '.csv'
all_list.to_csv(name, index = False)