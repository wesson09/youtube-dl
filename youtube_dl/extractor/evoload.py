# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    try_get,
    ExtractorError,
    urlencode_postdata,
    sanitized_Request,
    std_headers,
)

class EvoLoadIE(InfoExtractor):
    IE_NAME = 'evoload'
    # https://evoload.io/v/58AtgpYn5tAKEp
    _VALID_URL = r'https?://evoload\.io/[ev]/(?P<id>[a-zA-Z0-9]+)/?'
    _TEST = {}
    TITLE_RE = (
        r'<h3\s+class="kt-subheader__title">\s*(.+)\s*</h3>',
        r'<title>(?:Evoload|EvoLOAD.io) - Play\s(.+)\s*</title>'
    )
    VIDEO_URL = 'https://evoload.io/v/%s/'
    EMBED_URL = 'https://evoload.io/e/%s/'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage_video = self._download_webpage(self.VIDEO_URL % video_id, video_id, note='Downloading video page')
        webpage_embed = self._download_webpage(self.EMBED_URL % video_id, video_id, note='Downloading embed page')

        mob=re.findall('<div id="captcha_pass" value="(?P<id>[^"]+)"><\/div>',webpage_embed);
        cappass=mob[0];
        login_form = {"code":video_id,
                      "token":"ok",
                      "pass":cappass,
                      #"reff":"https://www.sepiaradiance.com/"
                       }
        request = sanitized_Request('https://evoload.io/SecurePlayer', urlencode_postdata(login_form))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        mobj = self._download_json(request, None,headers=std_headers)

        # if not mobj['allow_download']:
        #     raise ExtractorError('Evoload: Forbidden download')

        format = {
            'format_id': 'single',
            'url': mobj['stream']['src'],
            'ext': 'mp4',
            'size': mobj['size'],
        }
        formats=[]
        formats.append(format)
        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': mobj['name'],
            'thumbnail': mobj['cdn']['thumb'],
            'formats': formats,
        }
