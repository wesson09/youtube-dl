# coding: utf-8
from __future__ import unicode_literals

import time
import http.client
import json
import re
from typing import *
from urllib import parse
from ssl import SSLSocket

from .common import InfoExtractor
from .turner import TurnerBaseIE
from ..utils import (
    determine_ext,
    float_or_none,
    int_or_none,
    mimetype2ext,
    parse_age_limit,
    parse_iso8601,
    strip_or_none,
    try_get,
)

import socket
import ssl

class GogomoviesIE(InfoExtractor):#TurnerBaseIE):
    _VALID_URL = r'https?://(?:www\.)?voircartoon\.com(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'https://voircartoon.com/episode/paw-patrol-la-patpatrouille-saison-7-vf-episode-25/',
        'info_dict': {
            'id': 'rQxZvXQ4ROaSOqq-or2Mow',
            'ext': 'mp4',
            'title': 'Rick and Morty - Pilot',
            'description': 'Rick moves in with his daughter\'s family and establishes himself as a bad influence on his grandson, Morty.',
            'timestamp': 1543294800,
            'upload_date': '20181127',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Unable to download f4m manifest'],
    }, {
        'url': 'http://www.adultswim.com/videos/tim-and-eric-awesome-show-great-job/dr-steve-brule-for-your-wine/',
        'info_dict': {
            'id': 'sY3cMUR_TbuE4YmdjzbIcQ',
            'ext': 'mp4',
            'title': 'Tim and Eric Awesome Show Great Job! - Dr. Steve Brule, For Your Wine',
            'description': 'Dr. Brule reports live from Wine Country with a special report on wines.  \nWatch Tim and Eric Awesome Show Great Job! episode #20, "Embarrassed" on Adult Swim.',
            'upload_date': '20080124',
            'timestamp': 1201150800,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': '404 Not Found',
    }, {
        'url': 'http://www.adultswim.com/videos/decker/inside-decker-a-new-hero/',
        'info_dict': {
            'id': 'I0LQFQkaSUaFp8PnAWHhoQ',
            'ext': 'mp4',
            'title': 'Decker - Inside Decker: A New Hero',
            'description': 'The guys recap the conclusion of the season. They announce a new hero, take a peek into the Victorville Film Archive and welcome back the talented James Dean.',
            'timestamp': 1469480460,
            'upload_date': '20160725',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Unable to download f4m manifest'],
    }, {
        'url': 'http://www.adultswim.com/videos/attack-on-titan',
        'info_dict': {
            'id': 'attack-on-titan',
            'title': 'Attack on Titan',
            'description': 'md5:41caa9416906d90711e31dc00cb7db7e',
        },
        'playlist_mincount': 12,
    }, {
        'url': 'http://www.adultswim.com/videos/streams/williams-stream',
        'info_dict': {
            'id': 'd8DEBj7QRfetLsRgFnGEyg',
            'ext': 'mp4',
            'title': r're:^Williams Stream \d{4}-\d{2}-\d{2} \d{2}:\d{2}$',
            'description': 'original programming',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': '404 Not Found',
    }]


    def _real_extract(self, url):
        show_path = re.match(self._VALID_URL, url).groups()[2]
        #print(show_path);



        webpage=self._download_webpage(url,show_path);
        #print(webpage);
        propvalpattern = '<\s*meta\s+property\s*=\s*\"og:(?P<prop>[\w^\"]+)\"\s+content\s*=\s*\"(?P<value>[\w\W]|[^\"]*)\"\s*\/\s*>'
        matches = re.finditer(
            propvalpattern,
            webpage)
        ogtitle = '';
        ogdescription = '';
        ogdate='';
        oglocale='';
        for m in matches:
            if m.group(1) == 'title':
                ogtitle = m.group(2);
            elif m.group(1) == 'description':
                ogdescription = m.group(2);
            elif m.group(1) == 'updated_time':
                ogdate = m.group(2);
            elif m.group(1) == 'locale':
                oglocale = m.group(2);

        #data-id = '19960'
        video_urls = re.findall(
            r'data\-id\=[\"\'](?P<id>[^\"]|.+?)[\"\']', webpage)
        if not video_urls: exit;
        filmId=video_urls[0];
        #print(filmId)

        videoidurl = self._download_webpage('https://voircartoon.com/ajax-get-link-stream/?server=fembeds&filmId=%s' %  filmId,show_path);
        #print(videoidurl)
        videoid=re.findall(r'[^?]+\?id\=(?P<id>.*)',videoidurl)[0];
        #print(videoid);


        #dummy download m3u8 to prevent 403 during _extract_m3u8_formats
        dummym3u8 = self._download_webpage('https://lb.gogomovies.to/hls/%s/%s' %  (videoid, videoid),videoid);


        formats = self._extract_m3u8_formats(
            'https://lb.gogomovies.to/hls/%s/%s' %  (videoid, videoid),
            videoid, 'mp4')
        self._sort_formats(formats)

        return {
            'id': videoid,
            'title': ogtitle,
            'uploader': 'TODO',
            'uploader_date': ogdate,
            'formats': formats,
            'description': ogdescription,
            #'thumbnail': '',  # livestream.get('thumbnailUrl'),
            'is_live': False,
            # 'timestamp': int_or_none(livestream.get('createdAt'), 1000),
            # 'view_count': int_or_none(livestream.get('watchingCount')),
        }


