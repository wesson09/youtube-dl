from .common import InfoExtractor
from .vk import VKIE
from ..compat import compat_b64decode
from ..utils import (
    int_or_none,
    js_to_json,
    traverse_obj,
    unified_timestamp,
std_headers
)
import urllib3
import urllib.request

class BIQLEIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?biqle\.(?:com|org|ru)/watch/(?P<id>-?\d+_\d+)'
    _TESTS = [{
        'url': 'https://biqle.ru/watch/-2000421746_85421746',
        'md5': 'ae6ef4f04d19ac84e4658046d02c151c',
        'info_dict': {
            'id': '-2000421746_85421746',
            'ext': 'mp4',
            'title': 'Forsaken By Hope Studio Clip',
            'description': 'Forsaken By Hope Studio Clip — Смотреть онлайн',
            'upload_date': '19700101',
            'thumbnail': r're:https://[^/]+/impf/7vN3ACwSTgChP96OdOfzFjUCzFR6ZglDQgWsIw/KPaACiVJJxM\.jpg\?size=800x450&quality=96&keep_aspect_ratio=1&background=000000&sign=b48ea459c4d33dbcba5e26d63574b1cb&type=video_thumb',
            'timestamp': 0,
        },
    }, {
        'url': 'http://biqle.org/watch/-44781847_168547604',
        'md5': '7f24e72af1db0edf7c1aaba513174f97',
        'info_dict': {
            'id': '-44781847_168547604',
            'ext': 'mp4',
            'title': 'Ребенок в шоке от автоматической мойки',
            'description': 'Ребенок в шоке от автоматической мойки — Смотреть онлайн',
            'timestamp': 1396633454,
            'upload_date': '20140404',
            'thumbnail': r're:https://[^/]+/c535507/u190034692/video/l_b84df002\.jpg',
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        std_headers={}
        return self.url_result('https://vk.com/video'+video_id, VKIE.ie_key(), video_id)

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_meta('name', webpage, 'Title', fatal=False)
        timestamp = unified_timestamp(self._html_search_meta('uploadDate', webpage, 'Upload Date', default=None))
        description = self._html_search_meta('description', webpage, 'Description', default=None)

        global_embed_url = self._search_regex(
            r'<script[^<]+?window.globEmbedUrl\s*=\s*\'((?:https?:)?//(?:daxab\.com|dxb\.to|[^/]+/player)/[^\']+)\'',
            webpage, 'global Embed url')
        hash = self._search_regex(
            r'<script id="data-embed-video[^<]+?hash: "([^"]+)"[^<]*</script>', webpage, 'Hash')

        embed_url = global_embed_url + hash
        #embed_url ='https://daxab.com/player/jHxmSC-NCAR3a6bE3Lnoo56lKQ_vtESRLVgHiUJrCJD-dbnhH-ygZt3cTMfBtNa2BGY_xtGan0ep3PNe_6X2WcJeBz9LKww1Fjymrqr8gW4'
        if VKIE.suitable(embed_url):
            return self.url_result(embed_url, VKIE.ie_key(), video_id)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            # 'Accept-Encoding':'gzip, deflate',
            'Referer': 'https://biqle.ru/',

            'Connection': 'keep_alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        # request = urllib.request.Request(embed_url, None, headers)
        # http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        # embed_page = http.request('GET', request.full_url, headers=headers, preload_content=True).data
        embed_page = self._download_webpage(
            embed_url, video_id, 'Downloading embed webpage', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
          # 'Accept-Encoding':'gzip, deflate',
                'Referer': 'https://biqle.ru/',

                'Connection': 'keep_alive',
                                                                       'Upgrade-Insecure-Requests':'1',
                                                                       'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
                                                                       })#url})

        glob_params = self._parse_json(self._search_regex(
            r'<script id="globParams">[^<]*window.globParams = ([^;]+);[^<]+</script>',
            embed_page, 'Global Parameters'), video_id, transform_source=js_to_json)
        host_name = compat_b64decode(glob_params['server'][::-1]).decode()

        items = self._download_json(
            f'https://{host_name}/method/video.get/{video_id}', video_id,
            headers={'Referer': url}, query={
                'token': glob_params['video']['access_token'],
                'videos': video_id,
                'ckey': glob_params['c_key'],
                'credentials': glob_params['video']['credentials'],
            })
        item=items['response']['items'][0]
        formats = []
        for f_id, f_url in item.get('files', {}).items():
            if f_id == 'external':
                return self.url_result(f_url)
            ext, height = f_id.split('_')
            height_extra_key = traverse_obj(glob_params, ('video', 'partial', 'quality', height))
            if height_extra_key:
                formats.append({
                    'format_id': f'{height}p',
                    'url': f'https://{host_name}/{f_url[8:]}&videos={video_id}&extra_key={height_extra_key}',
                    'height': int_or_none(height),
                    'ext': ext,
                    'http_headers':std_headers
                })
        self._sort_formats(formats)

        thumbnails = []
        for k, v in item.items():
            if k.startswith('photo_') and v:
                width = k.replace('photo_', '')
                thumbnails.append({
                    'id': width,
                    'url': v,
                    'width': int_or_none(width),
                })

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'comment_count': int_or_none(item.get('comments')),
            'description': description,
            'duration': int_or_none(item.get('duration')),
            'thumbnails': thumbnails,
            'timestamp': timestamp,
            'view_count': int_or_none(item.get('views')),
            'http_headers':std_headers
        }