
from __future__ import unicode_literals
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
    compat_urllib_parse_unquote_plus,
    std_headers,
    parse_m3u8_attributes,
    compat_urllib_parse_urlparse,
    parse_codecs
)

from youtube_dl.compat import (
  compat_urllib_request
)
class ComedyShowIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?comedyshow\.to/player/index\.php\?data\=(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'http://itvhay.org/xem-phim-dau-la-dai-luc-371842',
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
        video_id = re.match(self._VALID_URL, url).groups()[0]
        #print(show_path);
        webpage=self._download_webpage(url,video_id);
        propvalpattern='FirePlayer\(\w+,\s*(?P<json>{.*})'
        matches = re.findall( propvalpattern,   webpage)

        ogdescription='';
        rawjson=matches[0]
        json=self._parse_json(rawjson,video_id)
        ogtitle = json['title']
        videopath=json['videoUrl']
        manifesturl='https://comedyshow.to'+videopath+'?s='+json['videoServer']+'&d='

        #reset defaults headers to avoid "security error"
        std_headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.33 Safari/537.36',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-us,en;q=0.5',
        }
        # manifest=self._download_webpage(manifesturl,video_id+'manifest',headers=std_headers)
        # while manifest=='security error':
        #     time.sleep(1)
        #     manifest=self._download_webpage(manifesturl,video_id+'manifest',headers=std_headers)
        trycount=0
        manifest=self._download_webpage(manifesturl,video_id+'manifest',headers=std_headers)
        while manifest=='security error' and trycount<10:
            time.sleep(1)#random.randrange(1, 5, 1))
            manifest=self._download_webpage(manifesturl,video_id+'manifest',headers=std_headers)
            trycount=trycount+1
        #islive, formats, dum = self._parse_m3u8_formats(manifest, manifesturl, video_id + 'manifest')
        m3u8_doc=manifest
        m3u8_id=video_id
        formats=[]
        m3u8_url=url

        format_url = lambda u: (
            u
            if re.match(r'^https?://', u)
            else compat_urlparse.urljoin(m3u8_url, u))
        def build_stream_name():
            # Despite specification does not mention NAME attribute for
            # EXT-X-STREAM-INF tag it still sometimes may be present (see [1]
            # or vidio test in TestInfoExtractor.test_parse_m3u8_formats)
            # 1. http://www.vidio.com/watch/165683-dj_ambred-booyah-live-2015
            stream_name = last_stream_inf.get('NAME')
            if stream_name:
                return stream_name
            # If there is no NAME in EXT-X-STREAM-INF it will be obtained
            # from corresponding rendition group
            stream_group_id = last_stream_inf.get('VIDEO')
            if not stream_group_id:
                return
            stream_group = groups.get(stream_group_id)
            if not stream_group:
                return stream_group_id
            rendition = stream_group[0]
            return rendition.get('NAME') or stream_group_id

        for line in m3u8_doc.splitlines():
            if line.startswith('#EXT-X-STREAM-INF:'):
                last_stream_inf = parse_m3u8_attributes(line)
            elif line.startswith('#') or not line.strip():
                continue
            else:
                tbr = float_or_none(
                    last_stream_inf.get('AVERAGE-BANDWIDTH')
                    or last_stream_inf.get('BANDWIDTH'), scale=1000)
                format_id = []
                if m3u8_id:
                    format_id.append(m3u8_id)
                stream_name = build_stream_name()
                # Bandwidth of live streams may differ over time thus making
                # format_id unpredictable. So it's better to keep provided
                # format_id intact.
                if True:#not live:
                    format_id.append(stream_name if stream_name else '%d' % (tbr if tbr else len(formats)))
                manifest_url = format_url(line.strip())

                # sublive,sub, subtitleformats  = self._extract_m3u8_live_and_formats(manifest_url, '-'.join(format_id), 'mp4',fatal=False)
                # if len(sub)==0:#4040
                #     continue
                # if sublive:
                #     live=True;

                f = {
                    'format_id': '-'.join(format_id),
                    'url': manifest_url,
                    'manifest_url': manifesturl,
                    'tbr': tbr,
                    'ext': 'mp4',
                    'fps': float_or_none(last_stream_inf.get('FRAME-RATE')),
                    'protocol': 'm3u8',
                    #'preference': preference,
                    #'subformats':sub,#composite streams of this format
                }
                resolution = last_stream_inf.get('RESOLUTION')
                if resolution:
                    mobj = re.search(r'(?P<width>\d+)[xX](?P<height>\d+)', resolution)
                    if mobj:
                        f['width'] = int(mobj.group('width'))
                        f['height'] = int(mobj.group('height'))
                # Unified Streaming Platform
                mobj = re.search(
                    r'audio.*?(?:%3D|=)(\d+)(?:-video.*?(?:%3D|=)(\d+))?', f['url'])
                if mobj:
                    abr, vbr = mobj.groups()
                    abr, vbr = float_or_none(abr, 1000), float_or_none(vbr, 1000)
                    f.update({
                        'vbr': vbr,
                        'abr': abr,
                    })
                codecs = parse_codecs(last_stream_inf.get('CODECS'))
                f.update(codecs)
                audio_group_id = last_stream_inf.get('AUDIO')
                # As per [1, 4.3.4.1.1] any EXT-X-STREAM-INF tag which
                # references a rendition group MUST have a CODECS attribute.
                # However, this is not always respected, for example, [2]
                # contains EXT-X-STREAM-INF tag which references AUDIO
                # rendition group but does not have CODECS and despite
                # referencing an audio group it represents a complete
                # (with audio and video) format. So, for such cases we will
                # ignore references to rendition groups and treat them
                # as complete formats.
                if audio_group_id and codecs and f.get('vcodec') != 'none':
                    audio_group = groups.get(audio_group_id)
                    if audio_group and audio_group[0].get('URI'):
                        # TODO: update acodec for audio only formats with
                        # the same GROUP-ID
                        f['acodec'] = 'none'


                #update extension according codecs
                if f.get('vcodec') != 'none':
                    #FORCE EXTENSION  if f['vcodec'].find('av')==0:
                        f['ext']='mp4'
                else:
                    if f['acodec'].find('mp4a')==0:
                        f['ext']='aac'
                    else:
                        f['ext']='mp3' #FORCE EXTENSION
                formats.append(f)

                # for DailyMotion
                progressive_uri = last_stream_inf.get('PROGRESSIVE-URI')
                if progressive_uri:
                    http_f = f.copy()
                    del http_f['manifest_url']
                    http_f.update({
                        'format_id': f['format_id'].replace('hls-', 'http-'),
                        'protocol': 'http',
                        'url': progressive_uri,
                    })
                    formats.append(http_f)

                last_stream_inf = {}


        #no headers for streams
        for f in formats:
            f['http_headers']= {}

        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': ogtitle,
            'uploader': 'TODO',
            'uploader_id': 'TODO',
            'formats': formats,
            'description': ogdescription,
            'is_live': False,
            #'http_headers':std_headers,
        }
        #formats=self._extract_m3u8_live_and_formats(manifesturl,video_id+'manifest',headers=std_headers)


        #
        # matches = re.findall(
        #     r'<iframe.*src="(?P<EMBED>[^\?]*)\?link=(?P<LINK>[^\"]*)".*>',

        # matches = re.findall(
        #     r'<iframe.*id="(?P<ID>[^\"]*)".*></iframe><script>(?P<EVAL>.*)</script>',
        # webpage)
        #
        # jsscramble=  matches[0][1]
        #
        # res=self._download_json('http://localhost:3000',video_id='video_id',
        #                     data=json.dumps({'js': jsscramble[1:]}).encode(),
        #                     headers={'Content-Type':'application/json'})
        #
        # resstr=compat_urllib_parse_unquote_plus( res['result'])
        #
        #
        # matches = re.findall(
        # r'.*setAttribute\("src","(?P<EMBED>[^\"]*)',
        # resstr,8)
        # embedlink=matches[0][24:]
        #
        #
        # matches = re.findall(
        #     r'.*\/(?P<ID>[\d|\w]*$)',
        #     embedlink)
        #
        # if not matches :#embed video from other site
        #     return
        # video_id= matches[0] ;

        if False:#embedlink.find('fembed')>=0:#TODO https://www.fembed.com/v/ID

            #get server page video data
            prejsonwebpage = self._download_webpage('http://itvhay.org/preload/habet.php', video_id, headers={
                # 'Host': 'api-if.tvhaystream.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                 'Referer': '%s?link=%s' % ( embedlink,embedlink),
                #'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            })

        else:  #https://play.tvhaystream.xyz/play/v1/ID
            prejsonwebpage=self._download_webpage(embedlink, video_id, headers={
                # 'Host': 'api-if.tvhaystream.xyz',
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
                'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            }
            videojsonhandle = self._download_json_handle(
                addr,
                show_path, 'Downloading video JSON',
                data=bytes('referrer=http://itvhay.org&typeend=html', 'utf-8'),
                headers=   headers , fatal=False)


            requestresult= videojsonhandle[0]
            print(requestresult)

            m3u8_doc='#EXTM3U\n'
            m3u8_doc+='#EXT-X-VERSION:3\n'
            m3u8_doc+='#EXT-X-TARGETDURATION:10\n'
            m3u8_doc+='#EXT-X-PLAYLIST-TYPE:VOD\n'
            headers = {'Accept': '*/*',
                       'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                       'User-Agent': 'Mozilla/5.0',# (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
                       "Accept-Encoding": "gzip, deflate",
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

            self._sort_formats(formats)
            return {
                'id': video_id,
                'title': ogtitle,
                'uploader': 'TODO',
                'uploader_id': 'TODO',
                'formats': formats,
                'description': ogdescription,
                'is_live': False,
            }


