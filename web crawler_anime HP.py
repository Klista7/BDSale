import requests,pandas,re
from bs4 import BeautifulSoup

def getInfoHP_db(url,ani_cname):#得到HP,name等信息
    data_bf = requests.get(url).content.decode('utf-8')
    bs_bf = BeautifulSoup(data_bf)
    ani_name = bs_bf.find(property="v:itemreviewed").string.lstrip(ani_cname).strip()
    ani_HP = bs_bf.find(id='info').find(text=re.compile('官方网站'))
    if ani_HP:
        a=ani_HP.parent.find_next_sibling('a')['href']
    else:
        a=''
    ani_info = [ani_name, ani_cname, a]
    return ani_info

def getBeforHP_db(ani_num):
    # 获取数据（json）
    # 三个季度140个#此处获取数据有问题，应该用循环
    url = 'https://movie.douban.com/j/new_search_subjects?sort=R&range=0,10&tags=%E5%8A%A8%E6%BC%AB&' \
          'start={}&countries=%E6%97%A5%E6%9C%AC'.format(ani_num)
    data = requests.get(url).text
    data = pandas.read_json(data, orient='split')  # 处理为可操纵数据
    data = data[['title', 'url']]
    ani_data = []
    for row in pandas.DataFrame.itertuples(data):  # 由函数处理得到动画信息列表
        ani_info = getInfoHP_db(row.url, row.title)
        ani_data.append(ani_info)
    return ani_data
#此处还是得好好规划一下
#动画名字可以从HP的title标签里拿

#get动画信息
ani_alldata=[]
ani_total=140#动画总数
i=0
while i<ani_total:
    ani_data=getBeforHP_db(i)
    ani_alldata+=ani_data
    i=i+20

data=pandas.DataFrame(ani_alldata,columns=['title','cntitle','HP'])
data.to_csv('data.csv')
'''
title换成原名，othernames(cntitle)都是译名，HP还是HP
'''
#对不起！未找到官网网址，请等待更新
#等待更新，将动画日文名获取，改为从官网title标签获取