

lb_toolkits
===========

.. code:: angular2html

   pip install lb_toolkits
   pip install --upgrade lb_toolkits

--------------

downloadcentre
--------------

| 支持各类数据下载，例如: ERA5、GFS、LandSat、Sentinel
| *downloadERA5:*
| - **download_era5_profile:**
下载ERA5的大气分层数据

.. code:: angular2html

   download_era5_profile(strdate,outname, prof_info, area_info=None,m_client=None, redownload=False)

-  **download_era5_surface:** 下载ERA5的地表数据

.. code:: angular2html

   download_era5_surface(strdate, outname, surf_info, area_info=None, m_client=None, redownload=False)

+----------------------------------------------------------------------+
| *downloadGFS:*                                                       |
+----------------------------------------------------------------------+
| - **downloadGFS:** 下载GFS的预报数据                                |
+----------------------------------------------------------------------+
| \```angular2html                                                     |
+----------------------------------------------------------------------+
| downloadGFS(outdir, nowdate, issuetime=0, forecasttime=[0],          |
| regoin=[0.0, 360.0, 90.0, -90.0])                                    |
+----------------------------------------------------------------------+
| \``\`                                                                |
+----------------------------------------------------------------------+

*downloadLandsat:* - **searchlandsat:**
通过设置查找条件，匹配满足条件的数据ID

.. code:: angular2html

   searchlandsat(username, password, product, lat, lon, start_date, end_date, cloud_max)

-  **downloadlandsat:** 根据返回的数据ID，下载相应的文件

.. code:: angular2html

   downloadlandsat(username,password,Landsat_name, output_dir, scene_id=None)

--------------

*downloadSentinel:* - **downloadSentinel:**
下载哨兵数据，支持下载Sentinel-1、Sentinel-2、Sentinel-3、Sentinel-5P

.. code:: angular2html

   downloadSentinel(username, password, starttime, endtime, outpath='./',
   platformname='Sentinel-2', producttype='S2MSI2A',
   footprint=None, geojson = None, filename='*', **keywords)



tools
-----

1、对hdf4、hdf5、netcdf4、tiff, json, grib1/2、ASCII文件操作
2、通过ftp、sftp、wget、爬虫下载相关文件

*hdfpro:* - **readhdf:** 读取hdf5文件,
返回数据（也可返回数据集属性信息）

.. code:: angular2html

   readhdf(filename, sdsname, dictsdsinfo=None)

-  **readhdf_fileinfo:** 读取hdf5文件全局属性, 返回文件全局属性信息

.. code:: angular2html

   readhdf_fileinfo(filename)

-  **writehdf:** 写入hdf5文件

.. code:: angular2html

   writehdf(filename, sdsname, data, overwrite=True,
           dictsdsinfo = None, dictfileinfo = None,
           compression = 9, info = False)

-  **writehdf_fileinfo:** 写入hdf5文件

.. code:: angular2html

   writehdf_fileinfo(filename, sdsname, data, overwrite=True,
           dictsdsinfo = None, dictfileinfo = None,
           compression = 9, info = False)

--------------

| *hdf4pro:*
| - **readhdf4:** 读取hdf4文件, 返回数据（也可返回数据集属性信息）

.. code:: angular2html

   readhdf4(h4file, sdsname, dictsdsattrs=None, dictfileattrs=None)

-  **readhdf4sdsattrs:** 读取hdf4文件数据集属性信息

.. code:: angular2html

   readhdf4sdsattrs(h4file, sdsname)

-  **readhdf4fileattrs:** 读取hdf4文件全局属性信息

.. code:: angular2html

   readhdf4fileattrs(h4file)

--------------

*ncpro:* - **readnc:** 读取netcdf4文件,
返回数据（也可返回数据集属性信息）

.. code:: angular2html

   readnc(filename, sdsname, dictsdsinfo=None)

-  **readnc_fileinfo:** 读取netcdf4文件全局属性信息

.. code:: angular2html

   readnc_fileinfo(filename)

-  **readnc_sdsinfo:** 读取netcdf4文件数据集属性信息

.. code:: angular2html

   readnc_sdsinfo(filename, sdsname)

-  **writenc:** 写入netcdf4文件数据集

.. code:: angular2html

   writenc(filename, sdsname, srcdata, dimension=None, overwrite=1,
           complevel=9, dictsdsinfo=None, fill_value=None,
           standard_name=None, long_name=None, description=None, units=None,
           valid_range=None,
           scale_factor=None, add_offset=None, **kwargs)

-  **writenc_fileinfo:** 写入netcdf4文件全局属性

.. code:: angular2html

   writenc_fileinfo(filename, dictfileinfo, overwrite=1)

-  **writenc_sdsinfo:** 写入netcdf4文件数据集属性

.. code:: angular2html

   writenc_sdsinfo(filename, sdsname, dictsdsinfo, overwrite=1)

-  **writencfortimes:** 写入netcdf4文件\ **时间戳**\ 数据集

.. code:: angular2html

   writencfortimes(filename, sdsname, srcdata, overwrite=1,
                   units = 'hours since 1900-01-01 00:00:00.0',
                   calendar = "gregorian",
                   complevel=9, dictsdsinfo=None)

--------------

*jsonpro:* - **readjson:** 读取json文件, 返回dict

.. code:: angular2html

   readjson(jsonname, **kwargs)

-  **writejson:** 写入json文件

.. code:: angular2html

   writejson(jsonname, dict_info, indent=4, chinese=False)

-  **readbinary:** 读取二进制文件

.. code:: angular2html

   readbinary(filename, shape, dtype=np.float32, offset=0, encodine='utf-8')

-  **writebinary:** 写入二进制文件

.. code:: angular2html

   writebinary(filename, data, overwrite=1, offset=0, encodine='utf-8')

-  **readascii:** 读取ASCII文件

.. code:: angular2html

   readascii(filename, dtype=float, comments='#', delimiter=None,
               converters=None, skiprows=0, usecols=None, unpack=False,
               ndmin=0, encoding='bytes', max_rows=None)

-  **writeascii:** 写入ASCII文件

.. code:: angular2html

   writeascii(filename, data,  fmt='%.18e', delimiter=' ', newline='\n', header='',
               footer='', comments='# ', encoding=None)

-  **loadarray:** 读取npy文件

.. code:: angular2html

   loadarray(file, mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')

-  **savearray:** 写入npy文件

.. code:: angular2html

   savearray(filename, data, allow_pickle=True, fix_imports=True)

.. _section-1:

————————————————
----------------

test
----
