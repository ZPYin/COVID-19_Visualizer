from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot

from pyecharts.charts import Map
from pyecharts import options as opts

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import datetime as dt

import sqlite3 as db

import os
import sys
import csv
import re

# add search path of phantomjs
sys.path.append('/Users/yinzhenping/Downloads/phantomjs-2.1.1-macosx/bin')
projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dbFile = os.path.join(projectDir, 'db', '2019_nCov_data.db')


def searchCityLongName(cityName):
    """
    search the city long name.

    Parameters
    ----------
    cityName: str
        city name. e.g., 鄂州

    examples
    --------
    > searchCityLongName('鄂州')
    > '鄂州市'
    """

    baidumap_City_table_file = os.path.join(
        projectDir, 'include', 'BaiduMap_cityCode_1102.txt')

    # load baidu map city table
    city_longname_list = []
    with open(baidumap_City_table_file, 'r', encoding='utf-8') as fh:
        tableReader = csv.reader(fh)
        for row in tableReader:
            city_longname_list.append(row[1])

    for city_longname in city_longname_list:
        if re.search('.*{0}.*'.format(cityName), city_longname):
            return city_longname

    return None


def display_recent_overall(pic_file):

    conn = db.connect(dbFile)
    cu = conn.cursor()

    cu.execute("""SELECT * FROM Overall;""")
    overallData = cu.fetchall()
    overallConfirmedCounts = []
    overallSuspectedCounts = []
    overallCuredCounts = []
    overallTime = []
    for record in overallData:
        overallTime.append(dt.datetime.utcfromtimestamp(record[1] / 1000))
        overallConfirmedCounts.append(record[2])
        overallSuspectedCounts.append(record[3])
        overallCuredCounts.append(record[4])

    plt.rcParams['font.family'] = ['Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax1 = plt.subplots(figsize=(8, 5))

    s1 = ax1.scatter(overallTime, overallConfirmedCounts, 3, color='r')
    s2 = ax1.scatter(overallTime, overallSuspectedCounts, 3, color='k')
    ax1.set_ylabel(u'人数')
    ax2 = ax1.twinx()
    s3 = ax2.scatter(overallTime, overallCuredCounts, 3, color='g')
    ax2.set_ylabel(u'人数')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xlim([dt.datetime(2020, 1, 23), dt.datetime(2020, 2, 1)])
    plt.legend((s1, s2, s3), (u'确证人数', u'疑似人数', u'治愈人数'))

    plt.savefig(pic_file)


def display_recent_overall_distribution(pic_file):

    conn = db.connect(dbFile)
    cu = conn.cursor()
    cu.execute(
        """select provinceShortName, confirmedCount
        from Region_Data where updateTime in
        (select max(rd.updateTime)
        from Region_Data rd where rd.country = '中国' group by rd.region_id);
        """)
    recentProvinceData = cu.fetchall()

    cu.execute("""select max(updateTime) from Region_Data;""")
    recentTime = cu.fetchone()
    recentTimeObj = dt.datetime.utcfromtimestamp(int(recentTime[0]) / 1000)

    # color-plot
    list1 = [[recentProvinceData[i][0], recentProvinceData[i][1]]
             for i in range(len(recentProvinceData))]
    map_1 = Map()
    map_1.set_global_opts(
        title_opts=opts.TitleOpts(title="{0}全国各省感染总人数".
                                  format(recentTimeObj.strftime('%y-%m-%d'))),
        visualmap_opts=opts.VisualMapOpts(max_=500)
        )
    map_1.add("{0}全国各省感染总人数".format(recentTimeObj.strftime('%y-%m-%d')),
              list1,
              maptype="china")
    make_snapshot(
        snapshot,
        file_name=map_1.render(),
        output_name=pic_file,
        delay=2,
        pixel_ratio=2,
        is_remove_html=True)


def display_recent_provincial_distribution(province, pic_file):

    conn = db.connect(dbFile)
    cu = conn.cursor()

    cu.execute("""select max(updateTime) from Region_Data;""")
    recentTime = cu.fetchone()
    recentTimeObj = dt.datetime.utcfromtimestamp(int(recentTime[0]) / 1000)

    cu.execute(
        """select cityName, confirmedCount
        from City_Data where updateTime in
        (select max(c_d.updateTime)
        from City_Data c_d
        inner join Region_Name r_n
        where c_d.country = '中国' and r_n.name=(?) and c_d.region_id = r_n.id
        group by c_d.cityName);""", (province,))
    hubeiProvinceData = cu.fetchall()

    cu.execute("""select provinceShortName from Region_Data
                where Region_Data.provinceName = (?)
            """, (province,))
    hubeiProvinceShortName = cu.fetchone()
    hubeiProvinceShortName = hubeiProvinceShortName[0]

    list2 = [[searchCityLongName(hubeiProvinceData[i][0]),
              hubeiProvinceData[i][1]]
             for i in range(len(hubeiProvinceData))]
    map_2 = Map()
    map_2.set_global_opts(
        title_opts=opts.TitleOpts(title="{0} {1}感染人数".
                                  format(recentTimeObj.strftime('%y-%m-%d'),
                                         province)),
        visualmap_opts=opts.VisualMapOpts(max_=500)
        )
    map_2.add("{0} {1}感染人数".format(
                recentTimeObj.strftime('%y-%m-%d'),
                province),
              list2,
              maptype=hubeiProvinceShortName)
    make_snapshot(
        snapshot,
        file_name=map_2.render(),
        output_name=pic_file,
        delay=2,
        pixel_ratio=2,
        is_remove_html=True)


def main():
    province = u'湖北省'
    pic_file_1 = os.path.join(projectDir, 'img', 'lineplot_overall.png')
    pic_file_2 = os.path.join(projectDir, 'img', 'overall_distribution.png')
    pic_file_3 = os.path.join(projectDir, 'img', 'hubei_distribution.png')

    display_recent_overall(pic_file_1)
    display_recent_overall_distribution(pic_file_2)
    display_recent_provincial_distribution(province, pic_file_3)


if __name__ == "__main__":
    main()
