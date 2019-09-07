#/usr/bin/env/ python
# -*- coding: utf-8 -*-

import requests,pandas,re,tkinter,os,time
from bs4 import BeautifulSoup
from tkinter import messagebox

'''
BD发售信息提取

作者：nKsnC
创建时间：2019年8月1日14:43:14
版本：v0.1(2019.8.4)
'''
#函数#

#搜索按钮（注：做完后，记得将此函数，放在最下面）
def sous_Button():
    sous_str=sous_entry.get()
    if os.path.exists('data.csv')&os.path.exists('BD_Data.csv'):
        sous_str=sous_name(sous_str)#此处有个问题，是统一处理为中文，还是日文呢，目前日文标题有些缺失
        if sous_str.empty:#sous_str返回row
            print_GUImess('空！没有发售信息，已发售完或动画名有误.')
        else:
            main_bdinfo=main_getBDInfo(sous_str.values[0])#这一块可以搞一个急速搜索（本地查找与网络查找谁快呢）和搜索#此处需要单独搜索模块
            print_GUIINFO(main_bdinfo)#sous_str.values[0]，这个是搜索那边
    else:
        net_get_All()

#获取BD发售信息
def main_getBDInfo(pd_str):#（未完成）
    #打开文件可能会失败，需注意（编码？）
    #改变BD数据的信息了（要包括中文名，以及更好的索引结构）（未完成）
    bd_data=pandas.read_csv('BD_Data.csv')
    need_data=bd_data[bd_data['title']==pd_str]#目前只支持日文名
    if need_data.empty:
        #没有找到发售信息
        ani_Check(pd_str)
    else:
        #找到了我该怎么返回呢
        return need_data

#检查HP,BD页面是否存在
def ani_Check(pd_str):
    check_pdata=pandas.read_csv('data.csv')
    check_row=check_pdata[(check_pdata['title']==pd_str)|(check_pdata['cntitle']==pd_str)]#更改为正则
    if check_row.isna().HP.values:
        # 对不起！未找到官网网址，请等待更新
        print_GUImess('对不起！未找到官网网址，请等待更新')
    else:
        check_bdlink=check_row.bd_link.values#之后构建一套属于自己的错误代码体系
        if check_bdlink=='404':
            # 对不起！未找到BD发售界面，请等待更新（404）
            print_GUImess('对不起！未找到BD发售界面，请等待更新（404）')
        elif check_bdlink=='502':
            #对不起！尚无发售信息，请等待更新（502）
            print_GUImess('对不起！尚无发售信息，请等待更新（502）')
        else:
            #这之后，是再去查找呢（如果是这个那为什么我一开始不去找呢），还是去官网爬取呢
            print_GUImess('未知')

#搜索模块
def sous_name(ss_str):
    sous_pdata = pandas.read_csv('data.csv')
    re_patten = re.compile(ss_str)
    sous_row = sous_pdata[
        (sous_pdata['title'].str.contains(re_patten)) | (sous_pdata['cntitle'].str.contains(re_patten))]
    if not sous_row.empty:
        sous_row=sous_row.cntitle
    return sous_row

#完全运行获取BD发售信息
def net_get_All():
    if not os.path.exists('AnimeInfo.csv'):
        net_get_HP()
    if not os.path.exists('BD_Data.csv'):
        net_get_BDInfo()
    sous_button()

#爬取动画HP（豆瓣）
def net_get_HP():

    print('爬取动画官网中，请等待。。。')

    # 得到HP,日文名等信息
    def getInfoHP_db(url, ani_cname):
        print(ani_cname)
        data_bf = requests.get(url).content.decode('utf-8')
        bs_bf = BeautifulSoup(data_bf)
        ani_name = bs_bf.find(property="v:itemreviewed").string.lstrip(ani_cname).strip()
        ani_HP = bs_bf.find(id='info').find(text=re.compile('官方网站'))
        if ani_HP:
            a = ani_HP.parent.find_next_sibling('a')['href']
        else:
            a = ''
        ani_info = [ani_name, ani_cname, a]
        return ani_info

    #获得前置数据
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

    # 此处还是得好好规划一下
    # 动画名字可以从HP的title标签里拿

    # get动画信息
    ani_alldata = []
    ani_total = 140  # 动画总数
    i = 0
    while i < ani_total:
        ani_data = getBeforHP_db(i)
        ani_alldata += ani_data
        i = i + 20

    data = pandas.DataFrame(ani_alldata, columns=['title', 'cntitle', 'HP'])
    data.to_csv('AnimeInfo.csv')
    '''
    title换成原名，othernames(cntitle)都是译名，HP还是HP
    '''
    # 对不起！未找到官网网址，请等待更新
    # 等待更新，将动画日文名获取，改为从官网title标签获取

