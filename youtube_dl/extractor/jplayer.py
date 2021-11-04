# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import unsmuggle_url


class GenericJPlayerIE(InfoExtractor):
    _WORKING = False
    _VALID_URL = r'.*'
    _TESTS = [{
        'url': 'https://www.radiomeuh.com/player/v1212/index.html',
        'md5': 'fa8899fa601eb7c83a64e9d568bdf325',
        'info_dict': {
            'id': 'nPripu9l',
            'ext': 'mp3',
            'title': 'Radio Meuh',
        }
    }]

    @staticmethod
    def _extract_url(webpage):
        urls = GenericJPlayerIE._extract_urls(webpage)
        return urls[0] if urls else None

    @staticmethod
    def _extract_urls(webpage):
        #locate jplayer script
        f=re.findall(r'<script .*src=.*jplayer.*.js',webpage);
        if len(f)==0:
          #no jplayer script found
          return;

        f=re.findall(r'{[\s|.]*title:\s*"(?P<TITLE>[^"]*)",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*',webpage);
        # {
        #     title: "ABC Jazz",
        #     mp3: "http://listen.radionomy.com/abc-jazz"
        # }
        if len(f) == 0:
            # no jplayer script found
            return;
        return re.findall(r'{[\s|.]*title:\s*"[^"]*",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*',webpage);

    def _real_extract(self, url):
        # webpage=self._download_webpage(url,url);
        #
        # f=re.findall(r'{[\s|.]*title:\s*"(?P<TITLE>[^"]*)",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*',webpage);

        formats=[];

        formats.append({
            'url': url,
            'vcodec': 'none',
            'ext': 'mp3',
            'is_live': True,#most are radios
        })
        # if len(f[0][0])==0:
        #     video_id=url
        # else:
        #     video_id=f[0][0];

        self._sort_formats(formats)

        return {
            'id':url,
            'title': url,
            'formats': formats,
        }
