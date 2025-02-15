# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import (
    compat_str,
    compat_urlparse,
)
from ..utils import (
    ExtractorError,
    int_or_none,
    qualities,
    strip_or_none,
    try_get,
    unified_strdate,
    url_or_none,
)

class ArteTVBaseIE(InfoExtractor):
    _ARTE_LANGUAGES = 'fr|de|en|es|it|pl'
    _API_BASE = 'https://api.arte.tv/api/player/%s'

# no multiple audio stream for live : 2 differents vods fr and de
# class ArteTVLiveIE(ArteTVBaseIE):
#     _VALID_URL = r'''https:\/\/www\.arte\.tv\/(?P<lang>%(langs)s)/direct''' % {'langs': ArteTVBaseIE._ARTE_LANGUAGES}
#     _LANG_URLS={
#         'fr':'https://artesimulcast.akamaized.net/hls/live/2031003/artelive_fr/index.m3u8',
#         'de':'https://artesimulcast.akamaized.net/hls/live/2030993/artelive_de/index.m3u8'
#     }
#     def _real_extract(self, url):
#         video_id='ARTE LIVE'
#         mobj = re.match(self._VALID_URL, url)
#         lang = mobj.group('lang') or mobj.group('lang_2')
#
#         live,formats = self._extract_m3u8_live_and_formats(self._LANG_URLS[lang],video_id)
#         self._sort_formats(formats)
#
#         return {
#             'id': video_id,
#             'title': video_id,
#             'is_live':True,
#             'formats': formats,
#         }
class ArteTVIE(ArteTVBaseIE):
    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            (?:www\.)?arte\.tv/(?P<lang>%(langs)s)/videos|
                            api\.arte\.tv/api/player/(?P<API_VERSION>v\d+)/config/(?P<lang_2>%(langs)s)
                        )
                        /(?P<id>\d{6}-\d{3}-[AF])
                    ''' % {'langs': ArteTVBaseIE._ARTE_LANGUAGES}
    # _VALID_URL = r'''(?x)
    #                 https?://
    #                     (?:
    #                         (?:www\.)?arte\.tv/(?P<lang>%(langs)s)/videos
    #                     )
    #                     /(?P<id>\d{6}-\d{3}-[AF])
    #                 ''' % {'langs': ArteTVBaseIE._ARTE_LANGUAGES}
    _TESTS = [{
        'url': 'https://www.arte.tv/en/videos/088501-000-A/mexico-stealing-petrol-to-survive/',
        'info_dict': {
            'id': '088501-000-A',
            'ext': 'mp4',
            'title': 'Mexico: Stealing Petrol to Survive',
            'upload_date': '20190628',
        },
    }, {
        'url': 'https://www.arte.tv/pl/videos/100103-000-A/usa-dyskryminacja-na-porodowce/',
        'only_matching': True,
    }, {
        'url': 'https://api.arte.tv/api/player/v2/config/de/100605-013-A',
        'only_matching': True,
    }]
    LANGS = {
        'fr': 'F',
        'de': 'A',
        'en': 'E[ANG]',
        'es': 'E[ESP]',
        'it': 'E[ITA]',
        'pl': 'E[POL]',
    }
    TRADS = [
        'fr-FR',
        'de-DE',
        'en-US',
        'es-ES',
        'it-IT',
        'pl-PL',
    ]
    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        API_VERSION = mobj.group('API_VERSION')
        lang = mobj.group('lang')  or mobj.group('lang_2')
        if API_VERSION is None:
            API_VERSION='v2'

        info = self._download_json(
            '%s/config/%s/%s' % ( self._API_BASE%API_VERSION, lang, video_id), video_id)
        if API_VERSION=='v2':
            player_info=info['data']['attributes']
            vsr=player_info['streams']
            formats=[]
            subtitles={}
            for format_it in vsr:
                format_url=format_it['url']
                format_id=format_it['versions'][0]
                format_id=format_id['eStat']['ml5']
                # overriding buggy language determination
                langf = 'undefined'
                subtitlef = 'undefined'
                versionCode=format_id
                i = 0
                for i, la in enumerate(self.LANGS):
                    trad = self.LANGS[la]
                    # VOX or VX
                    startseek = 1
                    if versionCode[1] == 'O':
                        startseek = 2  # means langf detection is the original language...

                    found = versionCode[startseek:].find(trad)
                    if found == 0:
                        langf = self.TRADS[i]
                        found2 = versionCode[startseek + found + 1:].find(trad)
                        if found2 > 0:
                            if versionCode[startseek + found + found2] == 'M':
                                subtitlef = self.TRADS[i] + ',SUBFORCED'
                    else:
                        if found != -1:
                            subtitlef = self.TRADS[i]
                if format_it['protocol'][:3]=='HLS':
                    dlive, m3u8_formats, subs = self._extract_m3u8_live_and_formats(
                        format_url, video_id, 'mp4',  # entry_protocol='m3u8_native',
                        m3u8_id=format_id, fatal=False)
                    for m3u8_format in m3u8_formats:
                        #m3u8_format['language_preference'] = lang_pref
                        m3u8_format['lang'] = langf
                        m3u8_format['subtitle'] = subtitlef
                        # if m3u8_format[ 'url'] == 'https://arteptweb-vh.akamaihd.net/i/am/ptweb/058000/058400/058451-000-A_0_VF_AMM-PTWEB_XQ.1jI0XFEqDH.smil/master.m3u8':
                        #   i = 0;
                    formats.extend(m3u8_formats)
                    for subk in subs:
                          subtitles[subk]=subs[subk]
                    continue
                # f = dict(format_dict)
                # format_url = url_or_none(f.get('url'))
                # streamer = f.get('streamer')
                # if not format_url and not streamer:
                #     continue
                # versionCode = f.get('versionCode')
                # l = re.escape(langcode)

                # Language preference from most to least priority
                # Reference: section 6.8 of
                # https://www.arte.tv/sites/en/corporate/files/complete-technical-guidelines-arte-geie-v1-07-1.pdf


                # overriding buggy language determination
                langf = 'undefined'
                subtitlef = 'undefined'

                i = 0
                for i, la in enumerate(self.LANGS):
                    trad = self.LANGS[la]
                    # VOX or VX
                    startseek = 1
                    if versionCode[1] == 'O':
                        startseek = 2  # means langf detection is the original language...

                    found = versionCode[startseek:].find(trad)
                    if found == 0:
                        langf = self.TRADS[i]
                        found2 = versionCode[startseek + found + 1:].find(trad)
                        if found2 > 0:
                            if versionCode[startseek + found + found2] == 'M':
                                subtitlef = self.TRADS[i] + ',SUBFORCED'
                    else:
                        if found != -1:
                            subtitlef = self.TRADS[i]

                media_type = f.get('mediaType')
                if media_type == 'hls':
                    m3u8_formats = self._extract_m3u8_formats(
                        format_url, video_id, 'mp4',  # entry_protocol='m3u8_native',
                        m3u8_id=format_id, fatal=False)
                    for m3u8_format in m3u8_formats:
                        m3u8_format['language_preference'] = lang_pref
                        m3u8_format['lang'] = langf
                        m3u8_format['subtitle'] = subtitlef
                        # if m3u8_format[ 'url'] == 'https://arteptweb-vh.akamaihd.net/i/am/ptweb/058000/058400/058451-000-A_0_VF_AMM-PTWEB_XQ.1jI0XFEqDH.smil/master.m3u8':
                        #   i = 0;
                    formats.extend(m3u8_formats)
                    continue

                # format = {
                #     'format_id': format_id,
                #     'preference': -10 if f.get('videoFormat') == 'M3U8' else None,
                #     #'language_preference': lang_pref,
                #     'lang': langf,
                #     'subtitle': subtitlef,
                #     'format_note': '%s, %s' % (f.get('versionCode'), f.get('versionLibelle')),
                #     'width': int_or_none(f.get('width')),
                #     'height': int_or_none(f.get('height')),
                #     'tbr': int_or_none(f.get('bitrate')),
                #     #'quality': qfunc(f.get('quality')),
                # }
                #
                # if media_type == 'rtmp':
                #     format['url'] = f['streamer']
                #     format['play_path'] = 'mp4:' + f['url']
                #     format['ext'] = 'flv'
                # else:
                #     format['url'] = f['url']
                #
                # formats.append(format)

            self._sort_formats(formats)

            metadata = player_info['metadata'];

            return {
                'id': player_info.get('VID') or video_id,
                 'title': metadata['title'],
                 'description': metadata['description'],
                'subtitles':subtitles,
                #'upload_date': unified_strdate(upload_date_str),
                'thumbnail': metadata['images'][0]['url'],#.get('programImage') or player_info.get('VTU', {}).get('IUR'),
                'formats': formats,
            }

        else:
            player_info = info['videoJsonPlayer']
            vsr = try_get(player_info, lambda x: x['VSR'], dict)
            if not vsr:
                error = None
                if try_get(player_info, lambda x: x['custom_msg']['type']) == 'error':
                    error = try_get(
                        player_info, lambda x: x['custom_msg']['msg'], compat_str)
                if not error:
                    error = 'Video %s is not available' % player_info.get('VID') or video_id
                raise ExtractorError(error, expected=True)

            upload_date_str = player_info.get('shootingDate')
            if not upload_date_str:
                upload_date_str = (player_info.get('VRA') or player_info.get('VDA') or '').split(' ')[0]

            title = (player_info.get('VTI') or player_info['VID']).strip()
            subtitle = player_info.get('VSU', '').strip()
            if subtitle:
                title += ' - %s' % subtitle

            qfunc = qualities(['MQ', 'HQ', 'EQ', 'SQ'])



            langcode = self.LANGS.get(lang, lang)
            langind = 0

            formats = []
            for format_id, format_dict in vsr.items():
                f = dict(format_dict)
                format_url = url_or_none(f.get('url'))
                streamer = f.get('streamer')
                if not format_url and not streamer:
                    continue
                versionCode = f.get('versionCode')
                l = re.escape(langcode)

                # Language preference from most to least priority
                # Reference: section 6.8 of
                # https://www.arte.tv/sites/en/corporate/files/complete-technical-guidelines-arte-geie-v1-07-1.pdf
                PREFERENCES = (
                    # original version in requested language, without subtitles
                    r'VO{0}$'.format(l),
                    # original version in requested language, with partial subtitles in requested language
                    r'VO{0}-ST{0}$'.format(l),
                    # original version in requested language, with subtitles for the deaf and hard-of-hearing in requested language
                    r'VO{0}-STM{0}$'.format(l),
                    # non-original (dubbed) version in requested language, without subtitles
                    r'V{0}$'.format(l),
                    # non-original (dubbed) version in requested language, with subtitles partial subtitles in requested language
                    r'V{0}-ST{0}$'.format(l),
                    # non-original (dubbed) version in requested language, with subtitles for the deaf and hard-of-hearing in requested language
                    r'V{0}-STM{0}$'.format(l),
                    # original version in requested language, with partial subtitles in different language
                    r'VO{0}-ST(?!{0}).+?$'.format(l),
                    # original version in requested language, with subtitles for the deaf and hard-of-hearing in different language
                    r'VO{0}-STM(?!{0}).+?$'.format(l),
                    # original version in different language, with partial subtitles in requested language
                    r'VO(?:(?!{0}).+?)?-ST{0}$'.format(l),
                    # original version in different language, with subtitles for the deaf and hard-of-hearing in requested language
                    r'VO(?:(?!{0}).+?)?-STM{0}$'.format(l),
                    # original version in different language, without subtitles
                    r'VO(?:(?!{0}))?$'.format(l),
                    # original version in different language, with partial subtitles in different language
                    r'VO(?:(?!{0}).+?)?-ST(?!{0}).+?$'.format(l),
                    # original version in different language, with subtitles for the deaf and hard-of-hearing in different language
                    r'VO(?:(?!{0}).+?)?-STM(?!{0}).+?$'.format(l),
                )

                for pref, p in enumerate(PREFERENCES):
                    if re.match(p, versionCode):
                        lang_pref = len(PREFERENCES) - pref
                else:
                    lang_pref = -1


                #overriding buggy language determination
                langf='undefined'
                subtitlef='undefined'

                i=0
                for i,la in enumerate(self.LANGS):
                        trad=self.LANGS[la]
                        #VOX or VX
                        startseek=1
                        if versionCode[1]=='O':
                          startseek=2 #means langf detection is the original language...

                        found=versionCode[startseek:].find(trad)
                        if found == 0:
                            langf = self.TRADS[i]
                            found2=versionCode[startseek+found+1:].find(trad)
                            if found2>0:
                               if versionCode[startseek + found +found2]=='M':
                                   subtitlef = self.TRADS[i]+',SUBFORCED'
                        else:
                          if found!=-1:
                            subtitlef = self.TRADS[i]



                media_type = f.get('mediaType')
                if media_type == 'hls':
                    m3u8_formats = self._extract_m3u8_formats(
                        format_url, video_id, 'mp4', # entry_protocol='m3u8_native',
                        m3u8_id=format_id, fatal=False)
                    for m3u8_format in m3u8_formats:
                        #m3u8_format['language_preference'] = lang_pref
                        m3u8_format['lang'] = langf
                        m3u8_format['subtitle'] = subtitlef
                        # if m3u8_format[ 'url'] == 'https://arteptweb-vh.akamaihd.net/i/am/ptweb/058000/058400/058451-000-A_0_VF_AMM-PTWEB_XQ.1jI0XFEqDH.smil/master.m3u8':
                        #   i = 0;
                    formats.extend(m3u8_formats)
                    continue

                format = {
                    'title': title,
                    'format_id': format_id,
                    'preference': -10 if f.get('videoFormat') == 'M3U8' else None,
                    'language_preference': lang_pref,
                    'lang': langf,
                    'subtitle':subtitlef,
                    'format_note': '%s, %s' % (f.get('versionCode'), f.get('versionLibelle')),
                    'width': int_or_none(f.get('width')),
                    'height': int_or_none(f.get('height')),
                    'tbr': int_or_none(f.get('bitrate')),
                    'quality': qfunc(f.get('quality')),
                }

                if media_type == 'rtmp':
                    format['url'] = f['streamer']
                    format['play_path'] = 'mp4:' + f['url']
                    format['ext'] = 'flv'
                else:
                    format['url'] = f['url']

                formats.append(format)

            self._sort_formats(formats)

            return {
                'id': player_info.get('VID') or video_id,
                'title': title,
                'description': player_info.get('VDE'),
                'upload_date': unified_strdate(upload_date_str),
                'thumbnail': player_info.get('programImage') or player_info.get('VTU', {}).get('IUR'),
                'formats': formats,
            }


class ArteTVEmbedIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?arte\.tv/player/v\d+/index\.php\?.*?\bjson_url=.+'
    _TESTS = [{
        'url': 'https://www.arte.tv/player/v5/index.php?json_url=https%3A%2F%2Fapi.arte.tv%2Fapi%2Fplayer%2Fv2%2Fconfig%2Fde%2F100605-013-A&lang=de&autoplay=true&mute=0100605-013-A',
        'info_dict': {
            'id': '100605-013-A',
            'ext': 'mp4',
            'title': 'United we Stream November Lockdown Edition #13',
            'description': 'md5:be40b667f45189632b78c1425c7c2ce1',
            'upload_date': '20201116',
        },
    }, {
        'url': 'https://www.arte.tv/player/v3/index.php?json_url=https://api.arte.tv/api/player/v2/config/de/100605-013-A',
        'only_matching': True,
    }]

    @staticmethod
    def _extract_urls(webpage):
        return [url for _, url in re.findall(
            r'<(?:iframe|script)[^>]+src=(["\'])(?P<url>(?:https?:)?//(?:www\.)?arte\.tv/player/v\d+/index\.php\?.*?\bjson_url=.+?)\1',
            webpage)]

    def _real_extract(self, url):
        qs = compat_urlparse.parse_qs(compat_urlparse.urlparse(url).query)
        json_url = qs['json_url'][0]
        video_id = ArteTVIE._match_id(json_url)
        return self.url_result(
            json_url, ie=ArteTVIE.ie_key(), video_id=video_id)


