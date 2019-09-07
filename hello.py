import tkinter
from tkinter import messagebox,StringVar
import random,time

def hit_me():
    a='你好'
    b='世界'
    c='hello world'
    d=[a,b,c]
    other=tkinter.Tk()
    for i in d:
        tkinter.Label(other,text=[i,'a']).pack()




#对窗口的设置
window=tkinter.Tk()
window.title('My Menu')
window.geometry('500x300')

#创建容器
menubar=tkinter.Menu(window)
#这里好像需要将这个部件与窗口连接

#创建各个菜单部件
startMenu=tkinter.Menu(menubar,tearoff=0)
startMenu.add_command(label='退出',command=window.quit)

setMenu=tkinter.Menu(menubar,tearoff=0)
setMenu.add_command(label='其他')

aboutMenu=tkinter.Menu(menubar,tearoff=0)
aboutMenu.add_command(label='关于我们')

#将各个部件放到容器里去
window.config(menu=menubar)#在窗口里，增加菜单容器
menubar.add_cascade(label='开始',menu=startMenu)
menubar.add_cascade(label='设置',menu=setMenu)
menubar.add_cascade(label='关于',menu=aboutMenu)

frame_sous=tkinter.Frame(window)
#搜索框创建
shru=tkinter.Entry(frame_sous)
def sous():#名字真好，正反读正好是搜索
    t=shru.get()
    print(t)
sous_b=tkinter.Button(frame_sous,text='搜索',command=sous)
#搜索框放置
frame_sous.pack()
shru.pack()
sous_b.pack()

#信息展示
frame_info=tkinter.Frame(window)
frame_ani=tkinter.Frame(frame_info)


l=['a','b','c']

#信息安放
frame_info.pack()
frame_ani.pack(side='left')

for i in l:
    tkinter.Label(frame_ani, text=i).pack()

frame_date = tkinter.Frame(frame_info)
frame_date.pack(side='right')

tkinter.Button(window,text='show',command=hit_me).pack()



window.mainloop()