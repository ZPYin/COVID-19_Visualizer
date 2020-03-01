from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot

from pyecharts.charts import Map
from pyecharts import options as opts

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import pandas as pd
import datetime as dt

import sqlite3 as db

import os
import sys
import csv
import re
import shutil

plt.switch_backend('Agg')

# add search path of phantomjs
projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dbFile = os.path.join(projectDir, 'db', '2019_nCov_data.db')

# from Chinese to English to support pyecharts
COUNTRY_DICT = {
    '尼日利亚': 'Nigeria',
    '新西兰': 'New Zealand',
    '立陶宛': 'Lithuania',
    '菲律宾': 'Philippines',
    '西班牙': 'Spain',
    '越南': 'Vietnan',
    '阿联酋': 'United Arab Emirates',
    '韩国': 'Korea',
    '马来西亚': 'Malaysia',
    '埃及': 'Egypt',
    '伊朗': 'Iran',
    '以色列': 'Israel',
    '黎巴嫩': 'Lebanon',
    '伊拉克': 'Iraq',
    '巴林': 'Bahrain',
    '科威特': 'Kuwait',
    '阿富汗': 'Afghanistan',
    '阿曼': 'Oman',
    '克罗地亚': 'Croatia',
    '奥地利': 'Austria',
    '瑞士': 'Swiztherland',
    '阿尔及利亚': 'Algeria',
    '希腊': 'Greece',
    '巴基斯坦': 'Pakistan',
    '巴西': 'Brazil',
    '格鲁吉亚': 'Georgia',
    '罗马尼亚': 'Romania',
    '丹麦': 'Denmark',
    '挪威': 'Norway',
    # '北马其顿':
    '荷兰': 'Netherlands',
    '北爱尔兰': 'Ireland',
    '中国': 'China',
    '俄罗斯': 'Russia',
    '尼泊尔': 'Nepal',
    '日本': 'Japan',
    '加拿大': 'Canada',
    '印度': 'India',
    '德国': 'Germany',
    '意大利': 'Italy',
    '斯里兰卡': 'Sri Lanka',
    '新加坡': 'Singapore',
    '柬埔寨': 'Cambodia',
    '比利时': 'Belgium',
    '法国': 'France',
    '泰国': 'Thailand',
    '澳大利亚': 'Australia',
    '瑞典': 'Sweden',
    '美国': 'United States',
    '芬兰': 'Finland',
    '英国': 'United Kingdom'
}


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

    cityLongName = None

    # search in the additional city name table
    correction_table_file = os.path.join(
        projectDir, 'include', 'cityName_correction_table.txt')
    cityName_correction_dict = dict()
    with open(correction_table_file, 'r', encoding='utf-8') as fh:
        tableReader = csv.reader(fh)
        tableReader.__next__()
        for row in tableReader:
            cityName_correction_dict[row[0]] = row[1]

    for city_longname in cityName_correction_dict.keys():
        if re.search('{0}'.format(cityName), city_longname):
            cityLongName = cityName_correction_dict[city_longname]

    if not cityLongName:
        # search in baidu map city table
        baidumap_City_table_file = os.path.join(
            projectDir, 'include', 'BaiduMap_cityCode_1102.txt')
        city_longname_list = []
        with open(baidumap_City_table_file, 'r', encoding='utf-8') as fh:
            tableReader = csv.reader(fh)
            tableReader.__next__()
            for row in tableReader:
                city_longname_list.append(row[1])

        for city_longname in city_longname_list:
            if re.search('.*{0}.*'.format(cityName), city_longname):
                cityLongName = city_longname

    return cityLongName


