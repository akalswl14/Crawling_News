#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pandas as pd
import time

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< naver 뉴스 전문 가져오기 >_select 사용
- 네이버 뉴스만 가져와서 결과값 조금 작음 
- 결과 메모장 저장 -> 엑셀로 저장 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
RESULT_PATH = '/Users/carly/Development/crawling/results'
eng_company=["EPA연합뉴스","AP연합뉴스"]
start = time.time()


# In[ ]:


def del_parenth(btext):
    while True:
        start = btext.find("(")
        if start == -1 :
            break
        else:
            end = btext.find(")")
            l = btext.split(btext[start:end+1])
            btext = l[0]+l[1]
    while True:
        start = btext.find("[")
        if start == -1 :
            break
        else:
            end = btext.find("]")
            l = btext.split(btext[start:end+1])
            btext = l[0]+l[1]
    while True:
        start = btext.find("<")
        if start == -1 :
            break
        else:
            end = btext.find(">")
            l = btext.split(btext[start:end+1])
            btext = l[0]+l[1]
    return btext


# In[ ]:


def mark_replace(btext):
    btext = btext.replace(",","")
    btext = btext.replace("..","")
    btext = btext.replace(". "," ")
    btext = btext.replace("'","")
    btext = btext.replace("\"","")
    btext = btext.replace("~"," ")
    btext = btext.replace("◇","")
    btext = btext.replace("▲",",")
    btext = btext.replace("%","퍼센트")
    btext = btext.replace("·"," ")
    btext = btext.replace("/"," ")
    btext = btext.replace("‘"," ")
    btext = btext.replace("“"," ")
    btext = btext.replace("	","")
    btext = btext.replace("=","")
    btext = btext.replace("’","")
    btext = btext.replace("”","")
    btext = btext.replace("【","")
    btext = btext.replace("】","")
    btext = btext.replace("~"," ")
    btext = btext.replace("  ","")
    btext = btext.replace("-","")
    btext = btext.replace("中","중")
    btext = btext.replace("■","")
    btext = btext.replace(":","")
    btext = btext.replace("☎","")
    btext = btext.replace("ㅠㅠ","") 
    btext = btext.replace("→","")
    btext = btext.replace("｢","")
    btext = btext.replace("｣","")
    btext = btext.replace("ㅇ","")
    btext = btext.replace("Δ","")
    btext = btext.replace("▷","")
    btext = btext.replace("「","")
    btext = btext.replace("」","")
    btext = btext.replace(">","")
    btext = btext.replace("]","")
    btext = btext.replace(")","")
    btext = btext.replace("...","")
    btext = btext.replace("..","")
    return btext


# In[ ]:


def get_news(url_news):
    news_detail = []
    breq = requests.get(url_news)
    bsoup = BeautifulSoup(breq.content, 'html.parser')
    title = bsoup.select("title")[0].text
    news_detail.append(title)
    pdate = bsoup.select('.t11')[0].get_text()
    news_detail.append(pdate)
    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', "")
    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가function _flash_removeCallback() {}", "")
    btext = btext[:btext.find("@")]
    btext = btext[:btext.find("▶")]
    length = len(btext)
    idx = length-25 + btext[length-25:length].find(".") # 기사 마지막 마침표를 찾기 위해서.
    btext = btext[:idx+1]
    btext = del_parenth(btext)
    btext = mark_replace(btext)
    news_detail.append(btext)
    news_detail.append(url_news)
    pcompany = bsoup.select('#footer address')[0].a.get_text()
    news_detail.append(pcompany)
    return news_detail #제목,날짜,기사,url,신문사


# In[ ]:


def find_title(url):
    if url.select(".photo") == []:
        title = url.select("dt")[0].text
    else :
        title = url.select("dt")[1].text
    return title


# In[ ]:


def crawler(yesterday):
    page = 1
    f = open("/Users/carly/Development/crawling/results/"+yesterday+".txt", 'w', encoding='utf-8')
    yesterday = str(yesterday)
    num = 0
    pageremain = True
    ExcelData = []
    prepage_title1 = 0
    prepage_title2 = 0
    prepage_title3 = 0
    txt = ""
    while pageremain:
    
        print(page)
    
        url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=summary&date=" + yesterday + "&page="+str(page)
        
        req = requests.get(url)
        print(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        if num == 0:
            num = len(soup.select(".writing"))
        elif num > len(soup.select(".writing")):
            pageremain = False
        dl = soup.select("dl")
        title1 = find_title(dl[0])
        title2 = find_title(dl[1])
        title3 = find_title(dl[len(dl)-1])
        if prepage_title1 == 0 :
            prepage_title1 = title1
            prepage_title2 = title2
            prepage_title3 = title3
        elif prepage_title1 == title1 and prepage_title2 == title2 and prepage_title3 == title3:
            break
        else:
            prepage_title1 = title1
            prepage_title2 = title2
            prepage_title3 = title3
        for urls in dl:
            try :
                company = urls.select(".writing")[0].text
                title = find_title(urls)
                print(company)
                if(company not in eng_company) and (title.find("の") == -1) and (title.find("Copyright") == -1) and (title.find("연표") == -1): #영문 기사 제외
                    url_news = urls.select("dt a")[0]["href"]
                    news_detail = get_news(url_news)
                    ExcelData.append(news_detail)
                    print(news_detail[0])
                    txt += news_detail[2]
                else:
                    print("<<영문, 일문 혹은 연표기사입니다.>>")
            except Exception as e:
                print(e)
                continue
        page += 1
        
        f.write(txt+"\n")  # new style
    f.close()
    return ExcelData


# In[ ]:


def excel_make(ExcelData,yesterday):
    col = ['제목','작성시각','본문', 'url','신문사']
    df = pd.DataFrame(ExcelData,columns=col)
    df.to_csv(RESULT_PATH+'/Excel'+yesterday+'.csv',encoding='utf-8-sig')


# In[ ]:


def main():
    yesterday = str(int(datetime.today().strftime("%Y%m%d"))-1)
    ExcelData = crawler(yesterday)    
    excel_make(ExcelData,yesterday) #엑셀로 만들기


# In[ ]:


main()
print("소요시간 :", time.time() - start)

