

# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_HTTPError
from ..utils import (
    dict_get,
    ExtractorError,
    int_or_none,
    js_to_json,
    parse_iso8601,
)

from ..downloader.external import (
    WebSocketFD,
)
from threading import Thread
import time
import sys

wspingurl = "wss://dss-relay-109-71-162-29.dditscdn.com/?random=76642862828024091022282852184340";
testurl = "wss://cdn-e05.showup.tv/h5live/stream/?url=rtmp%3A%2F%2Fcdn-t02.showup.tv%3A1935%2Fwebrtc&stream=6ca4a6616b9a761a40a0ca922ce8a741_aac&cid=36552&pid=49325072002";
initmsg = r'{"event":"register","applicationId":"memberChat/jasminRosseMclay377e58b0b81e98dadc4141d0d8d3af8b","connectionData":{"jasmin2App":true,"isMobileClient":false,"platform":"desktop","chatID":"freechat","sessionID":"m12345678901234567890123456789012","jsm2SessionId":"g1e270442bb0e0b609765eb7e17f760ee","userType":"user","performerId":"RosseMclay","clientRevision":"","playerVer":"nanoPlayerVersion: 4.12.1 appCodeName: Mozilla appName: Netscape appVersion: 5.0 (X11) platform: Linux x86_64","livejasminTvmember":false,"newApplet":true,"livefeedtype":null,"gravityCookieId":"","passparam":"","brandID":"jasmin","cobrandId":"livejasmin","subbrand":"livejasmin","siteName":"LiveJasmin","siteUrl":"https://www.livejasmin.com","clientInstanceId":"12978542516430979517930396516071","armaVersion":"36.15.7","isPassive":true,"chatHistoryRequired":true,"peekPatternJsm2":true}}';


#ping pong cbs
def on_message(wsr, message):
    print(message)


def on_error(wsr, error):
    print(error)


def on_close(wsr):
    print("### closed ###")


def on_open(wsr):
    def run(*args):
        # fok=ws.recv()
        # wsr.recv();
        wsr.send(initmsg)

        time.sleep(1)

        for i in range(100):
            # send the message, then wait
            if (i == 2):
                wsr.send('{"event":"call","funcName":"makeActive","data":[]}')
            else:
                wsr.send('{"event": "ping"}');
            #
            time.sleep(2)

        time.sleep(1)
        wsr.close()
        print("Thread terminating...")

    Thread(target=run).start()


def on_message(wsr, message):
    print(message)


def on_message_stream(wsr, message):
    try:
        foki = bytes(message, 'utf-8');

        if not message.startswith('{"eventType'):
            wsr.outputfile.write(message);
    except:
        wsr.outputfile.write(message);



def on_error_stream(wsr, error):
    print(error)


def on_close_stream(wsr,bla,vla):
    print("### closed ###")
    wsr.outputfile.close();

def on_open_stream(wsr):
    print("Thread on_open_stream...")
    def run(*args):
        # fok=ws.recv()
        # wsr.recv();
        wsr.send(initmsg)

        time.sleep(1)

        for i in range(100):
            # send the message, then wait
            if (i == 2):
                wsr.send('{"event":"call","funcName":"makeActive","data":[]}')
            else:
                wsr.send('{"event": "ping"}');
            #
            time.sleep(2)

        time.sleep(1)
        wsr.close()
        print("Thread terminating...")

    Thread(target=run).start()