def display_recent_overall(pic_file):

    conn = db.connect(dbFile)

    overallData = pd.read_sql_query("""SELECT * FROM Overall;""", conn)
    overallData['date'] = pd.to_datetime(
        overallData['time'] / 1000, unit='s')
    overallData = overallData.set_index('date')
    dailyMeanOverall = overallData.resample('D').mean().round()

    fig, ax1 = plt.subplots(figsize=(8, 5))

    s1, = ax1.plot(
        dailyMeanOverall.index,
        dailyMeanOverall['confirmedCount'],
        color='r', marker='o')
    s2, = ax1.plot(
        dailyMeanOverall.index,
        dailyMeanOverall['suspectedCount'],
        color='k', marker='o')
    ax1.set_ylabel('confirmed/suspected number')
    ax1.set_ylim([0, 80000])
    ax2 = ax1.twinx()
    s3, = ax2.plot(
        dailyMeanOverall.index,
        dailyMeanOverall['curedCount'],
        color='g', marker='o')
    s4, = ax2.plot(
        dailyMeanOverall.index,
        dailyMeanOverall['deadCount'],
        color='b', marker='o')
    ax2.set_ylabel('cured/dead number')
    ax2.set_ylim([0, 40000])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xlim(
        [dt.datetime(2020, 1, 23),
         max(dailyMeanOverall.index) + dt.timedelta(days=1)])
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=50)
    plt.legend(
        (s1, s2, s3, s4),
        ('confirmed', 'suspected', 'cured', 'dead'))
    plt.savefig(pic_file)


def display_recent_overall_distribution(pic_file, maxCount=500, **kwargs):
    """
    display the distribution of recent total numbers of nation-wide confirmed
    patients in China.

    Parameters
    ----------
    pic_file: str
        absolute path of the generated figure.
    maxCount: int
        maximumn count of colorbar. (default: 500)
    """

    conn = db.connect(dbFile)
    cu = conn.cursor()
    cu.execute(
        """select provinceShortName, confirmedCount
        from Region_Data
        where updateTime in (select max(updateTime)
        from Region_Data r_d
        where r_d.country='中国' and r_d.region_id=Region_Data.region_id)
        group by Region_Data.region_id;
        """)
    recentProvinceData = cu.fetchall()

    cu.execute("""select max(updateTime) from Region_Data;""")
    recentTime = cu.fetchone()
    recentTimeObj = dt.datetime.utcfromtimestamp(int(recentTime[0]) / 1000)

    # color-plot
    list1 = [[recentProvinceData[i][0], recentProvinceData[i][1]]
             for i in range(len(recentProvinceData))]
    map_1 = Map()
    map_1.add("{0}全国各省感染总人数".format(recentTimeObj.strftime('%y-%m-%d')),
              list1,
              maptype="china", is_map_symbol_show=False)
    map_1.set_global_opts(
        title_opts=opts.TitleOpts(title="{0}全国各省感染总人数".
                                  format(recentTimeObj.strftime('%y-%m-%d'))),
        visualmap_opts=opts.VisualMapOpts(max_=maxCount)
        )

    if 'notebook' in kwargs.keys():
        if kwargs['notebook']:
            map_1.render_notebook()
    else:
        html_file = '{0}.html'.format(os.path.splitext(pic_file)[0])
        tmpHtmlFile = map_1.render()
        shutil.move(tmpHtmlFile, html_file)
        make_snapshot(
            snapshot,
            file_name=html_file,
            output_name=pic_file,
            is_remove_html=False,
            **kwargs)


