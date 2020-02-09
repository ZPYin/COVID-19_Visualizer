import os
import requests
import json
from logger import logger
from virusDB import virusDB

API_URI = 'https://lab.isaaclin.cn/nCoV/api/'
PROJECTDIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

dbFile = os.path.join(PROJECTDIR, 'db', '2019_nCov_data.db')
db = virusDB(dbFile)
db.db_connect()


def download_overall_data(maxNReq=3):
    """
    download the statistics for China.

    Parameters
    ----------
    maxNReq: int
        maximumn request number. (default: 3)
    """

    reqCount = 0
    isSuccess = False

    # access the overall data
    while reqCount <= maxNReq and (not isSuccess):
        try:
            reqCount = reqCount + 1
            logger.info('Start to download the overall data.')
            OverallRes = requests.get(
                '{0}/overall'.format(API_URI),
                params={'latest': '0'},
                timeout=10)

            isSuccess = True
        except Exception as e:
            if reqCount <= maxNReq:
                logger.warn('Failed in {0} try.'.format(reqCount))
            else:
                logger.warn('Failed in {0} tries, exit!'.format(maxNReq))
                OverallRes.raise_for_status()

    OverallData = json.loads(OverallRes.text, encoding='utf-8')
    logger.info('{0:5d} OVERALL records were retrieved.'.format(
        len(OverallData['results']))
        )

    # save the overall data to the database
    logger.info('Start to save the overall data to the database.')
    db.db_create_overall_table()
    for record in OverallData['results']:
        entry = {
            'confirmedCount': record['confirmedCount'],
            'suspectedCount': record['suspectedCount'],
            'curedCount': record['curedCount'],
            'deadCount': record['deadCount'],
            'time': record['updateTime']
        }

        db.db_insert_overall_entry(entry)
    logger.info('Finish successfully!')

    return OverallData


def download_all_regionNames(maxNReq=3):
    """
    download the list of the supported area.

    Parameters
    ----------
    maxNReq: int
        maximumn request number. (default: 3)
    """

    reqCount = 0
    isSuccess = False

    # retrieve names
    while reqCount <= maxNReq and (not isSuccess):
        try:
            reqCount = reqCount + 1
            logger.info('Start to download the region names.')
            regionNamesRes = requests.get('{0}/provinceName'.format(API_URI),
                                          timeout=10)

            isSuccess = True
        except Exception as e:
            if reqCount <= maxNReq:
                logger.warn('Failed in {0} try.'.format(reqCount))
            else:
                logger.warn('Failed in {0} tries, exit!'.format(maxNReq))
                regionNamesRes.raise_for_status()

    regionNames = json.loads(regionNamesRes.text, encoding='utf-8')
    logger.info('{0:5d} region names were retrieved.'.format(
        len(regionNames['results'])))
    # save the region names to the database
    logger.info('Start to save the region names to the database.')
    db.db_create_regionname_table()
    for regionname in regionNames['results']:
        entry = {'name': regionname}

        db.db_insert_regionname_entry(entry)

    logger.info('Finish successfully!')

    return regionNames


def download_all_regional_data():
    """
    download the statistics for all regions and the respective cities inside.
    """

    regionNames = db.db_fetch_regionnames()

    for regionName in regionNames.keys():
        download_regional_data(regionName)


def download_regional_data(province='湖北省', maxNReq=3):
    """
    download the statistics for a give province/area.

    Parameters
    ----------
    province: str
        province name. e.g., '湖北省
    maxNReq: int
        maximumn request number. (defaults: 3)

    Returns
    -------
    regionalData: dict
        region data.
    """

    reqCount = 0
    isSuccess = False

    # access the regional data
    while reqCount <= maxNReq and (not isSuccess):
        try:
            reqCount = reqCount + 1
            logger.info(
                'Start to download the region data for {0}.'.format(province))
            regionalRes = requests.get('{0}/area'.format(API_URI),
                                       params={
                                                'latest': '0',
                                                'province': province},
                                       timeout=15)
            isSuccess = True
        except Exception as e:
            if reqCount <= maxNReq:
                logger.warn('Failed in {0} try.'.format(reqCount))
            else:
                logger.warn('Failed in {0} tries, exit!'.format(maxNReq))
                regionalRes.raise_for_status()

    regionalData = json.loads(regionalRes.text, encoding='utf-8')
    logger.info('{0:5d} REGIONAL records were retrieved.'.format(
        len(regionalData['results'])
    ))

    regionnames = db.db_fetch_regionnames()
    db.db_create_regiondata_table()
    db.db_create_citydata_table()

    # save the regional data to the database
    for record in regionalData['results']:
        region_id = regionnames[province]
        entry = {
            'provinceName': province,
            'provinceShortName': record['provinceShortName'],
            'confirmedCount': record['confirmedCount'],
            'suspectedCount': record['suspectedCount'],
            'curedCount': record['curedCount'],
            'deadCount': record['deadCount'],
            'country': record['country'],
            'updateTime': record['updateTime'],
            'region_id': region_id
        }

        db.db_insert_regiondata_entry(entry)

        if 'cities' in record.keys():

            for cityRecord in record['cities']:
                cityEntry = {
                    'updateTime': record['updateTime'],
                    'cityName': cityRecord['cityName'],
                    'confirmedCount': cityRecord['confirmedCount'],
                    'suspectedCount': cityRecord['suspectedCount'],
                    'curedCount': cityRecord['curedCount'],
                    'deadCount': cityRecord['deadCount'],
                    'country': record['country'],
                    'region_id': cityRecord['confirmedCount'],
                    'confirmedCount': cityRecord['confirmedCount'],
                    'region_id': region_id
                }

                db.db_insert_citydata_entry(cityEntry)

    logger.info('Finish successfully!')

    return regionalData


def main():
    download_all_regionNames()
    download_overall_data()
    download_all_regional_data()


if __name__ == "__main__":
    main()
