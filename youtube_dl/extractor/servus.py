# coding: utf-8
from __future__ import unicode_literals
import re
import urllib, os
from .common import InfoExtractor
from ..utils import (
    determine_ext,
    float_or_none,
    int_or_none,
    unified_timestamp,
    urlencode_postdata,
    url_or_none,
)


class ServusIE(InfoExtractor):
 
                    
                    
    _VALID_URL = r'https?:\/\/(?:www\.)?servustv\.com(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)\/'
    _TESTS = [{
        # new URL schema
        'url': 'https://www.servustv.com/videos/aa-1t6vbu5pw1w12/',
        'md5': '60474d4c21f3eb148838f215c37f02b9',
        'info_dict': {
            'id': 'AA-1T6VBU5PW1W12',
            'ext': 'mp4',
            'title': 'Die Grünen aus Sicht des Volkes',
            'alt_title': 'Talk im Hangar-7 Voxpops Gruene',
            'description': 'md5:1247204d85783afe3682644398ff2ec4',
            'thumbnail': r're:^https?://.*\.jpg',
            'duration': 62.442,
            'timestamp': 1605193976,
            'upload_date': '20201112',
            'series': 'Talk im Hangar-7',
            'season': 'Season 9',
            'season_number': 9,
            'episode': 'Episode 31 - September 14',
            'episode_number': 31,
        }
    }, {
        # old URL schema
        'url': 'https://www.servus.com/de/p/Die-Gr%C3%BCnen-aus-Sicht-des-Volkes/AA-1T6VBU5PW1W12/',
        'only_matching': True,
    }, {
        'url': 'https://www.servus.com/at/p/Wie-das-Leben-beginnt/1309984137314-381415152/',
        'only_matching': True,
    }, {
        'url': 'https://www.servus.com/tv/videos/aa-1t6vbu5pw1w12/',
        'only_matching': True,
    }, {
        'url': 'https://www.servus.com/tv/videos/1380889096408-1235196658/',
        'only_matching': True,
    }, {
        'url': 'https://www.pm-wissen.com/videos/aa-24mus4g2w2112/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        #video_id = re.match(self._VALID_URL, url).groups()
        video_id = self._match_id(url).upper()
        print("vid id %s"%(video_id))
        
        #TODO dig webpage to find  asset_link (realurl with id)
        
        heads = {'Sec-Fetch-User':'?1','Sec-Fetch-Mode':'navigate','Accept-Language':'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Sec-Fetch-Dest':'document','TE':'trailers','Upgrade-Insecure-Requests':'1','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding':'gzip, deflate, br',
    'Cookie':'_rbGeo=de; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+23+2021+13%3A21%3A28+GMT%2B0200+(heure+d%E2%80%99%C3%A9t%C3%A9+d%E2%80%99Europe+centrale)&version=6.21.0&isIABGlobal=false&hosts=&consentId=21c0a6e0-170b-456a-842b-97202c0d3f13&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CSTACK42%3A1&geolocation=FR%3BOCC&AwaitingReconsent=false; OptanonAlertBoxClosed=2021-08-20T11:17:10.458Z; eupubconsent-v2=CPLO5dCPLO5dCAcABBENBmCsAP_AAH_AAAYgIJtf_X__b3_j-_59f…_9nN___9ggmASYal9AF2JY4Mm0aVQogRhWEh0AoAKKAYWiawgZXBTsrgI9QQsAEJqAjAiBBiCjFgEAAgEASERASAHggEQBEAgABACpAQgAI2AQWAFgYBAAKAaFiBFAEIEhBkcFRymBARItFBPZWAJRd7GmEIZZYAUCj-iowEShBAsDISFg5jgCQEuAAA.f_gAD_gAAAAA; _garb=GA1.2.1521935483.1629458232; iom_consent=010fff0fff&1629717688528; ioam2018=000fda3f1f81cd885611f9015:1659698231544:1629458231544:.servustv.com:53:at_w_comservtv:RedCont/Lifestyle/LifestyleUeberblick:noevent:1629717687983:b928do; _gcl_au=1.1.1215458551.1629458232; _garb_gid=GA1.2.1633934174.1629706560'
    };
        webpage = self._download_webpage(url, video_id);#, headers=heads)
        #finding =re.search('\"(aa_id)\":\"(?P<id>\w+)\"', webpage) 
        #if finding :
        #   self.to_screen(finding);
        #self.to_screen(finding);
        
        #token = self._download_json(
        #    'https://auth.redbullmediahouse.com/token', video_id,
        #    'Downloading token', data=urlencode_postdata({
        #        'grant_type': 'client_credentials',
        #    }), headers={
        #        'Authorization': 'Basic SVgtMjJYNEhBNFdEM1cxMTpEdDRVSkFLd2ZOMG5IMjB1NGFBWTBmUFpDNlpoQ1EzNA==',
        #    })
        #access_token = token['access_token']
        #token_type = token.get('token_type', 'Bearer')

        videojsonhandle = self._download_json_handle(
            'https://api-player.redbull.com/stv/servus-tv?videoId=%s&timeZone=Europe/Paris' % video_id,
            video_id, 'Downloading video JSON', headers={
                #'Authorization': '%s %s' % (token_type, access_token),
                'Referer': '%s' % ('https://www.servustv.com/'),
                'Origin': '%s' % ('https://www.servustv.com/'),
            },fatal=False)
            
        title =  video_id
        alt_title = ''
        thumbnail =  ''
        description = ''
        series =''
        season = ''
        episode =''
        #duration = float_or_none(attrs.get('duration'), scale=1000) 
        timestamp=''
        if not videojsonhandle:#assume global live stream
          resource='https://rbmn-live.akamaized.net/hls/live/2002830/geoSTVDEweb/master.m3u8';
        else:
            
            video= videojsonhandle[0];    
            print(video)
            resource= video['videoUrl'] 
            title = video['title'] or video_id
            try:
                alt_title = video['title']
                thumbnail =  video['poster']
                description = video['description']#attrs.get('long_description') or attrs.get('short_description')
                timestamp=unified_timestamp(video.get('lastPublished'))
                series = video['label']
                season = video['season']
                episode =video['chapter']
                #duration = float_or_none(attrs.get('duration'), scale=1000) 
            except:
                episode = '';
        print(resource)
        formats = []
        thumbnail = None
        #print(resource);
        #if not isinstance(resource, dict):            continue
        format_url =resource;#video['videoUrl'] # url_or_none(resource.get('url'))
        #if not format_url:            continue
        path = urllib.parse.urlparse(format_url).path
        extension = os.path.splitext(path)[1]
        #extension = resource.get('extension')
        type_ = '';#resource.get('type')
        is_live = False
        #if extension == 'jpg' or type_ == 'reference_keyframe':            thumbnail = format_url            continue
        ext = determine_ext(format_url)
        if type_ == 'dash' or ext == 'mpd':
            formats.extend(self._extract_mpd_formats(
                format_url, video_id, mpd_id='dash', fatal=False))
        elif type_ == 'hls' or ext == 'm3u8':
            live, fmts =self._extract_m3u8_live_and_formats(
                format_url, video_id, 'mp4', entry_protocol='m3u8_native',
                m3u8_id='hls', fatal=False)
            if live: is_live =True
            formats.extend(fmts)
        elif extension == 'mp4' or ext == 'mp4':
            formats.append({
                'url': format_url,
                'format_id': type_,
                'width': int_or_none(resource.get('width')),
                'height': int_or_none(resource.get('height')),
            })
        self._sort_formats(formats)
        print(formats);
        attrs = {}
        if False:
         for attribute in video['attributes']:
            if not isinstance(attribute, dict):
                continue
            key = attribute.get('fieldKey')
            value = attribute.get('fieldValue')
            if not key or not value:
                continue
            attrs[key] = value



        return {
            'id': video_id,
            'title': title,
            'alt_title': alt_title,
            'description': description,
            'thumbnail': thumbnail, 
            'timestamp': timestamp,
            'series': series,
            'season': season, 
            'episode': episode, 
            'formats': formats,
            'is_live':is_live
        }
