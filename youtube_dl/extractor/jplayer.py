# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
#from ..downloader.http import HttpFD

from .. import downloader
from ..utils import unsmuggle_url
import requests
import json

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
        #locate jplayer script
        # f=re.findall(r'<script .*src=.*jplayer.*.js',webpage);
        # if len(f)==0:
        #   #no jplayer script found
        #   return;
        #
        # f=re.findall(r'{[\s|.]*title:\s*"(?P<TITLE>[^"]*)",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*',webpage);
        # # {
        # #     title: "ABC Jazz",
        # #     mp3: "http://listen.radionomy.com/abc-jazz"
        # # }
        # if len(f) == 0:
        #     # no jplayer script found
        #     return;
        # return re.findall(r'{[\s|.]*title:\s*"[^"]*",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*',webpage);

        urls = GenericJPlayerIE._extract_urls(webpage)
        return urls[0] if urls else None

    @staticmethod
    def _extract_urls(webpage,webpageurl):
        #locate jplayer script
        f = re.findall(r'<script .*src=.*jplayer.*.js', webpage);
        if len(f) == 0:
            # no jplayer script found
            return None;

        f = re.findall(r'{[\s|.]*title:\s*"(?P<TITLE>[^"]*)",[\s|.]*mp3:\s*"(?P<MP3>[^"]*)"[\s|.]*', webpage);
        # {
        #     title: "ABC Jazz",
        #     mp3: "http://listen.radionomy.com/abc-jazz"
        # }
        if len(f) == 0:
            # no jplayer script found
            return None;

            #   get /player/rtdata/tracks.json to retrieve current title...or not....

        URL_RE = re.compile('(?P<domain>https?://[^/]+)/')
        m = URL_RE.match(webpageurl)

        dom = m.group('domain')

        ie =GenericJPlayerIE()
        ie.set_downloader(HttpFD())
        resjs=ie._download_json(dom + '/player/rtdata/tracks.json',f[0][1],fatal=False,note=None);
        title = ''
        try:
            #resjs = json.loads(res.content);
            title = resjs[0]['artist']+'-'+resjs[0]['titre']
        except:
            title = f[0][0]

        formats = [];

        formats.append({
            'url': f[0][1],
            'vcodec': 'none',
            'ext': 'mp3',
            'is_live': True,  # most are radios
        })
        # if len(f[0][0])==0:
        #     video_id=url
        # else:
        #     video_id=f[0][0];

        #_sort_formats(formats)

        return {
            'id': f[0][0],
            'title': title,
            'formats': formats,
            'url':webpageurl,
        }


#def _real_extract(self, webpage):

