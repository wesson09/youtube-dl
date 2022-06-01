# coding: utf-8


from __future__ import unicode_literals
import urllib3
import time
import http.client
import json
import re

import base64
from typing import *


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
    try_get, sanitize_url,
    HEADRequest,
)

from youtube_dl.compat import (
  compat_urllib_request
)
class TVhaiIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(tvhai|tvhey)\.org(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'http://tvhai.org/xem-phim-dau-la-dai-luc-371842',
        'info_dict': {
            'id': 'rQxZvXQ4ROaSOqq-or2Mow',
            'ext': 'mp4',
            'title': 'Rot',
            'description': 'R.',
            'timestamp': 1543294800,
            'upload_date': '20181127',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Unable to download f4m manifest'],
    },
    ]


    def _real_extract(self, url):
        show_path = re.match(self._VALID_URL, url).groups()[2]
        #print(show_path);
        headers={
                'Host': 'cdn-rd.apirdtvhai.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',

            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            }
        proxies = {
            "http": 'http://localhost:8120',
            "https": 'http://localhost:8120',
        }
        http = urllib3.PoolManager()

        #r = http.request('GET', 'https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121')
        #res=self._download_webpage('https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121','fok', headers=headers)
        # res= requests.get('https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121', headers=headers
        #       ,allow_redirects=True,proxies=proxies,verify=False)
        # res = requests.get(
        #     'https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121'
        #    , allow_redirects=True);

        webpage=self._download_webpage(url,show_path);
        propvalpattern='<\s*meta\s+property\s*=\s*\"og:(?P<prop>[\w^\"]+)\"\s+content\s*=\s*\"(?P<value>[\w\W]|[^\"]*)\"\s*\/\s*>'
        matches = re.finditer( propvalpattern,   webpage)
        ogtitle='';
        ogdescription='';
        for m in matches:
            if m.group(1) == 'title' :
                ogtitle=m.group(2);
            elif m.group(1) == 'description' :
                ogdescription=m.group(2);

        matches = re.findall(
            r'<iframe.*src="(?P<EMBED>[^\?]*)\?link=(?P<LINK>[^\"]*)".*>',
            webpage)
        embed=matches[0][0]
        embedlink=matches[0][1]

        matches = re.findall(
            r'.*\/(?P<ID>[\d|\w]*$)',
            embedlink)

        if not matches :#embed video from other site
            return
        video_id= matches[0];


        if embedlink.find('fembed')>=0:#TODO https://www.fembed.com/v/ID

            #get server page video data
            prejsonwebpage = self._download_webpage('http://tvhai.org/preload/habet.php', video_id, headers={
                # 'Host': 'api-if.tvhaystream.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                 'Referer': '%s?link=%s' % ( embed,embedlink),
                #'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            })

        else:  #https://play.tvhaystream.xyz/play/v1/ID
            prejsonwebpage=self._download_webpage(embedlink, video_id, headers={
                # 'Host': 'api-if.tvhaystream.xyz',
                'Proxy-Connection':'keep-alive','Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                'Origin': '%s' % ('https://play.tvhaystream.xyz'),
                });


            matches = re.findall('var idUser = "(?P<ID>\w+)"',prejsonwebpage);
            #  print(matches);
            idUser=matches[0]
            matches = re.findall('var DOMAIN_API = \'(?P<ID>[\w:\/.-]+)\'',prejsonwebpage);
            #print(matches);
            DOMAIN_API=matches[0];

            matches = re.findall(r'((?P<SCHEME>(?:https?))\:\/\/(?P<HOSTNAME>(?:www.|[a-zA-Z0-9.]+)[a-zA-Z0-9\-\.]+\.([a-zA-Z0-9]*))(?P<PORT>\:[0-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?P<PATH>[a-zA-Z0-9\-\.\/]+)?(?P<QUERY>(?:\?$|[a-zA-Z0-9\.\,\;\?\'\\\+&%\$\=~_\-\*]+))?(?P<FRAGMENT>#[a-zA-Z0-9\-\.]+)?)'
            ,DOMAIN_API);
            hostname=matches[0][2];

            matches = re.findall('var DOMAIN_LIST_RD[ \t\n]=[ \t\n]\[(?P<domainlist>.*)\]',prejsonwebpage);
            matches = re.findall('\"(?P<domain>[^\"]*)\"',matches[0]);

            DOMAIN_LIST_RD= matches;


            addr = '%s%s/%s' % (DOMAIN_API,idUser,video_id)

            requestresult=''

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                'Accept': '*/*',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
	  'Referer': embedlink,
                'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            }
            videojsonhandle = self._download_json_handle(
                addr,
                show_path, 'Downloading video JSON',
                data=bytes('referrer=http://tvhey.org&typeend=html', 'utf-8'), headers=   headers , fatal=False)


            requestresult= videojsonhandle[0]
            #print(requestresult)

            m3u8_doc='#EXTM3U\n'
            m3u8_doc+='#EXT-X-VERSION:3\n'
            m3u8_doc+='#EXT-X-TARGETDURATION:10\n'
            m3u8_doc+='#EXT-X-PLAYLIST-TYPE:VOD\n'
            headers = {'Accept': '*/*',
                       'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                       'User-Agent': 'Mozilla/5.0',# (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
                       "Accept-Encoding": "gzip, deflate",
                       }
            headers ={'Host':'cdn-rd.apirdtvhai.xyz',
	  'User-Agent': 'Mozilla\/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'Accept': '*/*',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
	 # 'Accept-Encoding': 'gzip, deflate, br',
	  'Origin': 'https://play.plhqtvhay.xyz',
	  'Connection': 'keep-alive',
	  'Referer': 'https://play.plhqtvhay.xyz/',
	  'Sec-Fetch-Dest': 'empty',
	  'Sec-Fetch-Mode': 'no-cors',
	  'Sec-Fetch-Site': 'cross-site',

                       'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
            }
            headers={
            #     'Host': 'cdn-rd.apirdtvhai.xyz',
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            #     'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            #     #'Accept-Encoding': 'gzip, deflate, br',
            #     'Connection': 'keep-alive',
            #     'Upgrade-Insecure-Requests': '1',
            #     'Sec-Fetch-Dest': 'document',
            #     'Sec-Fetch-Mode': 'navigate',
            #     'Sec-Fetch-Site': 'none',
            #     'Sec-Fetch-User': '?1',
            #
            # 'Pragma': 'no-cache',
            # 'Cache-Control': 'no-cache',
            }
            idx=0
            idxdomain=0
            for v in requestresult['data'][1]:
                domain = DOMAIN_LIST_RD[idxdomain];
                idxdomain = idxdomain + 1
                if idxdomain >= len(DOMAIN_LIST_RD):
                    idxdomain = 0
                m3Uchunk='https://%s/%s' % (domain, v)
                m3u8_doc +='#EXTINF:%s,\n' % requestresult['data'][0][idx]
                m3u8_doc +='#EXT-X-BYTERANGE:100000000000@8\n'
                m3u8_doc += m3Uchunk+'\n'
                idx=idx+1
            m3u8_doc +='#EXT-X-ENDLIST\n'
            #print(m3u8_doc)
            d=base64.b64encode(bytes(m3u8_doc, 'UTF-8'))
            dataurl='data:application/x-mpegURL;base64,' +d.decode(encoding="utf-8");
            formats = self._extract_m3u8_formats(
            dataurl,
               video_id, 'mp4',entry_protocol='m3u8_native')
            for f in formats:
                f['http_headers']=headers;
            self._sort_formats(formats)
            # res=requests.get('https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121'
            #                  ,  headers=headers        );
            #
            #
            # fok=self._download_webpage('https://cdn-rd.apirdtvhai.xyz/rdv1/5ee31dd5665f2d19d5af4a99/6090a454700883c6e698f36e29a7ae9950129efea8c0f1b68cbe0a828779d2972a4dfa2be68f753555086acaa17ebe0e/cd94dddcddbc34102989c3af9c996121',video_id,
            #                            headers=headers);
            return {
                'id': video_id,
                'title': ogtitle,
                'uploader': 'TODO',
                'uploader_id': 'TODO',
                'formats': formats,
                'description': ogdescription,
                'is_live': False,
                'http_headers':headers,
            }