class ArteTVPlaylistIE(ArteTVBaseIE):
    _VALID_URL = r'https?://(?:www\.)?arte\.tv/(?P<lang>%s)/videos/(?P<id>RC-\d{6})' % ArteTVBaseIE._ARTE_LANGUAGES
    _TESTS = [{
        'url': 'https://www.arte.tv/en/videos/RC-016954/earn-a-living/',
        'info_dict': {
            'id': 'RC-016954',
            'title': 'Earn a Living',
            'description': 'md5:d322c55011514b3a7241f7fb80d494c2',
        },
        'playlist_mincount': 6,
    }, {
        'url': 'https://www.arte.tv/pl/videos/RC-014123/arte-reportage/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        lang, playlist_id = re.match(self._VALID_URL, url).groups()
        collection = self._download_json(
            '%s/collectionData/%s/%s?source=videos'
            % (self._API_BASE, lang, playlist_id), playlist_id)
        entries = []
        for video in collection['videos']:
            if not isinstance(video, dict):
                continue
            video_url = url_or_none(video.get('url')) or url_or_none(video.get('jsonUrl'))
            if not video_url:
                continue
            video_id = video.get('programId')
            entries.append({
                '_type': 'url_transparent',
                'url': video_url,
                'id': video_id,
                'title': video.get('title'),
                'alt_title': video.get('subtitle'),
                'thumbnail': url_or_none(try_get(video, lambda x: x['mainImage']['url'], compat_str)),
                'duration': int_or_none(video.get('durationSeconds')),
                'view_count': int_or_none(video.get('views')),
                'ie_key': ArteTVIE.ie_key(),
            })
        title = collection.get('title')
        description = collection.get('shortDescription') or collection.get('teaserText')
        return self.playlist_result(entries, playlist_id, title, description)


class ArteTVCategoryIE(ArteTVBaseIE):
    _VALID_URL = r'https?://(?:www\.)?arte\.tv/(?P<lang>%s)/videos/(?P<id>[\w-]+(?:/[\w-]+)*)/?\s*$' % ArteTVBaseIE._ARTE_LANGUAGES
    _TESTS = [{
        'url': 'https://www.arte.tv/en/videos/politics-and-society/',
        'info_dict': {
            'id': 'politics-and-society',
            'title': 'Politics and society',
            'description': 'Investigative documentary series, geopolitical analysis, and international commentary',
        },
        'playlist_mincount': 13,
    },
    ]

    @classmethod
    def suitable(cls, url):
        return (
            not any(ie.suitable(url) for ie in (ArteTVIE, ArteTVPlaylistIE, ))
            and super(ArteTVCategoryIE, cls).suitable(url))

    def _real_extract(self, url):
        lang, playlist_id = re.match(self._VALID_URL, url).groups()
        webpage = self._download_webpage(url, playlist_id)

        items = []
        for video in re.finditer(
                r'<a\b[^>]*?href\s*=\s*(?P<q>"|\'|\b)(?P<url>https?://www\.arte\.tv/%s/videos/[\w/-]+)(?P=q)' % lang,
                webpage):
            video = video.group('url')
            if video == url:
                continue
            if any(ie.suitable(video) for ie in (ArteTVIE, ArteTVPlaylistIE, )):
                items.append(video)

        if items:
            title = (self._og_search_title(webpage, default=None)
                     or self._html_search_regex(r'<title\b[^>]*>([^<]+)</title>', default=None))
            title = strip_or_none(title.rsplit('|', 1)[0]) or self._generic_title(url)

            result = self.playlist_from_matches(items, playlist_id=playlist_id, playlist_title=title)
            if result:
                description = self._og_search_description(webpage, default=None)
                if description:
                    result['description'] = description
                return result
