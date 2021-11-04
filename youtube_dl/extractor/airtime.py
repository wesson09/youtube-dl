# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import unsmuggle_url


class GenericAirtimeIE(InfoExtractor):
    _WORKING = False
    _VALID_URL = r'.*'
    _TESTS = [{
        'url': 'https://deltacast.hd.free.fr/embed/player?stream=auto&title=Now%20playing',
        'md5': 'fa8899fa601eb7c83a64e9d568bdf325',
        'info_dict': {
            'id': 'nPripu9l',
            'ext': 'mp3',
            'title': 'Deltacast Radio',
        }
    }]

    @staticmethod
    def _extract_url(webpage):
        urls = GenericAirtimeIE._extract_urls(webpage)
        return urls[0] if urls else None

    @staticmethod
    def _extract_urls(webpage):
        #locate jplayer script
        f=re.findall(r'<script .*src=.*airtime.*.js',webpage);
        if len(f)==0:
          #no jplayer script found
          return;

        f=re.findall(r'availableDesktopStreamQueue[\s|.]*=[\s|.]*\[{"url":"(?P<URL>[^"]*)","codec":"(?P<CODEC>[^"]*)","bitrate":(?P<bitrate>[^,]*)',webpage);

        if len(f) == 0:
            # no jplayer script found
            return;
        return [f[0][0].replace('\\','')];

    def _real_extract(self, url):
        # webpage=self._download_webpage(url,url);
        # f = re.findall(
        #     r'availableDesktopStreamQueue[\s|.]*=[\s|.]*\[{"url":"(?P<URL>[^"]*)","codec":"(?P<CODEC>[^"]*)","bitrate":(?P<bitrate>[^,]*)',
        #     webpage);

        #TODO get /api/live-info to retrieve current title...or not....

        formats=[];

        formats.append({
            'url': url,
            #'vcodec':  f[0][1],
            'ext': 'mp3',
            'is_live': True,#most are radios
        })
        # if len(f[0][0])==0:
        #     video_id=url
        # else:
        #     video_id=f[0][0];

        self._sort_formats(formats)

        return {
            'id': url,
            'title': 'LibreTime Radio',
            'formats': formats,
        }
