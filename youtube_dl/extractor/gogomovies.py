# coding: utf-8
from __future__ import unicode_literals

import time
import http.client
import json
import re
from typing import *
from urllib import parse
from ssl import SSLSocket

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
    try_get,
)

from  ..http3_client import (HttpClient,HttpRequest,HttpConnection);
import socket
import ssl

import asyncio

import aioquic
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h0.connection import H0_ALPN, H0Connection
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import (
    DataReceived,
    H3Event,
    HeadersReceived,
    PushPromiseReceived,
)
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.connection import QuicConnection;
from aioquic.quic.events import QuicEvent
from aioquic.tls import CipherSuite, SessionTicket
#import M2Crypto
#import OpenSSL
async def runhttp3request(
        configuration: QuicConfiguration,
        urls: List[str],
        data: Optional[str],
        include: bool,
      #  output_dir: Optional[str],
        local_port: int,
        zero_rtt: bool,
) -> str:
    # parse URL
    parsed = parse.urlparse(urls[0])
    assert parsed.scheme in (
        "https",
        "wss",
    ), "Only https:// or wss:// URLs are supported."
    host = parsed.hostname
    if parsed.port is not None:
        port = parsed.port
    else:
        port = 443

    async with connect(
            host,
            port,
            configuration=configuration,
            create_protocol=HttpClient,
            session_ticket_handler=None,#save_session_ticket,
            local_port=local_port,
            wait_connected=not zero_rtt,
    ) as client:
        client = cast(HttpClient, client)

        if parsed.scheme == "wss":
            ws = await client.websocket(urls[0], subprotocols=["chat", "superchat"])

            # send some messages and receive reply
            for i in range(2):
                message = "Hello {}, WebSocket!".format(i)
                print("> " + message)
                await ws.send(message)

                message = await ws.recv()
                print("< " + message)

            await ws.close()
        else:
            # perform request
            coros = [
                perform_http_request(
                    client=client,
                    url=url,
                    data=data,
                    include=include,
                    #output_dir=output_dir,
                )
                for url in urls
            ]


            res=await asyncio.gather(*coros)


            # process http pushes
            process_http_pushess(client=client, include=include)

            return res