#爬取BD发售信息（在官网）
def net_get_BDInfo():

    '''
    另一种思路，找名字，在找日期。
    这样，就算还在下一级页面，也更好操作了
    '''

    # BD发售信息#
    # 提取BD发售日期信息
    def getInfoHtml_1(ani, url):
        req = request_Connection(url)
        html_1 = req.content.decode('utf-8')
        bs_1 = BeautifulSoup(html_1)
        re_saletitle = re.compile(r'.?%s.?.*(\d|(①|②|③|④|⑤|⑥|⑦|⑧|⑨))$' % ani)
        re_saledata = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        re_list = [re_saletitle, re_saledata]
        # 找到之后，看子集里有没有日期（但有些未发售，未决定日期，但这不要紧不是吗，但还有在子标签的）

        # 粗查找（先找名字，再找日期）
        sale_date = cu_getInfo(bs_1, re_list)
        # 先找一级界面且分卷的,二级界面就是深度查找（通用办法），首先名字，进入二级界面，再用粗方法
        if not sale_date:
            sale_date = xi_getInfo(bs_1, re_list, url)
        return sale_date

    # 粗提取
    def cu_getInfo(bs, re_list):
        sale_date = {}
        for juan_name in bs.find_all(text=re_list[0]):
            for i in juan_name.parents:
                juan_date = i.find(text=re_list[1])
                if juan_date:
                    sale_date[juan_name] = juan_date.strip()
                    break
        return sale_date

    # 细提取
    def xi_getInfo(bs, re_list, url):
        sale_date = {}
        date_sale = {}
        for juan_name in bs.find_all(text=re_list[0]):
            a = juan_name.find_parent('a')
            if a:
                url_all = url_InAll(url, a['href'])
                html_juan = requests.get(url_all).content.decode('utf-8')
                bs_juan = BeautifulSoup(html_juan)
                date_sale = cu_getInfo(bs_juan, re_list)
            else:
                date_sale[juan_name] = '打开卷页面失败'
            sale_date.update(date_sale)
        return sale_date

    # BD发售页面（link）#
    # 提取BD界面（通过导航栏的方法）
    def getBDHtml(hp):
        req = request_Connection(hp)
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
                    # getInfoHtml_1(url_all, row.title)
                    flag = 1
                    return url_all
            if flag == 0:
                return '502'  # 404，未找到BD信息页（没有导航栏）；502 尚无发售信息（找到导航栏，但没有BD页）
        else:
            return '404'

    # 获取BD发售页面
    def getBDInfo(data_0):
        data_hp = data_0[['title', 'HP']]  # 官网数据（日文名+HP）
        data_hp = data_hp.fillna(value='NoNe')  # 重新填充无为NoNe
        bd_info = []
        i=1
        for row in data_hp.itertuples():  # 迭代各动画
            print('%d/140'% i)
            i+=1#计数器
            if row.HP != 'NoNe':  # 会有未取到的HP
                bdhtml_info = getBDHtml(row.HP)
                bd_info.append([row.title, bdhtml_info])
        bd_info = pandas.DataFrame(bd_info, columns=['title', 'bd_link'])
        data_0 = pandas.merge(data_0, bd_info, on='title', how='left')
        data_0.to_csv('data.csv')


    # 其他#
    # 得到可get的二级链接
    def url_InAll(url1, url2):
        url_flag = re.match(r'(http.+)|(www.+)', url2)  # 此处匹配不完美
        if not url_flag:
            a = [t for t in url2.split('/', 1) if re.match('(#)?\w+', t)]
            url2 = url1 + '/' + a[0]
        return url2

    # 构造数据结构(存储）
    def struct_BDdata(jtitle, ctitle, bdinfo):
        pd_bdinfo = pandas.Series(bdinfo)
        pd_index = pandas.MultiIndex.from_product([[ctitle], pd_bdinfo.index], names=['title', 'juan_name'])
        pd_values = pd_bdinfo.values
        bdinfo = pandas.DataFrame(pd_values, index=pd_index, columns=['sale_date'])
        return bdinfo

    #处理get连接失败的（不一定是超时)
    def request_Connection(url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}
        while True:
            try:
                req = requests.get(url, headers=header)
                return req
            except requests.exceptions.ConnectionError:
                print('连接失败，正在重试。。。')
                time.sleep(2)

    # 一个是对HTML0进行操作（目的提取出bd发售界面）
    # 另一个就是对HTML1进行提取（目的获得发售信息）

    data_0 = pandas.read_csv("data.csv")  # 原始数据

    # 提取bd页面
    if 'bd_link' not in data_0.columns:
        print('正在获取BD页面....')
        getBDInfo(data_0)
        data_0 = pandas.read_csv("AnimeInfo.csv")
    # 可能出现BD页面改变，重新获取（其他页面亦是如此）
    # 只运行一次的程序
    print(data_0)

    # 主戏：从BDlink里去获取BD发售信息
    data_hp = data_0[['title', 'bd_link', 'cntitle']]  # 官网数据（日文名+HP）
    data_hp = data_hp.fillna(value='NoNe')  # 重新填充无为NoNe
    pd_bdall = pandas.DataFrame()
    for bd_link_info in data_hp.itertuples():
        bd_link = bd_link_info.bd_link
        ani_name = bd_link_info.title
        if bd_link == '404':
            bd_info = '未找到BD信息页'
        elif bd_link == '502':
            bd_info = '尚无发售信息'
        elif bd_link == 'NoNe':
            bd_info = '无官网信息'
        else:
            # 这里就是主提取包括数据结构的构建
            bd_info = getInfoHtml_1(ani_name, bd_link)
            bd_info = struct_BDdata(ani_name, bd_link_info.cntitle, bd_info)
            pd_bdall = pd_bdall.append(bd_info)
        print(bd_link_info.cntitle, ani_name, bd_info)
    pd_bdall.to_csv('BD_Data.csv')
    # 存放，需要一对多，
    # BD页面的解决办法：放在原始数据的panda结构，检测有没有这一栏
    # 考虑提取BD网页要不要也放在一个函数里
    # 之后要不要考虑把这整个变为一个对象来操作

