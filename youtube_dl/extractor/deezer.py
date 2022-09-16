

from __future__ import unicode_literals

import json

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
    orderedSet,
urlencode_postdata,
    std_headers
)

#todo track navigation with https://www.deezer.com/ajax/gw-light.php?method=log.listen post parameters (for individual download)
class DeezerBaseInfoExtractor(InfoExtractor):
    def get_data(self, url):
        #if not self.get_param('test'):
        #self.report_warning('For now, this extractor only supports the 30 second previews. Patches welcome!')

        mobj = self._match_valid_url(url)
        data_id = mobj.group('id')

        webpage = self._download_webpage(url, data_id,headers=std_headers)
        geoblocking_msg = self._html_search_regex(
            r'<p class="soon-txt">(.*?)</p>', webpage, 'geoblocking message',
            default=None)
        if geoblocking_msg is not None:
            raise ExtractorError(
                'Deezer said: %s' % geoblocking_msg, expected=True)

        data_json = self._search_regex(
            (r'__DZR_APP_STATE__\s*=\s*({.+?})\s*</script>',
             r'naboo\.display\(\'[^\']+\',\s*(.*?)\);\n'),
            webpage, 'data JSON')
        data = json.loads(data_json)
        return data_id, webpage, data

    def getUserInfo(self):
        sid='fr12345_______________________________89'
        if std_headers.get('Cookie'):
                heads=std_headers['Cookie'].split(';')#todo parse better
                headdict={}
                for h in heads:
                    s=h.find('=');
                    headdict[ h[0:s].strip()]=h[s+1:]
                if headdict.get('sid') :
                    sid=headdict.get('sid')
        return self._download_json(
            'https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token=',
            None, 'Logging in',
            headers={
                'coookie': 'sid='+sid,
            })
    def getTracksUrls(self,userinfo,straktids):

        traktids=','.join(straktids)
        songsinfo = self._download_json(
            'https://www.deezer.com/ajax/gw-light.php?method=song.getListData&input=3&api_version=1.0&api_token=' +
            userinfo['results']['checkForm'], None, 'get song info',
            data=json.dumps((json.loads('{"sng_ids":[' + traktids + ']}'))).encode(),
            headers={
                'coookie': 'sid=fr12345_______________________________89',
            })
        traktokens = []
        for s in songsinfo['results']["data"]:
            traktokens.append('"'+s['TRACK_TOKEN']+'"');
        traktokens = ','.join(traktokens)
        datasong = '{"license_token":"' + userinfo['results']["USER"]["OPTIONS"]['license_token'] \
                   + '","media":[{"type":"FULL","formats":[{"cipher":"BF_CBC_STRIPE","format":"MP3_128"},{"cipher":"BF_CBC_STRIPE","format":"FLAC"}]}],"track_tokens":[' + traktokens + ']}';
        urlinfo = self._download_json(
            'https://media.deezer.com/v1/get_url',
            None, 'get urls',
            data=json.dumps((json.loads(datasong))).encode(),
        )
        return  [songsinfo,urlinfo]

class DeezerTitleIE(DeezerBaseInfoExtractor):
    _VALID_URL = r'vso://dzr:(?P<id>[0-9]+)'

    def _real_extract(self, url):
        titleid = self._match_id(url)
        # 1 - User info
        userinfo = self.getUserInfo()
        [songsinfo,urlinfo]=self.getTracksUrls(userinfo, [titleid])
        if not urlinfo['data'][0].get('media'):
            raise ExtractorError (songsinfo['data'][0].get('SNG_TITLE')+' not enough right to download')
            return {}

        s = songsinfo['results']['data'][0]
        artists = s['ARTISTS'][0].get('ART_NAME')

        formats = []
        for formit in urlinfo['data'][0]['media']:
            formats.append({
                'format_id': formit['format'],
                'url': formit['sources'][0]['url'],
                'ext': 'mp3',
                # 'headers':std_headers
            })

        return{
            'id': titleid,'dzrdecode':titleid,
            'duration': int_or_none(s.get('DURATION')),
            'fulltitle': '%s - %s %s' % (artists, s.get('ALB_TITLE'), s.get('SNG_TITLE')),
            'title': '%s - %s %s' % (artists, s.get('ALB_TITLE'), s.get('SNG_TITLE')),
            'uploader': s.get('ART_NAME'),
            'uploader_id': s.get('ART_ID'),
            'age_limit': 16 if s.get('EXPLICIT_LYRICS') == '1' else 0,
            'formats': formats,
            #'headers': std_headers
        }

    # Deleting (Calling destructor)
    def __del__(self):
        print('Destructor called, extractor deleted.')


