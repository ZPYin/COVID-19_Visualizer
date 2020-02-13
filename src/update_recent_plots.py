from data_downloader import download_all_regionNames
from data_downloader import download_overall_data
from data_downloader import download_all_regional_data
from data_visualizer import display_recent_overall
from data_visualizer import display_recent_overall_distribution
from data_visualizer import display_recent_provincial_distribution
from logger import logger

import os
import sys
import time

# add search path of phantomjs
projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# download data
download_all_regionNames()
time.sleep(3)
download_overall_data()
time.sleep(3)
download_all_regional_data(pause=10)

# display
province = u'湖北省'
pic_file_1 = os.path.join(projectDir, 'img', 'lineplot_overall.png')
pic_file_2 = os.path.join(projectDir, 'img', 'overall_distribution.png')
pic_file_3 = os.path.join(projectDir, 'img', 'hubei_distribution.png')

logger.info('Display line-plot of overall data.')
display_recent_overall(pic_file_1)

logger.info("""Display color-plot of distribution of
            confirmed patients in China""")
display_recent_overall_distribution(pic_file_2, maxCount=1000)

logger.info("""Display color-plot of distribution of
            confirmed patients in {0}""".format(province))
display_recent_provincial_distribution(province, pic_file_3, maxCount=1000)
