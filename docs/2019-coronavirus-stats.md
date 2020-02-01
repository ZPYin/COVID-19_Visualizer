# 2019 Coronavirus Statistics

## Description

This project is aimed to guide myself through the whole process of how to create a standard project to demonstrate something useful for others.

## Project structure

`data_downloader`

1. download the data through the [API](#1) provided by someone anonymous. Here, I'm appreciated for the efforts that the anonymous author made to share the data.
2. save the data records to SQLite3 database, which is stored under the folder of `db`.

![database](./../img/database_structure.png)

`data_visualizer`

1. display some statistics in a intuitive manner.

<center>
<img src='../img/lineplot_overall.png', width=550, height=350, lat='overall_plot'>
<br>
Time series of 2019-nCov patients in China
</center>

<center>
<img src='../img/overall_distribution.png', width=550, height=300, lat='overall_distribution'>
<br>
Provincial distribution of 2019-nCov patients in China
</center>

<center>
<img src='../img/hubei_distribution.png', width=550, height=300, lat='hubei_distribution'>
<br>
Distribution of 2019-nCov patients in Hubei Province
</center>

## Contact

- Zhenping Yin <zp.yin@whu.edu.cn>

[1]: https://lab.isaaclin.cn/nCoV/