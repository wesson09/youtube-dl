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


class TVhaiIE(InfoExtractor):#TurnerBaseIE):
    _VALID_URL = r'https?://(?:www\.)?tvhai\.org(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'http://tvhai.org/xem-phim-dau-la-dai-luc-371842',
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
        propvalpattern='<\s*meta\s+property\s*=\s*\"og:(?P<prop>[\w^\"]+)\"\s+content\s*=\s*\"(?P<value>[\w\W]|[^\"]*)\"\s*\/\s*>'
        matches = re.finditer(
            propvalpattern,
            webpage)
        ogtitle='';
        ogdescription='';
        for m in matches:
            if m.group(1) == 'title' :
                ogtitle=m.group(2);
            elif m.group(1) == 'description' :
                ogdescription=m.group(2);
        
        matches = re.findall(
        '(?:https?:)?\/\/play\.tvhaystream.xyz\/play\/v1\/(?P<ID>\w+)',
        webpage)

        if not matches :#embed video from other site
            return;
        video_id= matches[0];  
        prejsonwebpage=self._download_webpage('https://play.tvhaystream.xyz/play/v1/%s' %video_id,video_id,headers={
           # 'Host': 'api-if.tvhaystream.xyz',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
#'Accept': '*/*',
#'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
#'Accept-Encoding': 'gzip, deflate, br',
#'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#'Content-Length': '44',
#'Connection': 'keep-alive',
#'Sec-Fetch-Dest': 'empty',
#'Sec-Fetch-Mode': 'cors',
#'Sec-Fetch-Site': 'same-site',
#'Pragma': 'no-cache',
#'Cache-Control': 'no-cache',
                #'Authorization': '%s %s' % (token_type, access_token),
                #'Referer': '%s' % ('https://play.tvhaystream.xyz'),
                'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            });
       # print(prejsonwebpage);
        
        
    #     var TYPEEND = 'html';
    #var DOMAIN_API = 'https://api-plhq.tvhaystream.xyz/apiv4/';
    #var DOMAIN_LIST_RD = ["plhq01.ggcctvhai001.xyz","plhq02.ggcctvhai001.xyz","plhq03.ggcctvhai001.xyz","plhq04.ggcctvhai001.xyz","plhq05.ggcctvhai001.xyz","plhq06.ggcctvhai001.xyz","plhq07.ggcctvhai001.xyz","plhq08.ggcctvhai001.xyz"];

        #matches = re.findall('var idfile = "(?P<ID>\w+)"',prejsonwebpage);
        #print(matches);
        #idfile=matches[0]
        #assert( idfile == videoid)
        
        matches = re.findall('var idUser = "(?P<ID>\w+)"',prejsonwebpage);        
        #  print(matches);
        idUser=matches[0]
        matches = re.findall('var DOMAIN_API = \'(?P<ID>[\w:\/.-]+)\'',prejsonwebpage);        
        #print(matches);
        DOMAIN_API=matches[0]
        
        #print( '%s%s/%s' % (DOMAIN_API,idUser,video_id));
        context = ssl._create_default_https_context()
        # enable PHA for TLS 1.3 connections if available
        #if context.post_handshake_auth is not None:
        #    context.post_handshake_auth = True
        # context.check_hostname=False;

        with socket.create_connection(('api-plhq.tvhaystream.xyz', 443)) as sock:
            with context.wrap_socket(sock,
                                     server_hostname='api-plhq.tvhaystream.xyz') as sslsock:
                dercert = sslsock.getpeercert(True)
        cert = ssl.DER_cert_to_PEM_cert(dercert)

        # prepare configuration
        configuration = QuicConfiguration(
            is_client=True, alpn_protocols=H3_ALPN
        )
        configuration.load_verify_locations(cadata=bytes(cert, 'utf-8'))
        connection = QuicConnection(configuration=configuration);
        # connect
        addr = '%s%s/%s' % (DOMAIN_API,idUser,video_id)#"https://api-plhq.tvhaystream.xyz/apiv4/5ee31dd5665f2d19d5af4a99/6121dce66cfe6c0a52ca86de";
        stream_handler = None
        local_host = "::"
        local_port = 31280
        loop = asyncio.get_event_loop()

        future = loop.run_until_complete(
            # asyncio.run(
            runhttp3request(
                #      addr,
                # 443,
                #     configuration=configuration,
                #     create_protocol=QuicConnectionProtocol,
                #     session_ticket_handler=None,
                #     local_port=local_port,
                #     wait_connected=True
                configuration,
                [addr],
                # 'referrer=http://%3A%2F%2Ftvhai.org&typeend=html',
                'referrer=http://tvhai.org&typeend=html',
                False,
                local_port,
                True,
            ));

        # print("func_normal()={future}".format(**vars()))
        #print(future[0])
        # r'https?://(?:www\.)?tvhai\.org(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

        VALID_M3U = 'https?://(?:www\.)?(([\w^\/-]*)\/)*(?P<id>[^?#&]+)\.m3u8'
        matches = re.search(VALID_M3U, future[0])
        m3u8url = matches[0];
        loop.close()

        formats = self._extract_m3u8_formats(
            m3u8url,
            video_id, 'mp4')
        #    https://m3u8-plhq.tvhaystream.xyz/m3u8/v3/5/6121dce66cfe6c0a52ca86de/1630510274/b7bfab92ee090d3ddce2989f62e2b1fd.m3u8
        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': ogtitle,
            'uploader': 'TODO',
            'uploader_id': 'TODO',
            'formats': formats,
            'description': ogdescription,  # livestream.get('content'),
            #'thumbnail': '',  # livestream.get('thumbnailUrl'),
            'is_live': False,
            # 'timestamp': int_or_none(livestream.get('createdAt'), 1000),
            # 'view_count': int_or_none(livestream.get('watchingCount')),
        }