def display_recent_global_distribution(pic_file, maxCount=200, **kwargs):
    """
    display the distribution of recent total numbers of confirmed patients.

    Parameters
    ----------
    pic_file: str
        absolute path of the generated figure.
    maxCount: int
        maximumn count of colorbar. (default: 200)
    """

    conn = db.connect(dbFile)
    cu = conn.cursor()

    OverallDf = pd.read_sql_query(
        """select * from Region_Data""", conn)
    OverallDf['updateTime'] = OverallDf['updateTime'].astype('int64')

    recentData = OverallDf.groupby('provinceShortName').apply(
        lambda t: t[t['updateTime'] == t['updateTime'].max()])

    recentData = recentData.groupby('country').agg(
        {
            'confirmedCount': 'sum',
            'suspectedCount': 'sum',
            'updateTime': 'mean'
        })
    recentData['date'] = pd.to_datetime(
        recentData['updateTime']/1000, unit='s')

    time = recentData[recentData.index == '中国']['updateTime']
    data = [
        [
            COUNTRY_DICT[recentData.index[i]],
            int(recentData['confirmedCount'][i])
        ]
        for i in range(recentData.shape[0])
        if recentData.index[i] in COUNTRY_DICT.keys()]

    map_3 = Map()
    map_3.add(
        "{0} worldwide COVID-19 patients distribution".format(
            recentData['date'][1].strftime('%Y-%m-%d')),
        data,
        maptype='world', is_map_symbol_show=False)
    map_3.set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False,
            font_size=100))
    map_3.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(max_=maxCount),
        title_opts=opts.TitleOpts(title=""))

    if 'notebook' in kwargs.keys():
        if kwargs['notebook']:
            map_3.render_notebook()
    else:
        html_file = '{0}.html'.format(os.path.splitext(pic_file)[0])
        tmpHtmlFile = map_3.render()
        shutil.move(tmpHtmlFile, html_file)
        make_snapshot(
            snapshot,
            file_name=html_file,
            output_name=pic_file,
            is_remove_html=False,
            **kwargs)


def display_recent_provincial_distribution(province, pic_file, maxCount=500,
                                           **kwargs):
    """
    display the distribution of recent total numbers of confirmed patients.

    Parameters
    ----------
    province: str
        province name. e.g., '湖北省'
    pic_file: str
        absolute path of the generated figure.
    maxCount: int
        maximumn count of colorbar. (default: 500)
    """

    conn = db.connect(dbFile)
    cu = conn.cursor()

    cu.execute("""select max(updateTime) from Region_Data;""")
    recentTime = cu.fetchone()
    recentTimeObj = dt.datetime.utcfromtimestamp(int(recentTime[0]) / 1000)

    cu.execute(
        """select cityName, confirmedCount
        from City_Data
        where City_Data.region_id=
        (select id from Region_Name where Region_Name.name=(?))
        and updateTime in (select max(updateTime)
        from City_Data
        where City_Data.region_id=
        (select id from Region_Name where Region_Name.name=(?)))
        group by City_Data.cityName;""", (province, province))
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
    map_2.add("{0} {1}感染人数".format(
                recentTimeObj.strftime('%y-%m-%d'),
                province),
              list2,
              maptype=hubeiProvinceShortName,
              is_map_symbol_show=False)
    map_2.set_global_opts(
        title_opts=opts.TitleOpts(title="{0} {1}感染人数".
                                  format(recentTimeObj.strftime('%y-%m-%d'),
                                         province)),
        visualmap_opts=opts.VisualMapOpts(max_=maxCount)
        )

    if 'notebook' in kwargs.keys():
        if kwargs['notebook']:
            map_2.render_notebook()
    else:
        html_file = '{0}.html'.format(os.path.splitext(pic_file)[0])
        tmpHtmlFile = map_2.render()
        shutil.move(tmpHtmlFile, html_file)
        make_snapshot(
            snapshot,
            file_name=html_file,
            output_name=pic_file,
            is_remove_html=False,
            **kwargs)


def main():
    province = u'湖北省'
    pic_file_1 = os.path.join(projectDir, 'img', 'lineplot_overall.png')
    pic_file_2 = os.path.join(projectDir, 'img', 'overall_distribution.png')
    pic_file_3 = os.path.join(projectDir, 'img', 'hubei_distribution.png')
    pic_file_4 = os.path.join(projectDir, 'img', 'global_distribution.png')

    # display_recent_overall(pic_file_1)
    # display_recent_overall_distribution(pic_file_2, pixel_ratio=1)
    # display_recent_provincial_distribution(
    # province, pic_file_3, pixel_ratio=1)
    display_recent_global_distribution(pic_file_4, pixel_ratio=1)


if __name__ == "__main__":
    main()