async def perform_http_request(
    client: HttpClient,
    url: str,
    data: Optional[str],
    include: bool,
    #output_dir: Optional[str],
) -> str:
    # perform request
    start = time.time()
    if data is not None:
        http_events = await client.post(
            url,
            data=data.encode(),
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        method = "POST"
    else:
        http_events = await client.get(url)
        method = "GET"
    elapsed = time.time() - start

    # print speed
    octets = 0
    http3client="";
    for http_event in http_events:
        if isinstance(http_event, DataReceived):
            octets += len(http_event.data)
    print(
        "Response received for %s %s : %d bytes in %.1f s (%.3f Mbps)"
        % (method, parse.urlparse(url).path, octets, elapsed, octets * 8 / elapsed / 1000000)
    )

    for http_event in http_events:
        if isinstance(http_event, HeadersReceived) and include:
            headers = b""
            for k, v in http_event.headers:
                headers += k + b": " + v + b"\r\n"
            if headers:
                print(headers + b"\r\n")
        elif isinstance(http_event, DataReceived):
            http3client=http3client + http_event.data.decode('utf-8')
    # output response
    # if output_dir is not None:
    #     output_path = os.path.join(
    #         output_dir, os.path.basename(urlparse(url).path) or "index.html"
    #     )
    #     with open(output_path, "wb") as output_file:
    #         write_response(
    #             http_events=http_events, include=include, output_file=output_file
    #         )
    return http3client;


def process_http_pushess(
    client: HttpClient,
    include: bool,
    #output_dir: Optional[str],
) -> None:
    for _, http_events in client.pushes.items():
        method = ""
        octets = 0
        path = ""
        for http_event in http_events:
            if isinstance(http_event, DataReceived):
                octets += len(http_event.data)
            elif isinstance(http_event, PushPromiseReceived):
                for header, value in http_event.headers:
                    if header == b":method":
                        method = value.decode()
                    elif header == b":path":
                        path = value.decode()
        print("Push received for %s %s : %s bytes", method, path, octets)

        # output response
        # if output_dir is not None:
        #     output_path = os.path.join(
        #         output_dir, os.path.basename(path) or "index.html"
        #     )
        #     with open(output_path, "wb") as output_file:
        #         write_response(
        #             http_events=http_events, include=include, output_file=output_file
        #         )


class GogomoviesIE(InfoExtractor):#TurnerBaseIE):
    _VALID_URL = r'https?://(?:www\.)?voircartoon\.com(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'https://voircartoon.com/episode/paw-patrol-la-patpatrouille-saison-7-vf-episode-25/',
        'info_dict': {
            'id': 'rQxZvXQ4ROaSOqq-or2Mow',
            'ext': 'mp4',
            'title': 'Rick and Morty - Pilot',
            'description': 'Rick moves in with his daughter\'s family and establishes himself as a bad influence on his grandson, Morty.',
            'timestamp': 1543294800,
            'upload_date': '20181127',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Unable to download f4m manifest'],
    }, {
        'url': 'http://www.adultswim.com/videos/tim-and-eric-awesome-show-great-job/dr-steve-brule-for-your-wine/',
        'info_dict': {
            'id': 'sY3cMUR_TbuE4YmdjzbIcQ',
            'ext': 'mp4',
            'title': 'Tim and Eric Awesome Show Great Job! - Dr. Steve Brule, For Your Wine',
            'description': 'Dr. Brule reports live from Wine Country with a special report on wines.  \nWatch Tim and Eric Awesome Show Great Job! episode #20, "Embarrassed" on Adult Swim.',
            'upload_date': '20080124',
            'timestamp': 1201150800,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': '404 Not Found',
    }, {
        'url': 'http://www.adultswim.com/videos/decker/inside-decker-a-new-hero/',
        'info_dict': {
            'id': 'I0LQFQkaSUaFp8PnAWHhoQ',
            'ext': 'mp4',
            'title': 'Decker - Inside Decker: A New Hero',
            'description': 'The guys recap the conclusion of the season. They announce a new hero, take a peek into the Victorville Film Archive and welcome back the talented James Dean.',
            'timestamp': 1469480460,
            'upload_date': '20160725',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Unable to download f4m manifest'],
    }, {
        'url': 'http://www.adultswim.com/videos/attack-on-titan',
        'info_dict': {
            'id': 'attack-on-titan',
            'title': 'Attack on Titan',
            'description': 'md5:41caa9416906d90711e31dc00cb7db7e',
        },
        'playlist_mincount': 12,
    }, {
        'url': 'http://www.adultswim.com/videos/streams/williams-stream',
        'info_dict': {
            'id': 'd8DEBj7QRfetLsRgFnGEyg',
            'ext': 'mp4',
            'title': r're:^Williams Stream \d{4}-\d{2}-\d{2} \d{2}:\d{2}$',
            'description': 'original programming',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': '404 Not Found',
    }]


    def _real_extract(self, url):
        show_path = re.match(self._VALID_URL, url).groups()[2]
        #print(show_path);



        webpage=self._download_webpage(url,show_path);
        #print(webpage);
        propvalpattern = '<\s*meta\s+property\s*=\s*\"og:(?P<prop>[\w^\"]+)\"\s+content\s*=\s*\"(?P<value>[\w\W]|[^\"]*)\"\s*\/\s*>'
        matches = re.finditer(
            propvalpattern,
            webpage)
        ogtitle = '';
        ogdescription = '';
        ogdate='';
        oglocale='';
        for m in matches:
            if m.group(1) == 'title':
                ogtitle = m.group(2);
            elif m.group(1) == 'description':
                ogdescription = m.group(2);
            elif m.group(1) == 'updated_time':
                ogdate = m.group(2);
            elif m.group(1) == 'locale':
                oglocale = m.group(2);

        #data-id = '19960'
        video_urls = re.findall(
            r'data\-id\=[\"\'](?P<id>[^\"]|.+?)[\"\']', webpage)
        if not video_urls: exit;
        filmId=video_urls[0];
        #print(filmId)

        videoidurl = self._download_webpage('https://voircartoon.com/ajax-get-link-stream/?server=fembeds&filmId=%s' %  filmId,show_path);
        #print(videoidurl)
        videoid=re.findall(r'[^?]+\?id\=(?P<id>.*)',videoidurl)[0];
        #print(videoid);


        #dummy download m3u8 to prevent 403 during _extract_m3u8_formats
        dummym3u8 = self._download_webpage('https://lb.gogomovies.to/hls/%s/%s' %  (videoid, videoid),videoid);


        formats = self._extract_m3u8_formats(
            'https://lb.gogomovies.to/hls/%s/%s' %  (videoid, videoid),
            videoid, 'mp4')
        self._sort_formats(formats)

        return {
            'id': videoid,
            'title': ogtitle,
            'uploader': 'TODO',
            'uploader_date': ogdate,
            'formats': formats,
            'description': ogdescription,
            #'thumbnail': '',  # livestream.get('thumbnailUrl'),
            'is_live': False,
            # 'timestamp': int_or_none(livestream.get('createdAt'), 1000),
            # 'view_count': int_or_none(livestream.get('watchingCount')),
        }


