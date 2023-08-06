# -*- coding:utf-8 -*-
'''
@Project  : lb_toolkits
@File     : spiderdownload.py
@Modify Time      @Author    @Version    
--------------    -------    --------    
2022/7/14 10:28      Lee       1.0         
@Description
------------------------------------
 
'''
import os
import sys
import numpy as np
import re
import requests
from tqdm import tqdm


class spiderdownload(object):

    def __init__(self, username=None, password=None):

        self.session = requests.Session()
        if username is not None and password is not None :
            self.login(username, password)


    def logged_in(self):
        """Check if the log-in has been successfull based on session cookies."""
        eros_sso = self.session.cookies.get("EROS_SSO_production_secure")
        return bool(eros_sso)

    def login(self, username, password, url_login):
        """Login to URL."""
        rsp = self.session.get(url_login)
        csrf = self._get_tokens(rsp.text)
        payload = {
            "username": username,
            "password": password,
            "csrf": csrf,
        }
        rsp = self.session.post(url_login, data=payload, allow_redirects=True)

        if not self.logged_in():
            raise Exception("login failed.")

    def logout(self, url_logout):
        """Log out from URL."""
        self.session.get(url_logout)

    def _get_tokens(self, body):
        """Get `csrf_token` and `__ncforminfo`."""
        csrf = re.findall(r'name="csrf" value="(.+?)"', body)[0]
        # ncform = re.findall(r'name="__ncforminfo" value="(.+?)"', body)[0]

        if not csrf:
            raise Exception("EE: login failed (csrf token not found).")
        # if not ncform:
        #     raise EarthExplorerError("EE: login failed (ncforminfo not found).")

        return csrf
        return csrf, ncform

    def download(self, output_dir, url, timeout=5*60, skip=False):
        """Download a Landsat scene.

        Parameters
        ----------
        identifier : str
            Scene Entity ID or Display ID.
        output_dir : str
            Output directory. Automatically created if it does not exist.
        dataset : str, optional
            Dataset name. If not provided, automatically guessed from scene id.
        timeout : int, optional
            Connection timeout in seconds.
        skip : bool, optional
            Skip download, only returns the remote filename.

        Returns
        -------
        filename : str
            Path to downloaded file.
        """
        os.makedirs(output_dir, exist_ok=True)
        # if not dataset:
        #     dataset = guess_dataset(identifier)
        # if is_display_id(identifier):
        #     entity_id = self.api.get_entity_id(identifier, dataset)
        # else:
        #     entity_id = identifier
        # url = EE_DOWNLOAD_URL.format(
        #     data_product_id=DATA_PRODUCTS[dataset], entity_id=entity_id
        # )
        filename = self._download(output_dir, url, timeout=timeout, skip=skip)

        return filename

    def _download(self, output_dir, url, timeout, chunk_size=1024, skip=False):
        """Download remote file given its URL."""
        # Check availability of the requested product
        # EarthExplorer should respond with JSON

        # from clint.textui import progress
        # r = requests.get(url, stream=True)
        # with open('test', 'wb') as fp :
        #     total_length = int(r.headers.get('content-length'))
        #     for ch in progress.bar(r.iter_content(chunk_size=1024,), expected_size=(total_length/1024) + 1) :
        #         if ch : fp.write(ch)
        # exit()
        # with self.session.get(
        #         url, allow_redirects=False, stream=True, timeout=timeout
        # ) as r:
        #     r.raise_for_status()
        #     error_msg = r.json().get("errorMessage")
        #     if error_msg:
        #         raise Exception(error_msg)
        #     download_url = r.json().get("url")

        download_url = url
        try:
            with self.session.get(
                    download_url, stream=True, allow_redirects=True, timeout=timeout
            ) as r:
                headers = r.headers

                file_size = int(r.headers.get("Content-Length"))
                with tqdm(
                        total=file_size, unit_scale=True, unit="B", unit_divisor=1024
                ) as pbar:
                    # local_filename = r.headers["Content-Disposition"].split("=")[-1]
                    # local_filename = local_filename.replace('"', "")
                    local_filename = os.path.basename(download_url)
                    local_filename = os.path.join(output_dir, local_filename)
                    if skip:
                        return local_filename
                    with open(local_filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(chunk_size)
        except requests.exceptions.Timeout:
            raise Exception(
                "Connection timeout after {} seconds.".format(timeout)
            )
        print('download 【%s】 success...' %(local_filename))

        return local_filename


if __name__ == '__main__':

    # url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20220729/00/atmos/gfs.t00z.goessimpgrb2.0p25.f000'
    #
    # down = spiderdownload()
    # down.download('./', url=url, )

    url = 'https://oco2.gesdisc.eosdis.nasa.gov/data/OCO2_DATA/OCO2_L2_Standard.10r/2015/094/oco2_L2StdGL_04019a_150404_B10004r_191205021747.h5'
    down = spiderdownload(username='cuitao', password='CUItao1234')
    down.download(output_dir='./', url=url)

