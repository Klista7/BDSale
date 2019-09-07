import pandas,requests,re,time
from bs4 import BeautifulSoup

'''
另一种思路，找名字，在找日期。
这样，就算还在下一级页面，也更好操作了
'''
#BD发售信息#
#提取BD发售日期信息
def getInfoHtml_1(ani,url):
    req = request_TimeOut(url)
    html_1 = req.content.decode('utf-8')
    bs_1 = BeautifulSoup(html_1)
    re_saletitle = re.compile(r'.?%s.?.*(\d|(①|②|③|④|⑤|⑥|⑦|⑧|⑨))$' %ani)
    re_saledata=re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    re_list=[re_saletitle,re_saledata]
    #找到之后，看子集里有没有日期（但有些未发售，未决定日期，但这不要紧不是吗，但还有在子标签的）

    #粗查找（先找名字，再找日期）
    sale_date=cu_getInfo(bs_1,re_list)
    # 先找一级界面且分卷的,二级界面就是深度查找（通用办法），首先名字，进入二级界面，再用粗方法
    if not sale_date:
        sale_date=xi_getInfo(bs_1,re_list,url)
    return sale_date
#粗提取
def cu_getInfo(bs,re_list):
    sale_date={}
    for juan_name in bs.find_all(text=re_list[0]):
        for i in juan_name.parents:
            juan_date=i.find(text=re_list[1])
            if juan_date:
                sale_date[juan_name]=juan_date.strip()
                break
    return sale_date
#细提取
def xi_getInfo(bs,re_list,url):
    sale_date={}
    date_sale={}
    for juan_name in bs.find_all(text=re_list[0]):
        a=juan_name.find_parent('a')
        if a:
            url_all=url_InAll(url,a['href'])
            html_juan = requests.get(url_all).content.decode('utf-8')
            bs_juan = BeautifulSoup(html_juan)
            date_sale=cu_getInfo(bs_juan,re_list)
        else:
            date_sale[juan_name]='打开卷页面失败'
        sale_date.update(date_sale)
    return sale_date


#BD发售页面（link）#
#提取BD界面（通过导航栏的方法）
def getBDHtml(hp):
    req=request_TimeOut(hp)
    html_0 = req.text  # get
    bs_0 = BeautifulSoup(html_0)  # 创建BS实例
    flag = 0  # 有无发售flag
    if bs_0.ul or bs_0.ol:  # ul,ol都不存在的情况的概率很低吧
        nav = bs_0.ul if (bs_0.ul) else bs_0.ol
    else:
        nav = None
    if nav:  # 有无导航栏
        for i in nav.find_all('a'):
            if re.search('Blu|BD', str(i.string)):
                url_all = url_InAll(hp, i['href'])
                #getInfoHtml_1(url_all, row.title)
                flag = 1
                return url_all
        if flag == 0:
            return 502#404，未找到BD信息页（没有导航栏）；502 尚无发售信息（找到导航栏，但没有BD页）
    else:
        return 404

#获取BD发售页面
def getBDInfo(data_0):
    data_hp = data_0[['title', 'HP']]  # 官网数据（日文名+HP）
    data_hp = data_hp.fillna(value='NoNe')  # 重新填充无为NoNe
    bd_info = []
    for row in data_hp.itertuples():  # 迭代各动画
        if row.HP != 'NoNe':  # 会有未取到的HP
            bdhtml_info = getBDHtml(row.HP)
            bd_info.append([row.title, bdhtml_info])
    bd_info = pandas.DataFrame(bd_info, columns=['title', 'bd_link'])
    data_0 = pandas.merge(data_0, bd_info, on='title', how='left')
    data_0.to_csv('data.csv')


#其他#
#得到可get的二级链接
def url_InAll(url1,url2):
    url_flag = re.match(r'(http.+)|(www.+)', url2)#此处匹配不完美
    if not url_flag:
        a=[t for t in url2.split('/',1) if re.match('(#)?\w+',t)]
        url2=url1+'/'+a[0]
    return url2

#构造数据结构(存储）
def struct_BDdata(jtitle,ctitle,bdinfo):
    pd_bdinfo = pandas.Series(bdinfo)
    pd_index = pandas.MultiIndex.from_product([[ctitle], pd_bdinfo.index], names=['title', 'juan_name'])
    pd_values = pd_bdinfo.values
    bdinfo = pandas.DataFrame(pd_values, index=pd_index, columns=['sale_date'])
    return bdinfo

def request_TimeOut(url):
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}
    while True:
        try:
            req=requests.get(url,headers=header)
            return req
        except requests.exceptions.ConnectionError:
            print('连接失败，正在重试。。。')
            time.sleep(2)

#一个是对HTML0进行操作（目的提取出bd发售界面）
#另一个就是对HTML1进行提取（目的获得发售信息）

data_0=pandas.read_csv("data.csv")#原始数据

#提取bd页面
if 'bd_link' not in data_0.columns:
    print('正在获取BD页面....')
    getBDInfo(data_0)
    data_0=pandas.read_csv("data.csv")
#可能出现BD页面改变，重新获取（其他页面亦是如此）
#只运行一次的程序
print(data_0)

#主戏：从BDlink里去获取BD发售信息
data_hp=data_0[['title','bd_link','cntitle']]#官网数据（日文名+HP）
data_hp=data_hp.fillna(value='NoNe')#重新填充无为NoNe
pd_bdall=pandas.DataFrame()
for bd_link_info in data_hp.itertuples():
    bd_link=bd_link_info.bd_link
    ani_name=bd_link_info.title
    if bd_link=='404':
        bd_info='未找到BD信息页'
    elif bd_link=='502':
        bd_info='尚无发售信息'
    elif bd_link=='NoNe':
        bd_info='无官网信息'
    else:
        #这里就是主提取包括数据结构的构建
        bd_info=getInfoHtml_1(ani_name,bd_link)
        bd_info=struct_BDdata(ani_name,bd_link_info.cntitle,bd_info)
        pd_bdall=pd_bdall.append(bd_info)
    print(bd_link_info.cntitle,ani_name,bd_info)
pd_bdall.to_csv('BD_Data.csv')
#存放，需要一对多，（基本完成）
#BD页面的解决办法：放在原始数据的panda结构，检测有没有这一栏（√）
#考虑提取BD网页要不要也放在一个函数里（√）
#之后要不要考虑把这整个变为一个对象来操作
#BUG:存在连接不上的情况，思路一：总体里使用选择性结构，思路二：单独操作
#网络连接问题，应该早点考虑的