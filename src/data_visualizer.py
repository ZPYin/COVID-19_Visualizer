from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot

from pyecharts.charts import Map
from pyecharts import options as opts

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import pandas as pd
import datetime as dt
import numpy as np

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


def searchCountryENName(countryCNName):
    """
    search the country English name.

    Parameters
    ----------
    countryCNName: str
        country Chinese name. e.g., '中国' (China)

    examples
    --------
    >>> searchCountryENName('中国')
    >>> 'China'
    """

    countryENName = 'unknown'

    # search in the additional city name table
    mapping_file = os.path.join(
        projectDir, 'include', 'country_English_name_table.txt')
    country_name_dict = dict()
    with open(mapping_file, 'r', encoding='utf-8') as fh:
        tableReader = csv.reader(fh)
        tableReader.__next__()
        for row in tableReader:
            country_name_dict[row[1]] = row[0]

    for countryCN in country_name_dict.keys():
        if re.search('{0}'.format(countryCNName), countryCN):
            countryENName = country_name_dict[countryCN]

    return countryENName


def searchCountryCNName(countryENName):
    """
    search the country Chinese name.

    Parameters
    ----------
    countryENName: str
        country English name. e.g., 'China' (中国)

    examples
    --------
    >>> searchCountryENName('China')
    >>> '中国'
    """

    countryCNName = 'unknown'

    # search in the additional city name table
    mapping_file = os.path.join(
        projectDir, 'include', 'country_English_name_table.txt')
    country_name_dict = dict()
    with open(mapping_file, 'r', encoding='utf-8') as fh:
        tableReader = csv.reader(fh)
        tableReader.__next__()
        for row in tableReader:
            country_name_dict[row[0]] = row[1]

    for countryEN in country_name_dict.keys():
        if re.search('{0}'.format(countryENName), countryEN):
            countryCNName = country_name_dict[countryEN]

    return countryCNName


def searchCityLongName(cityName):
    """
    search the city long name.

    Parameters
    ----------
    cityName: str
        city name. e.g., 鄂州

    examples
    --------
    >>> searchCityLongName('鄂州')
    >>> '鄂州市'
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
    """
    Visualize the time series of COVID-19 statistics in China.
    """

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
    ax1.set_ylim([0, np.max(dailyMeanOverall['confirmedCount']) * 1.3])
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
    ax2.set_ylim([0, np.max(dailyMeanOverall['curedCount'] * 1.3)])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xlim(
        [dt.datetime(2020, 1, 23),
         max(dailyMeanOverall.index) + dt.timedelta(days=1)])
    plt.title('Time series of COVID-19 pandemic in China')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=50)
    plt.legend(
        (s1, s2, s3, s4),
        ('confirmed', 'suspected', 'cured', 'dead'))
    plt.savefig(pic_file)


def display_timeseries(pic_file, country):
    """
    Visualize the time series of COVID-19 statistics for the given country.
    """

    conn = db.connect(dbFile)

    RegionDf = pd.read_sql_query(
        """select * from Region_Data WHERE country='{0}'""".format(country),
        conn)
    RegionDf['updateTime'] = RegionDf['updateTime'].astype('int64')
    RegionDf['date'] = pd.to_datetime(
        RegionDf['updateTime'] / 1000, unit='s')
    RegionDf = RegionDf.set_index('date')
    dailyMeanRegion = RegionDf.resample('D').mean().round()
    fig, ax1 = plt.subplots(figsize=(8, 5))

    s1, = ax1.plot(
        dailyMeanRegion.index,
        dailyMeanRegion['confirmedCount'],
        color='r', marker='o')
    s2, = ax1.plot(
        dailyMeanRegion.index,
        dailyMeanRegion['suspectedCount'],
        color='k', marker='o')
    ax1.set_ylabel('confirmed/suspected number')
    ax1.set_ylim([0, np.max(dailyMeanRegion['confirmedCount']) * 1.3])
    ax2 = ax1.twinx()
    s3, = ax2.plot(
        dailyMeanRegion.index,
        dailyMeanRegion['curedCount'],
        color='g', marker='o')
    s4, = ax2.plot(
        dailyMeanRegion.index,
        dailyMeanRegion['deadCount'],
        color='b', marker='o')
    ax2.set_ylabel('cured/dead number')
    ax2.set_ylim([0, np.max(dailyMeanRegion['curedCount']) * 1.3])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xlim(
        [dt.datetime(2020, 2, 20),
            max(dailyMeanRegion.index) + dt.timedelta(days=1)])
    plt.title('Time series of the COVID-19 pandemic in {0}'.format(
        searchCountryENName(country)))
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
            searchCountryENName(recentData.index[i]),
            int(recentData['confirmedCount'][i])
        ]
        for i in range(recentData.shape[0])]

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
    pic_file_5 = os.path.join(projectDir, 'img', 'lineplot_Italy.png')

    # display_recent_overall(pic_file_1)
    # display_recent_overall_distribution(pic_file_2, pixel_ratio=1)
    # display_recent_provincial_distribution(
    # province, pic_file_3, pixel_ratio=1)
    # display_recent_global_distribution(pic_file_4, pixel_ratio=1)
    display_timeseries(pic_file_5, searchCountryCNName('Italy'))


if __name__ == "__main__":
    main()
