# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .jwplatform import JWPlatformIE

from ..utils import std_headers

class NakedIE(InfoExtractor):
    _VALID_URL = r'https:\/\/www\.naked\.com\/\?model=(?P<id>.*)'
    _TESTS = [{
        'url': 'http://www.spiegel.de/video/vulkan-tungurahua-in-ecuador-ist-wieder-aktiv-video-1259285.html',
        'md5': '50c7948883ec85a3e431a0a44b7ad1d6',
        'info_dict': {
            'id': 'II0BUyxY',
            'display_id': '1259285',
            'ext': 'mp4',
            'title': 'Vulkan Tungurahua in Ecuador ist wieder aktiv - DER SPIEGEL - Wissenschaft',
            'description': 'md5:8029d8310232196eb235d27575a8b9f4',
            'duration': 48.0,
            'upload_date': '20130311',
            'timestamp': 1362997920,
        },
    }, {
        'url': 'http://www.spiegel.de/video/schach-wm-videoanalyse-des-fuenften-spiels-video-1309159.html',
        'only_matching': True,
    }, {
        'url': 'https://www.spiegel.de/video/eifel-zoo-aufregung-um-ausgebrochene-raubtiere-video-99018031.html',
        'only_matching': True,
    }, {
        'url': 'https://www.spiegel.de/panorama/urteile-im-goldmuenzenprozess-haftstrafen-fuer-clanmitglieder-a-aae8df48-43c1-4c61-867d-23f0a2d254b7',
        'only_matching': True,
    }, {
        'url': 'http://www.spiegel.de/video/spiegel-tv-magazin-ueber-guellekrise-in-schleswig-holstein-video-99012776.html',
        'only_matching': True,
    }, {
        'url': 'http://www.spiegel.de/sport/sonst/badminton-wm-die-randsportart-soll-populaerer-werden-a-987092.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id,   headers=std_headers)
        media_id = self._html_search_regex(
            r'\'models\':\s*\[\s*(?P<MODELS>.*)\s*,\s*\],\s*\'favorites\'',
            webpage, 'media id', group='MODELS')
        models=self._parse_json('['+media_id+']',video_id);
        for mod in models:
            if mod['model_seo_name']==video_id:
                model=mod
                break;

        formats=[]
        if model:
            media_id=model['model_id']

            streams=self._download_json('https://www.naked.com/ws/chat/get-stream-urls.php?model_id='+media_id,video_id,
                headers=std_headers);


            for hls in streams['data']['hls']:
                #hls=streams['data']['hls'][0]
                dlive, m3u8_formats, subs = self._extract_m3u8_live_and_formats( 'https:'+hls['url'], video_id, 'mp4',  m3u8_id=hls['name'], fatal=False)
                formats.extend(m3u8_formats)
        return {
            'id': video_id,
            'display_id': video_id,
            'title': video_id,
            'description': self._html_search_meta('description',webpage, default=None),
            'formats':formats,
            'is_live':dlive,
            'headers':std_headers
        }
