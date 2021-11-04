from __future__ import unicode_literals

import json
import re
import io
import base64

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
import requests


class AudacyHLSHackerIE(InfoExtractor):  # TurnerBaseIE):
    _VALID_URL = r'https?://(?:smartstreams\.)?radio\.com(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'https://smartstreams.radio.com/stream/7505/listen/71995ed8-9d83-515a-970a-273219251816/high/stream.m3u8',
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
        show_path = re.match(self._VALID_URL, url).groups()[1]
        print(show_path);
        video_id = show_path;
        webpage = self._download_webpage(url, video_id)

        buf = io.StringIO(webpage)
        line = buf.readline()
        HLSdoc = '#EXTM3U\n'
        HLSdoc += '#EXT-X-VERSION:7\n'
        HLSdoc += '#EXT-X-TARGETDURATION:10\n';

        title = ''
        artist = ''
        while len(line) > 0:
            if line.find('EXT-X-KEY') >= 0:
                HLSdoc += line;
            elif line.find('{') >= 0:
                print(line)
                if title == '':
                    f = re.findall(r'\"title\":\"(?P<soc>[^"]*)', line);  # (?P<soc>\[^\"\]*)\"',line);
                    title = f[0];
                    f = re.findall(r'\"artist\":\"(?P<soc>[^"]*)', line);  # (?P<soc>\[^\"\]*)\"',line);
                    artist = f[0];
                    f = re.findall(r'\"duration\":(?P<soc>[^,]*)', line);  # (?P<soc>\[^\"\]*)\"',line);
                    duration = float(f[0]);
                    #f = re.findall(r'\"segment\":(?P<soc>[^,]*)', line);  # (?P<soc>\[^\"\]*)\"',line);
                    #FragmentCount = int(f[0]); #evil count
                    heuristikFragmentCount =int(duration/ 5.0) #assuming 5 sec per fragment
                    line = buf.readline()
                    f = re.findall(r'(?P<PRE>[^"]*)track(?P<COUNT>\d*)(?P<POST>.*)',   line);
                    lurl = f[0][0] + "track0" + f[0][2]
                    for i in range(heuristikFragmentCount):
                        HLSdoc += '#EXTINF:10,\n';
                        HLSdoc += f[0][0] + "track" + str(i) + f[0][2] + '\n';
                    break;

            line = buf.readline()

        #formats = []
        HLSdoc += '#EXT-X-ENDLIST\n';
        dataurl = base64.b64encode(bytes(HLSdoc, 'utf-8')).decode("utf-8")

        formats = self._extract_m3u8_formats(  'data:application/x-mpegURL;base64,' + dataurl, video_id, 'mp4',entry_protocol='m3u8_native')

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': artist+' - '+title,
            # 'description': strip_or_none(video_data.get('description')),
            # 'duration': float_or_none(video_data.get('duration')),
            'formats': formats,
            # 'subtitles': {},
            # 'age_limit': parse_age_limit(video_data.get('tvRating')),
            # 'thumbnail': video_data.get('poster'),
            # '#timestamp': parse_iso8601(video_data.get('launchDate')),
            # 'series': series,
            # 'season_number': int_or_none(video_data.get('seasonNumber')),
            # 'episode': episode_title,
            # 'episode_number': int_or_none(video_data.get('episodeNumber')),
        }



        self._sort_formats(formats)
        return {
            'id': video_id,
             'title': 'aucaiogtitle',
            'uploader': 'TODO',
            'uploader_id': 'TODO',
             'formats': formats,
            'duration':duration,
           # 'description': ogdescription,  # livestream.get('content'),
            #'thumbnail': '',  # livestream.get('thumbnailUrl'),
            'is_live': False,
            # 'timestamp': int_or_none(livestream.get('createdAt'), 1000),
            # 'view_count': int_or_none(livestream.get('watchingCount')),
        }


