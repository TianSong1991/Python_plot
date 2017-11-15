# coding: utf-8

import os
import pymysql
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import seaborn as sns
from ggplot import *


#配置MySQL

conn = pymysql.connect(host='127.0.0.1', port=3306, user='*****', passwd='*****',db='******',charset='utf8')

cur = conn.cursor()

# sql语句
xybase = "SELECT  f4 as ajbh,f5 as kehu, f8 as shfzh18,f22 as ywy,f14 as zjqkje,              f15 as zjshje,f19 as jdsj from xybase where f22 is not null and f5 in ('兴业','广发')"

# 利用pandas 模块导入mysql数据
mysqlxybase = pd.read_sql(xybase, conn)

# sql语句
xydzd = "SELECT f23 as ajbh,f2 as kehu, f1 as shfzh18,f18 as ywy,f7 as hkrq,f10 as hkmx,              f17 as hkbz from xydzd where f10 > 0  and f2 in ('兴业','广发')"

# 利用pandas 模块导入mysql数据
mysqlxydzd = pd.read_sql(xydzd, conn)

# sql语句
mysqlprovince = "SELECT * from province"

# 利用pandas 模块导入mysql数据
province = pd.read_sql(mysqlprovince, conn)

xydzd = mysqlxydzd

xydzd['hkmx'] = xydzd['hkmx'].astype(float)
xydzd['hkbz'] = xydzd['hkbz'].astype(int)

xydzd = xydzd[xydzd.hkbz==1]
xydzd = xydzd[xydzd.hkmx>0]

xydzddata =xydzd[['ajbh','kehu','hkrq','hkmx','shfzh18']]

xydzddata["shfzhnum"] = xydzddata["shfzh18"].str.len()
xydzddata = xydzddata[xydzddata.shfzhnum==18]
xydzddata["bornyear"]=xydzddata["shfzh18"].str.slice(6,10)
xydzddata["sex"]=xydzddata["shfzh18"].str.get(16)
xydzddata["address"]=xydzddata["shfzh18"].str.slice(0,2)
xydzddata["shfzhnum"] = xydzddata["shfzh18"].str.len()

xydzddata['year'] = xydzddata['hkrq'].str.slice(0,4).astype(int)
xydzddata['month'] = xydzddata['hkrq'].str.slice(5,7).astype(int)

xydzddata["nnn"] = 1
xydzddata["bornyear"] = xydzddata["bornyear"].astype(int)
xydzddata["age"] = 2017-xydzddata["bornyear"]
xydzddata["sex"] = xydzddata["sex"].astype(int)
xydzddata["sex"][xydzddata["sex"]%2==0]='女'
xydzddata["sex"][xydzddata["sex"]!='女']='男'

xydzddata['address'] = xydzddata['address'].astype(int)

xydzddata = pd.merge(xydzddata,province, left_on='address', right_on='shfnum', left_index=False, right_index=False ,how='left')
xydzddata = xydzddata[['ajbh','kehu','hkrq','hkmx','shfzh18','sex','age','province','year','month','nnn']]
xydzddata = xydzddata[xydzddata.year>2015]

#每个客户每月回款情况
xydzdhkmx = xydzddata['hkmx'].groupby([xydzddata['kehu'], xydzddata['year'], xydzddata['month']]).sum().reset_index()

#每个月还款次数
xydzddata1 = xydzddata[xydzddata.hkmx>0]
hkcsh = xydzddata1['ajbh'].groupby([xydzddata1['kehu'], xydzddata1['year'], xydzddata1['month']]).count().reset_index()

#每个月还款案件
xydzddata2 = xydzddata[xydzddata.hkmx>0]
xydzddata2 = xydzddata2[['ajbh','kehu','year','month']]
xydzddata2 = xydzddata2.drop_duplicates()
hkaj = xydzddata2['ajbh'].groupby([xydzddata1['kehu'], xydzddata1['year'], xydzddata1['month']]).count().reset_index()

#地区图
region = xydzddata1['nnn'].groupby([xydzddata1['kehu'], xydzddata1['year'], xydzddata1['province']]).count().reset_index()

bins = [18,30,40,50,100]

group_names = ['20-30','30-40','40-50','50以上']

xydzddata1['age1']=pd.cut(xydzddata1['age'],bins,labels=group_names)

agedata = xydzddata1['nnn'].groupby([xydzddata1['kehu'], xydzddata1['age1']]).count().reset_index()
agedata = agedata[(agedata.kehu == '兴业') | (agedata.kehu == '广发')]

mysqlxybase['zjqkje'] = mysqlxybase['zjqkje'].astype(float)
mysqlxybase['zjshje'] = mysqlxybase['zjshje'].astype(float)

xybase = mysqlxybase
xybasedata = xybase[['ajbh','kehu','shfzh18','zjqkje','zjshje','jdsj']]
xybasedata = xybasedata[xybasedata.zjqkje>0]

xybasedata['year'] = xybasedata['jdsj'].str.slice(0,4).astype(int)
xybasedata['month'] = xybasedata['jdsj'].str.slice(5,7).astype(int)

xybasedata = xybasedata[xybasedata.year>2015]

#xybase去重
xybasedata = xybasedata.drop_duplicates()

xybasezhanbi = xybasedata[['zjqkje','zjshje']].groupby([xybasedata['kehu'], xybasedata['year'], xybasedata['month']]).sum().reset_index()

xybasezhanbi['zhanbi'] =round(xybasezhanbi['zjshje']/xybasezhanbi['zjqkje'],5)

xingyehkmx = xydzdhkmx[(xydzdhkmx.kehu == '兴业')]
guangfahkmx = xydzdhkmx[(xydzdhkmx.kehu == '广发')]