class DeezerPlaylistIE(DeezerBaseInfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?deezer\.com/(../)?playlist/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.deezer.com/playlist/176747451',
        'info_dict': {
            'id': '176747451',
            'title': 'Best!',
            'uploader': 'anonymous',
            'thumbnail': r're:^https?://(e-)?cdns-images\.dzcdn\.net/images/cover/.*\.jpg$',
        },
        'playlist_count': 29,
    }
    def _real_extract(self, url):
        playlist_id, webpage, data = self.get_data(url)
        # 1 - User info
        # userinfo=self._download_json(
        #     'https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token=', None, 'Logging in',
        #     # data=urlencode_postdata(data),
        #     headers={
        #         'coookie': 'sid=fr12345_______________________________89',
        #     })
        playlist_title = data.get('DATA', {}).get('TITLE')
        playlist_uploader = data.get('DATA', {}).get('PARENT_USERNAME')
        playlist_thumbnail = self._search_regex(
            r'<img id="naboo_playlist_image".*?src="([^"]+)"', webpage,
            'playlist thumbnail')

        entries = []
        songs=data.get('SONGS', {}).get('data');
        trackids=[]
        for s in songs:
            trackids.append(s['SNG_ID']);
        #[songsinfo,urlinfo]=self.getTracksUrls(userinfo, trackids)
        cpt=0;
        for s in songs:
            # 2a - Track to Tokens TODO: get all songs meta at a time
            # traktids='["'+s['SNG_ID']+'"]'
            # self.to_screen(urlencode_postdata(json.loads('{"sng_ids":'+traktids+'}')))
            #


            # songinfo.TRACK_TOKEN
            # userinfo.USER.OPTIONS.license_token
            # {license_token: lictoken, media: [{type: "FULL", formats: [{cipher: "BF_CBC_STRIPE", format: "MP3_128"}]}],
            #  track_tokens: [track_tok]};

            # if not urlinfo['data'][cpt].get('media'):
            #     self.report_warning(s.get('SNG_TITLE'))
            #     cpt=cpt+1;
            #     continue
            #
            # formats = [{
            #     'format_id': urlinfo['data'][cpt]['media'][0]['format'],
            #     'url': urlinfo['data'][cpt]['media'][0]['sources'][0]['url'],# s.get('MEDIA', [{}])[0].get('HREF'),
            #     'preference': -100,  # Only the first 30 seconds
            #     'ext': 'mp3',
            #     # 'headers':std_headers
            # }]
            # self._sort_formats(formats)
            artists = ', '.join(
                orderedSet(a.get('ART_NAME') for a in s.get('ARTISTS')))

            entries.append( {
                            '_type': 'url',
                            'id':s.get('SNG_ID'),
                            'ie_key': DeezerTitleIE.ie_key(),
                            'url':'vso://dzr:%s' % ( s.get('SNG_ID')),
                            'duration': int_or_none(s.get('DURATION')),
                            'title':'%s - %s - %s' % (artists, s.get('ALB_TITLE'), s.get('SNG_TITLE')),
                            'uploader': s.get('ART_NAME'),
                            'uploader_id': s.get('ART_ID'),
                            'headers':std_headers,
                            })
            # entries.append({
            #     'ie_key': ie
            #     'id': s.get('SNG_ID'),
            #     'duration': int_or_none(s.get('DURATION')),
            #     'title': '%s - %s' % (artists, s.get('SNG_TITLE')),
            #     'uploader': s.get('ART_NAME'),
            #     'uploader_id': s.get('ART_ID'),
            #     'age_limit': 16 if s.get('EXPLICIT_LYRICS') == '1' else 0,
            #     'formats': formats,
            #     'headers':std_headers
            # })
            cpt =cpt+1

        return {
            '_type': 'playlist',
            'id': playlist_id,
            'title': playlist_title,
            'uploader': playlist_uploader,
            'thumbnail': playlist_thumbnail,
            'entries': entries,
        }


class DeezerAlbumIE(DeezerBaseInfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?deezer\.com/(../)?album/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'https://www.deezer.com/fr/album/67505622',
        'info_dict': {
            'id': '67505622',
            'title': 'Last Week',
            'uploader': 'Home Brew',
            'thumbnail': r're:^https?://(e-)?cdns-images\.dzcdn\.net/images/cover/.*\.jpg$',
        },
        'playlist_count': 7,
    }

    def _real_extract(self, url):
        album_id, webpage, data = self.get_data(url)

        album_title = data.get('DATA', {}).get('ALB_TITLE')
        album_uploader = data.get('DATA', {}).get('ART_NAME')
        album_thumbnail = self._search_regex(
            r'<img id="naboo_album_image".*?src="([^"]+)"', webpage,
            'album thumbnail')

        entries = []
        for s in data.get('SONGS', {}).get('data'):
            formats = [{
                'format_id': 'preview',
                'url': s.get('MEDIA', [{}])[0].get('HREF'),
                'preference': -100,  # Only the first 30 seconds
                'ext': 'mp3',
            }]
            self._sort_formats(formats)
            artists = ', '.join(
                orderedSet(a.get('ART_NAME') for a in s.get('ARTISTS')))

            entries.append( {
                            '_type': 'url',
                            'id':s.get('SNG_ID'),
                            'ie_key': DeezerTitleIE.ie_key(),
                            'url':'vso://dzr:%s' % ( s.get('SNG_ID')),
                            'duration': int_or_none(s.get('DURATION')),
                            'title':'%s - %s - %s' % (artists, s.get('ALB_TITLE'), s.get('SNG_TITLE')),
                            'uploader': s.get('ART_NAME'),
                            'uploader_id': s.get('ART_ID'),
                            'headers':std_headers,
                            })
            # entries.append({
            #     'id': s.get('SNG_ID'),
            #     'duration': int_or_none(s.get('DURATION')),
            #     'title': '%s - %s' % (artists, s.get('SNG_TITLE')),
            #     'uploader': s.get('ART_NAME'),
            #     'uploader_id': s.get('ART_ID'),
            #     'age_limit': 16 if s.get('EXPLICIT_LYRICS') == '1' else 0,
            #     'formats': formats,
            #     'track': s.get('SNG_TITLE'),
            #     'track_number': int_or_none(s.get('TRACK_NUMBER')),
            #     'track_id': s.get('SNG_ID'),
            #     'artist': album_uploader,
            #     'album': album_title,
            #     'album_artist': album_uploader,
            # })

        return {
            '_type': 'playlist',
            'id': album_id,
            'title': album_title,
            'uploader': album_uploader,
            'thumbnail': album_thumbnail,
            'entries': entries,
        }
