from data_downloader import download_all_regionNames
from data_downloader import download_overall_data
from data_downloader import download_all_regional_data
from data_visualizer import display_recent_overall
from data_visualizer import display_recent_overall_distribution
from data_visualizer import display_recent_provincial_distribution

import os
import sys

# add search path of phantomjs
projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# download data
download_all_regionNames()
download_overall_data()
download_all_regional_data()

# display
province = u'湖北省'
pic_file_1 = os.path.join(projectDir, 'img', 'lineplot_overall.png')
pic_file_2 = os.path.join(projectDir, 'img', 'overall_distribution.png')
pic_file_3 = os.path.join(projectDir, 'img', 'hubei_distribution.png')

display_recent_overall(pic_file_1)
display_recent_overall_distribution(pic_file_2, maxCount=1000)
display_recent_provincial_distribution(province, pic_file_3, maxCount=1000)
