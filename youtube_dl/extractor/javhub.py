# coding: utf-8
from __future__ import unicode_literals

import re
#from https://gitea.com/nao20010128nao/ytdl-patched/src/branch/ytdlp/yt_dlp
from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    determine_ext,
    intlist_to_bytes
)
def decode_base(value, digits):
    # This will convert given base-x string to scalar (long or int)
    table = {char: index for index, char in enumerate(digits)}
    result = 0
    base = len(digits)
    for chr in value:
        result *= base
        result += table[chr]
    return result


def scalar_to_bytes(scalar):
    if not scalar:
        return b''
    array = []
    while scalar:
        scalar, idx = divmod(scalar, 256)
        array.insert(0, idx)
    return intlist_to_bytes(array)


def encode_base(scalar, digits):
    # This will convert scalar (long or int) to base-x string
    if not scalar:
        return ''
    base = len(digits)
    result = ''
    while scalar:
        scalar, idx = divmod(scalar, base)
        result = digits[idx] + result
    return result


def char_replace(base, replace, string):
    # character-by-character replacing
    if not string:
        return ''
    assert len(base) == len(replace)
    table = {b: r for b, r in zip(base, replace) if b != r}
    if not table:
        return string
    result = ''
    for i in string:
        result += table.get(i, i)
    return result

class JavhubIE(InfoExtractor):
    IE_NAME = 'javhub'
    _VALID_URL = r'https?://(?:ja\.)?javhub\.net/play/(?P<id>[^/]+)'

    B58_TABLE_1 = '23456789ABCDEFGHJKLNMPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz1'
    B58_TABLE_2 = '789ABCDEFGHJKLNMPQRSTUVWX23456YZabcdefghijkmnopqrstuvwxyz1'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        data_src = self._search_regex(r'data-src="([^\"]+)"(?:>| data-track)', webpage, 'data-src')

        playapi_post = char_replace(self.B58_TABLE_2, self.B58_TABLE_1, data_src).encode('utf8')

        playapi_response = self._download_json(
            'https://ja.javhub.net/playapi', video_id,
            data=b'data=%s' % playapi_post, headers={'Referer': url})
        mp4_url = playapi_response.get('playurl')
        if not mp4_url:
            raise ExtractorError('Server returned invalid data')
        mp4_url = scalar_to_bytes(decode_base(mp4_url, self.B58_TABLE_2)).decode('utf8')

        result = self._search_json_ld(webpage, video_id)
        title = self._search_regex(r'<h5[^>]+?>(.+)</h5>', webpage, 'title', default=None)
        if not title and result.get('title'):
            title = result['title']
        if not title:
            title = self._html_extract_title(webpage, 'html title', default=None, fatal=False)

        if title:
            title = re.sub(r'^(?:無料動画|Watch Free Jav)\s+', '', title)

        result.update({
            'id': video_id,
            'title': title,
            'formats': [{
                'url': mp4_url,
                'protocol': 'http',
                'ext': determine_ext(mp4_url),
                'http_headers': {
                    'Referer': url,
                },
            }],
            'age_limit': 18,
        })
        return result