get_ipython().magic('matplotlib inline')
sns.set_style("whitegrid")
sns.set_context("talk")
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] #指定默认字体  
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
ax = sns.barplot(x="month", y="hkmx", hue="year", data=xingyehkmx)
ax.set_xlabel('月份',fontsize=15)
ax.set_ylabel('还款总额',fontsize=15)
ax.set_title('兴业客户',fontsize=15)
plt.show()

ax1 = sns.barplot(x="month", y="hkmx", hue="year", data=guangfahkmx)
ax1.set_xlabel('月份',fontsize=15)
ax1.set_ylabel('还款总额',fontsize=15)
ax1.set_title('广发客户',fontsize=15)
plt.show()

xingyehkzhb = xybasezhanbi[(xybasezhanbi.kehu == '兴业')]
guangfahkzhb = xybasezhanbi[(xybasezhanbi.kehu == '广发')]
xingyehkzhb['year'] = xingyehkzhb['year'].astype(str)
guangfahkzhb['year'] = guangfahkzhb['year'].astype(str)

ggplot(aes(x='month', y='zhanbi', colour='year'), data=xingyehkzhb) +   geom_point()+    geom_line()+    xlab('月份')+    ylab('还款占比')+    ggtitle('兴业客户还款占比情况')+    scale_x_continuous(breaks=range(1,13))

ggplot(aes(x='month', y='zhanbi', colour='year'), data=guangfahkzhb) +   geom_point()+    geom_line()+    xlab('月份')+    ylab('还款占比')+    ggtitle('广发客户还款占比情况')+    scale_x_continuous(breaks=range(1,13))

plt.figure(1)
plt.figure(2) 
plt1=plt.subplot(221)
plt2=plt.subplot(222)
plt.figure(1) 
ax2 = sns.barplot(x="age1", y="nnn", hue="kehu", data=agedata)
ax2.set_xlabel('年龄段',fontsize=15)
ax2.set_ylabel('数量',fontsize=15)
ax2.set_title('年龄段回款分析',fontsize=15)
plt.sca(plt1)  
explode = [0, 0.1, 0, 0] 
xingyeagedata = agedata[agedata.kehu=='兴业']

plt.pie(x=xingyeagedata['nnn'], labels=xingyeagedata['age1'],  explode=explode, autopct='%3.1f %%',        shadow=True, labeldistance=1.1,   startangle = 90,pctdistance = 0.6)

plt.title('兴业客户年龄段回款情况')

plt.sca(plt2)  
explode = [0, 0.1, 0, 0] 
guangfaagedata = agedata[agedata.kehu=='广发']

plt.title('广发客户年龄段回款情况')
plt.pie(x=guangfaagedata['nnn'], labels=guangfaagedata['age1'], explode=explode,  autopct='%3.1f %%',        shadow=True,  labeldistance=1.1,  startangle = 90,pctdistance = 0.6)

plt.show()

#地区图
region1 = xydzddata1['hkmx'].groupby([xydzddata1['kehu'], xydzddata1['year'], xydzddata1['province']]).sum().reset_index()

regiondata = pd.merge(region1,region,how='left',on=['kehu','year','province'])

regiondata['newprovince'] = '地区'

regiondata['province'] = regiondata['province'].astype(str)
regiondata['newprovince'] = regiondata['newprovince'].astype(str)

regiondata['newprovince'][(regiondata.province == '北京') | (regiondata.province == '天津') | (regiondata.province == '河北') | (regiondata.province == '山西')                   | (regiondata.province == '内蒙古' )] = '华北'

regiondata['newprovince'][(regiondata.province == '辽宁' )|( regiondata.province == '吉林') | (regiondata.province == '黑龙江') ] = '东北'

regiondata['newprovince'][(regiondata.province == '上海' )| (regiondata.province == '江苏') |( regiondata.province == '浙江') | (regiondata.province == '安徽')                   | (regiondata.province == '福建' )| (regiondata.province == '江西' )| (regiondata.province == '山东' )] = '华东'

regiondata['newprovince'][(regiondata.province == '河南') |( regiondata.province == '湖北') | (regiondata.province == '湖南') ] = '华中'

regiondata['newprovince'][(regiondata.province == '重庆') | (regiondata.province == '四川') | (regiondata.province == '贵州' )|( regiondata.province == '云南')                   | (regiondata.province == '西藏') ] = '西南'

regiondata['newprovince'][(regiondata.province == '陕西') | (regiondata.province == '甘肃') | (regiondata.province == '青海' )|( regiondata.province == '宁夏')                   | (regiondata.province == '新疆') ] = '西北'

regiondata['newprovince'][(regiondata.province == '广东') | (regiondata.province == '广西' )| (regiondata.province == '海南' )] = '华南'

regionplot = regiondata['hkmx'].groupby([regiondata['kehu'], regiondata['year'], regiondata['newprovince']]).sum().reset_index()

regionplot['year'] = regionplot['year'].astype(str)

plt.figure(1)
plt.figure(2) 
plt.figure(1) 
ax3 = sns.barplot(x="newprovince", y="hkmx", hue="kehu", data=regionplot[regionplot.year=='2016'])
ax3.set_xlabel('地区',fontsize=15)
ax3.set_ylabel('还款金额',fontsize=15)
ax3.set_title('2016地区回款分析',fontsize=15)
plt.figure(2)
ax4 = sns.barplot(x="newprovince", y="hkmx", hue="kehu", data=regionplot[regionplot.year=='2017'])
ax4.set_xlabel('地区',fontsize=15)
ax4.set_ylabel('还款金额',fontsize=15)
ax4.set_title('2017地区回款分析',fontsize=15)
plt.show()