#GUI信息显示
def print_GUImess(ts_str):
    ts=messagebox.showinfo(title='提示',message=ts_str)
    print(ts)
def print_GUIINFO(pd_data):
    sale_Window=tkinter.Tk()
    sale_Window.title(pd_data.title.values[0])
    sale_Window.geometry('350x150')
    for i in pd_data.itertuples():
        tkinter.Label(sale_Window,text=('%s:%s'% (i.juan_name,i.sale_date))).pack()

#GUI界面#

#窗口设置
main_gui=tkinter.Tk()
main_gui.title('BD Sale')
main_gui.geometry('500x300')

#关于窗口设置
def GUI_about():
    about_gui = tkinter.Tk()
    about_gui.title('关于')
    about_gui.geometry('200x100')
    tkinter.Label(about_gui,text='BD发售信息提取\n').pack()
    tkinter.Label(about_gui,text='版本：开发中').pack()

def BDdata_update():
    net_get_BDInfo()

#菜单创建
menubar=tkinter.Menu(main_gui)
main_gui.config(menu=menubar)

help_menu=tkinter.Menu(menubar,tearoff=0)
help_menu.add_command(label='关于',command=GUI_about)#弹出窗口，显示信息【版本，作者】（未完成）

menubar.add_cascade(label='帮助',menu=help_menu)

#搜索建立
sous_frame=tkinter.Frame(main_gui)
sous_entry=tkinter.Entry(sous_frame)
sous_button=tkinter.Button(sous_frame,text='搜索',command=sous_Button)#搜索输入的名字，返回在。。。（未完成）
update_button=tkinter.Button(sous_frame,text='更新',command='BDdata_update')


sous_frame.pack()
sous_entry.grid(row=1,column=1)
sous_button.grid(row=1,column=2,padx=10)
update_button.grid(row=1,column=3)



main_gui.mainloop()

'''
参考代码信息：(更改为字符串）
404，未找到（网络方面）
    404001:未找到官网信息
    404002：未找到BD页面
111，未找到（本机方面）
    111001：未找到官网信息
    111002：未找到BD页面（链接）
    111003：未找到该词条
'''
#还有一种所有已发售的动画（解决办法：超过140的动画全部标记为已发售）
#当有一个链接未响应怎么办，不可能在重新来过吧（之后在重新，还是填充式）
#目前BUG：链接超时
#不支持模糊搜索（√）
#搜索模块应该单独做，目前不支持（多值检索）

'''
两个问题：
一，输出显示
二，bd发售抓取
'''
