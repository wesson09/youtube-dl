# coding: utf-8


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
)

from youtube_dl.aes import aes_decrypt, aes_encrypt, aes_cbc_decrypt, aes_cbc_encrypt, aes_decrypt_text
from youtube_dl.utils import bytes_to_intlist, intlist_to_bytes
import base64


from youtube_dl.compat import (
  compat_urllib_request
)
class KavimoIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?onlineacademy\.ir(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'https://onlineacademy.ir/teacher/استاد-حسین-دلدار/',
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
        #   s.hex2buf = function (e) {
        #     return new Uint8Array(e.match(/.{2}/g).map(function (e) {
        #       return parseInt(e, 16)
        #     }))
        #   },
        #   s.buf2str = function (e) {
        #     return new TextDecoder('utf-8').decode(e)
        #   },
        #   s.str2buf = function (e) {
        #     return new TextEncoder('utf-8').encode(e)
        #   },
        #   s.deriveKey = function (e, t) {
        #     return t = t || crypto.getRandomValues(new Uint8Array(8)),
        #     crypto.subtle.importKey('raw', this.str2buf(e), 'PBKDF2', !1, [
        #       'deriveKey'
        #     ]).then(function (e) {
        #       return crypto.subtle.deriveKey({
        #         name: 'PBKDF2',
        #         salt: t,
        #         iterations: 1000,
        #         hash: 'SHA-256'
        #       }, e, {
        #         name: 'AES-GCM',
        #         length: 256
        #       }, !1, [
        #         'encrypt',
        #         'decrypt'
        #       ])
        #     }).then(function (e) {
        #       return [e,
        #       t]
        #     })
        #   },
        #   s.AESDECRYPT_BY_PASSPHARE = function (e, t) {
        #     var i = this,
        #     r = t.split('-').map(this.hex2buf),
        #     a = r[1],
        #     n = r[2],
        #     s = r[0];
        #     return this.deriveKey(e, s).then(function (e) {
        #       var t = e[0];
        #       return crypto.subtle.decrypt({
        #         name: 'AES-GCM',
        #         iv: a
        #       }, t, n)
        #     }).then(function (e) {
        #       return i.buf2str(new Uint8Array(e))
        #     })
        #   },
        #   s.loadsuccess = function (e, t, i, r) {
        #     void 0 === r && (r = null);
        #     var a = this;
        #     if (i.isSidxRequest) return this._handleSidxRequest(e, i),
        #     void this._handlePlaylistLoaded(e, t, i, r);
        #     if (this.resetInternalLoader(i.type), 'string' != typeof e.data) throw new Error('expected responseType of "text" for PlaylistLoader');
        #     var n = window.Vis.Vendor.Base64.decode(e.data);
        #     if (t.tload = x.now(), '' != n) {
        #       var s = n.split('-') [0],
        #       o = window['msgn-' + s];
        #       n = n.replace(s + '-', ''),
        #       this.AESDECRYPT_BY_PASSPHARE(o + s, n).then(function (n) {
        #         e.data = n,
        #         e.data.indexOf('#EXTINF:') > 0 || e.data.indexOf('#EXT-X-TARGETDURATION:') > 0 ? a._handleTrackOrLevelPlaylist(e, t, i, r) : a._handleMasterPlaylist(e, t, i, r)
        #       })
        #     }
        #   },
        encrypted=r'''13c3e374224932ec-43eef39e9cf5f0d66bb1ae42-0facbae7fa9c80e32c03d3c7b8303c63bab8cd6162b69fc7da4a7a45b24555bf311f3ed1b47ac58162527f623060da76c06e6705e71248a0d733051189a7bf3702536bb41d836f7c46f22f83e58fe355e804689b5998c65cf68cca874c1623047a1b4c726d0481474f94501a7d9c4403ccfd8e69cf2e72aaeeb52172cdcf747a82762a30ae5e03d190b7316e4d6c65a2b98fc55259cc6fc5cc9704f9e8e65d04a87c503f417db518a85d5beeb227e05c77ce36ce6553321d647c32b0a33058e62070f5c07d2da69c5cdd710f0e3861e7f78fcc7f48be408b544520eb84343dc7330948e554d979eb8258d62c7af06f16bd29414804f22122898efa2edcd77effdb6f3ad3958a832d60a1be106f6b8ce55856af78bf4fd2c9c6005c7cfb1b927eafefeb7bbb924d138b8e73674f444f1f8e84f5353e31c6be5af1e9bf23c3d922247ed2d28256bef88b81150fbd8039f3641afea2dfb3c4b731d9f8e70a7e68be0b53518ff2cf8713f1fd2891c1972c1fa8adca48e711ad42a7e7339852ed19bacc9a176c92390b0be6aeb7f6d5e909280cf9e8e684cc7b62097ed775d0ab3985ba30c37d8657b96a6d0aa8b6c0d9933eefd2016695394f6630abe10e646d6e2fe3eaeb80f5707fd260ed9706eaac778319e5c4137e4cddb7df03423322539a6aee33663687b66b7382469ddee0b51131221e1d77caada97bfcefe4eb18e27a57887a0e28d96a474a1ec168233382b9912bb5d1b22e7e4bdb1524393b9b5a60080babb9937beb4c1e6edc642104a73e58aa75c640cf'''
        #encrypted=encrypted.replace('-','')
        encrypted=bytes(encrypted, 'utf-8')
        key='Wd1RBQSh8jxAEF994JjShiFNscq7GXz9qsoikj89yaup'
        key = bytes(key, 'utf-8')
        print(aes_decrypt(encrypted, key))

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
                data=bytes('referrer=http://tvhai.org&typeend=html', 'utf-8'), headers=   headers , fatal=False)


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