class ShowUpTVIE(InfoExtractor):
    _ID_RE = r'[\da-fA-F]+'
    _COMMON_RE = r'//player\.zype\.com/embed/%s\.(?:js|json|html)\?.*?(?:access_token|(?:ap[ip]|player)_key)='
    _VALID_URL = r'https?://showup\.tv/(?P<id>.*)';
    _TEST = {
        'url': 'https://player.zype.com/embed/5b400b834b32992a310622b9.js?api_key=jZ9GUhRmxcPvX7M3SlfejB6Hle9jyHTdk2jVxG7wOHPLODgncEKVdPYBhuz9iWXQ&autoplay=false&controls=true&da=false',
        'md5': 'eaee31d474c76a955bdaba02a505c595',
        'info_dict': {
            'id': '5b400b834b32992a310622b9',
            'ext': 'mp4',
            'title': 'Smoky Barbecue Favorites',
            'thumbnail': r're:^https?://.*\.jpe?g',
            'description': 'md5:5ff01e76316bd8d46508af26dc86023b',
            'timestamp': 1504915200,
            'upload_date': '20170909',
        },
    }

    @staticmethod
    def _extract_urls(webpage):
        return [
            mobj.group('url')
            for mobj in re.finditer(
                r'<script[^>]+\bsrc=(["\'])(?P<url>(?:https?:)?%s.+?)\1' % (ZypeIE._COMMON_RE % ZypeIE._ID_RE),
                webpage)]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage=self._download_webpage(url,video_id,headers={
                    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests":"1",
            "Cache-Control":"no-cache",
            "Cookie":"accept_rules=true; wsUID=f07bd0f061a073a56d5e0e0f1b0ece80; __utma=185028331.1220171536.1641203129.1641203129.1641288547.2; __utmc=185028331; __utmz=185028331.1641288547.2.2.utmcsr=www.google.com|utmccn=(referral)|utmcmd=referral|utmcct=/; waPlayer-volumev2=100; waPlayer-backup-volumev2=100; currWatchedTimeSeconds3870041=146630; __utmb=185028331.4.10.1641288547; currWatchedTimeSeconds3863214=1185; currWatchedTimeSeconds1322941=1025; showup=b85ab1db318a31fe75cccc3fb54f78dd",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
        })
        f = re.findall(
                # r'availableDesktopStreamQueue[\s|.]*=[\s|.]*\[{"url":"(?P<URL>[^"]*)","codec":"(?P<CODEC>[^"]*)","bitrate":(?P<bitrate>[^,]*)',
            r'csrfToken[\s\S]*/script>',
                 webpage);
        # f=r'var csrfToken = '';    var am = [[" p*l "," p*l$","1qndmi0","\\.com","\\.eu","\\.net","\\.pl","\\.tv","\\.us","c0","chomik","http","inn(\\.+)stro","kropka","kurwiskiem","kurwiskiem","kurwisz","kurwo","nagra","nagry","nagrywam","oble.na","pasztet","patologia","prostytu","redhouse","sexups","skajp","skp","skype","szkole","szmacic","szmata","szmato","szmaty","tnij","vivet","wentyle","www","zwisy","roomx"],[".com","cam4","goo.gl","haste","livejasmine","liveshow","sexrura","sexups.ga","studio24","wrzucie","wrzutapl","zbi0rnik","zbiornik","redcams"]];autoModerator.init(); var swfThresholdMinute = 180;var swfThresholdLimit = 40; var messagePrice = 5;  jQuery(function ($) { player.stormStreamingAddr = \'cdn-e05.showup.tv\';transList.stormStreamingAddr = \'cdn-e05.showup.tv\';if (!Modernizr.touch) transList.attachVideoPreview();player.posterURL = \'files/466411.jpg\'; transmission.init(1322941, \'_Alicja_\', false, \'//cdn-s01.showup.tv/files/59c7f81312b65/63-5ef9127a7b063.png\'); player.streamID = \'6ca4a6616b9a761a40a0ca922ce8a741\';player.transcoderAddr = \'cdn-t02.showup.tv\';transmission.hostUser.uid = 1322941;player.start(); prvChat.init();'
        # '});';
        r = re.findall(
            r'player\.stormStreamingAddr = \'(?P<paddr>[^\']*)\'.*transList\.stormStreamingAddr = \'(?P<tladdr>[^\']*)\'.*transmission\.init\((\d*), \'([^\']*)\', false, \'(?P<thumb>[^\']*)\'\); player\.streamID = \'(?P<streamID>[^\']*)\';player\.transcoderAddr = \'(?P<transcoderAddr>[^\']*)\';transmission\.hostUser\.uid = \d*',
        f[0]);

        wssurl=r'wss://'+r[0][0]+'/h5live/stream/?url=rtmp%3A%2F%2F'+r[0][6]+'%3A1935%2Fwebrtc&stream='+r[0][5]+'_aac&cid=549236&pid=85171025744'

        f={}
        if self._downloader.params.get('dump_single_json') :
            f = {
                'url': wssurl,
                'protocol': 'wss',
            }
        else:
            f={
                'url':wssurl,
                'protocol':'wss',
                'on_open':on_open_stream,
                'on_error':on_error_stream,
                'on_close':on_close_stream,
                'on_message':on_message_stream,
            }
        formats=[];
        formats.append(f);
        return {
            'id': video_id, 'ext': 'mp4',
            # 'display_id': display_id,
            'title': 'title',
            # 'description': dict_get(video, ('description', 'caption'),
            #                         try_get(video, lambda x: x['meta']['description'])),
            'thumbnail': r[0][4],
            # 'timestamp': int_or_none(video.get('date')),
            # 'duration': int_or_none(video.get('length')),
            'formats': formats,
            'is_live': True,

        }

        #websocket.enableTrace(True)

        wsapp = websocket.WebSocketApp(wspingurl,
            header=[#"User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
                    #"Accept: */*",
                    "Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding: gzip, deflate, br",
                    #"Sec-WebSocket-Version: 13",
                    "Origin: https://www.livejasmin.com",
                    #"Sec-WebSocket-Extensions: permessage-deflate",
                    #"Sec-WebSocket-Key: pRml08fEvb9ltStMfr4xGQ==",
                    "Connection: keep-alive, Upgrade",
                    "Sec-Fetch-Dest: websocket",
                    "Sec-Fetch-Mode: websocket",
                    "Sec-Fetch-Site: cross-site",
                    "Pragma: no-cache",
                    "Cache-Control: no-cache",
                    "Upgrade: websocket"],
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        wsapp.on_open = on_open
        def arun(*args):
            wsapp.run_forever()

        Thread(target=arun).start()
        time.sleep(2)
        ws = websocket.WebSocket()
        ws2 = websocket.WebSocket()
        header=["User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
                    "Accept: */*",
                    "Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding: gzip, deflate, br",
                    #"Sec-WebSocket-Version: 13",
                    "Origin: https://www.livejasmin.com",
                    #"Sec-WebSocket-Extensions: permessage-deflate",
                    #"Sec-WebSocket-Key: gsVFAaMTdf8HW8pI/f9FhA==",
                    "Connection: keep-alive, Upgrade",
                    "Sec-Fetch-Dest: websocket",
                    "Sec-Fetch-Mode: websocket",
                    "Sec-Fetch-Site: cross-site",
                    "Pragma: no-cache",
                    "Cache-Control: no-cache",
                    "Upgrade: websocket"]
        urltvchannel= "wss://ip-109-71-162-196.dditscdn.com/stream?url=rtmp%3A%2F%2F109.71.162.196%3A1935%2Ftvchannel&stream=amiagold.free.f0bcfb4637753b309dd9c69092ccb1b6&cid=358146&pid=40066140016"
        urltvchannel='wss://ip-109-71-162-197.dditscdn.com/stream?url=rtmp%3A%2F%2F109.71.162.197%3A1935%2Ftvchannel&stream=irisstonee.free.d3fb24c95de3a4877c0031e7657fb93f&cid=328572&pid=69445551233'
        ws.connect(wssurl,header=header


        );
        fok=r'{"event": "register", "applicationId": "memberChat/jasminJuliCartere210a216083da5b089523bf69a93efca", \
         "connectionData": {"jasmin2App": true, "isMobileClient": false, "platform": "desktop", "chatID": "freechat", \
                            "sessionID": "m12345678901234567890123456789012", \
                            "jsm2SessionId": "g1e270442bb0e0b609765eb7e17f760ee", "userType": "user", \
                            "performerId": "JuliCarter", "clientRevision": "", \
                            "playerVer": "nanoPlayerVersion: 4.12.1 appCodeName: Mozilla appName: Netscape appVersion: 5.0 (X11) platform: Linux x86_64", \
                            "livejasminTvmember": false, "newApplet": true, "livefeedtype": null, "gravityCookieId": "", \
                            "passparam": "", "brandID": "jasmin", "cobrandId": "livejasmin", "subbrand": "livejasmin", \
                            "siteName": "LiveJasmin", "siteUrl": "https://www.livejasmin.com", \
                            "clientInstanceId": "13901615120297165003252565425811", "armaVersion": "36.15.7", \
                            "isPassive": true, "chatHistoryRequired": true, "peekPatternJsm2": true}}' ;
        fok=r'{"event": "ping"}';

        fok=ws.recv();
        print(fok)
        fok=ws.recv();
        print(fok)
        fok=ws.recv();
        print(fok)
        # {"eventType": "onServerInfo",
        #  "onServerInfo": {"serverName": "H5Live Server", "serverVersion": "4.1.12.0", "interfaceVersion": "1.0.0.0",
        #                   "events": ["onServerInfo", "onStreamInfo", "onStreamInfoUpdate", "onStreamStatus",
        #                              "onMetaData", "onFrameDropStart", "onFrameDropEnd", "onRandomAccessPoint"],
        #                   "capabilities": ["onPause", "onPlay", "metaKeepAlive", "metastreamonly", "checkandclose"]}}
        # {"eventType": "onStreamStatus", "onStreamStatus": {"status": "started", "requestId": 0, "count": 0, "tag": ""}}
        # this one must be provocated {"eventType": "onUpdateSourceSuccess", "onUpdateSourceSuccess": {"requestId": 0, "count": 0, "tag": ""}}
        # {"eventType": "onStreamInfo", "onStreamInfo": {"haveVideo": true, "haveAudio": true,
        #                                                "mimeType": "video/mp4; codecs=\"avc1.42E01E, mp4a.40.2\"",
        #                                                "prerollDuration": 0,
        #                                                "videoInfo": {"width": 1280, "height": 720, "frameRate": 30},
        #                                                "audioInfo": {"sampleRate": 48000, "channels": 2,
        #                                                              "bitsPerSample": 16}}}

        #binary video format header
        fok=ws.recv();
        f = open('my_file.mp3', 'wb')
        f.write(fok)
        #{"eventType":"onRandomAccessPoint","onRandomAccessPoint":{"streamTime":22.999999999995453}}
        fok=ws.recv();

        #big binary
        fok = ws.recv();
        while (fok) :
          #print(fok);
          f.write(fok)

          fok=ws.recv();

        f.close()





        ws2.connect("wss://dss-live-109-71-162-25.dditscdn.com/stream?url=rtmp://109.71.162.25/memberChat/jasminRoseWine4df9f0a229b98d5f44739fb08de3e403?sessionId-m12345678901234567890123456789012|clientInstanceId-2062541620722766740745437899353&stream=free/stream_854_480_1500&cid=465126&pid=83278118356",
                   header=["User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
                            "Accept: */*",
                            "Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                            "Accept-Encoding: gzip, deflate, br",
                            "Sec-WebSocket-Version: 13",
                            "Origin: https://www.livejasmin.com",
                            "Sec-WebSocket-Extensions: permessage-deflate",
                            "Sec-WebSocket-Key: wyiBBUVUDkhSs5++/0NYqQ==",
                            "Connection: keep-alive, Upgrade",
                            "Sec-Fetch-Dest: websocket",
                            "Sec-Fetch-Mode: websocket",
                            "Sec-Fetch-Site: cross-site",
                            "Pragma: no-cache",
                            "Cache-Control: no-cache",
                            "Upgrade: websocket"]
                   );


        try:
            response = self._download_json(re.sub(
                r'\.(?:js|html)\?', '.json?', url), video_id)['response']
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code in (400, 401, 403):
                raise ExtractorError(self._parse_json(
                    e.cause.read().decode(), video_id)['message'], expected=True)
            raise

        body = response['body']
        video = response['video']
        title = video['title']

        if isinstance(body, dict):
            formats = []
            for output in body.get('outputs', []):
                output_url = output.get('url')
                if not output_url:
                    continue
                name = output.get('name')
                if name == 'm3u8':
                    formats = self._extract_m3u8_formats(
                        output_url, video_id, 'mp4',
                        'm3u8_native', m3u8_id='hls', fatal=False)
                else:
                    f = {
                        'format_id': name,
                        'tbr': int_or_none(output.get('bitrate')),
                        'url': output_url,
                    }
                    if name in ('m4a', 'mp3'):
                        f['vcodec'] = 'none'
                    else:
                        f.update({
                            'height': int_or_none(output.get('height')),
                            'width': int_or_none(output.get('width')),
                        })
                    formats.append(f)
            text_tracks = body.get('subtitles') or []
        else:
            m3u8_url = self._search_regex(
                r'(["\'])(?P<url>(?:(?!\1).)+\.m3u8(?:(?!\1).)*)\1',
                body, 'm3u8 url', group='url', default=None)
            if not m3u8_url:
                source = self._search_regex(
                    r'(?s)sources\s*:\s*\[\s*({.+?})\s*\]', body, 'source')

                def get_attr(key):
                    return self._search_regex(
                        r'\b%s\s*:\s*([\'"])(?P<val>(?:(?!\1).)+)\1' % key,
                        source, key, group='val')

                if get_attr('integration') == 'verizon-media':
                    m3u8_url = 'https://content.uplynk.com/%s.m3u8' % get_attr('id')
            formats = self._extract_m3u8_formats(
                m3u8_url, video_id, 'mp4', 'm3u8_native', m3u8_id='hls')
            text_tracks = self._search_regex(
                r'textTracks\s*:\s*(\[[^]]+\])',
                body, 'text tracks', default=None)
            if text_tracks:
                text_tracks = self._parse_json(
                    text_tracks, video_id, js_to_json, False)
        self._sort_formats(formats)

        subtitles = {}
        if text_tracks:
            for text_track in text_tracks:
                tt_url = dict_get(text_track, ('file', 'src'))
                if not tt_url:
                    continue
                subtitles.setdefault(text_track.get('label') or 'English', []).append({
                    'url': tt_url,
                })

        thumbnails = []
        for thumbnail in video.get('thumbnails', []):
            thumbnail_url = thumbnail.get('url')
            if not thumbnail_url:
                continue
            thumbnails.append({
                'url': thumbnail_url,
                'width': int_or_none(thumbnail.get('width')),
                'height': int_or_none(thumbnail.get('height')),
            })

        return {
            'id': video_id,
            'display_id': video.get('friendly_title'),
            'title': title,
            'thumbnails': thumbnails,
            'description': dict_get(video, ('description', 'ott_description', 'short_description')),
            'timestamp': parse_iso8601(video.get('published_at')),
            'duration': int_or_none(video.get('duration')),
            'view_count': int_or_none(video.get('request_count')),
            'average_rating': int_or_none(video.get('rating')),
            'season_number': int_or_none(video.get('season')),
            'episode_number': int_or_none(video.get('episode')),
            'formats': formats,
            'subtitles': subtitles,
        }

