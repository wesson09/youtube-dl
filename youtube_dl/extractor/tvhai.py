# coding: utf-8
from __future__ import unicode_literals
import time
import http.client
import json
import re

import base64
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
    try_get, sanitize_url,
)

import socket
import ssl
#
# from  ..http3_client import (HttpClient,HttpRequest,HttpConnection);
# import asyncio
#
# import aioquic
# from aioquic.asyncio.client import connect
# from aioquic.asyncio.protocol import QuicConnectionProtocol
# from aioquic.h0.connection import H0_ALPN, H0Connection
# from aioquic.h3.connection import H3_ALPN, H3Connection
# from aioquic.h3.events import (
#     DataReceived,
#     H3Event,
#     HeadersReceived,
#     PushPromiseReceived,
# )
# from aioquic.quic.configuration import QuicConfiguration
# from aioquic.quic.connection import QuicConnection;
# from aioquic.quic.events import QuicEvent
# from aioquic.tls import CipherSuite, SessionTicket
#
# async def runhttp3request(
#         configuration: QuicConfiguration,
#         urls: List[str],
#         data: Optional[str],
#         include: bool,
#       #  output_dir: Optional[str],
#         local_port: int,
#         zero_rtt: bool,
# ) -> str:
#     # parse URL
#     parsed = parse.urlparse(urls[0])
#     assert parsed.scheme in (
#         "https",
#         "wss",
#     ), "Only https:// or wss:// URLs are supported."
#     host = parsed.hostname
#     if parsed.port is not None:
#         port = parsed.port
#     else:
#         port = 443
#
#     async with connect(
#             host,
#             port,
#             configuration=configuration,
#             create_protocol=HttpClient,
#             session_ticket_handler=None,#save_session_ticket,
#             local_port=local_port,
#             wait_connected=not zero_rtt,
#     ) as client:
#         client = cast(HttpClient, client)
#
#         if parsed.scheme == "wss":
#             ws = await client.websocket(urls[0], subprotocols=["chat", "superchat"])
#
#             # send some messages and receive reply
#             for i in range(2):
#                 message = "Hello {}, WebSocket!".format(i)
#                 print("> " + message)
#                 await ws.send(message)
#
#                 message = await ws.recv()
#                 print("< " + message)
#
#             await ws.close()
#         else:
#             # perform request
#             coros = [
#                 perform_http_request(
#                     client=client,
#                     url=url,
#                     data=data,
#                     include=include,
#                     #output_dir=output_dir,
#                 )
#                 for url in urls
#             ]
#
#
#             res=await asyncio.gather(*coros)
#
#
#             # process http pushes
#             process_http_pushess(client=client, include=include)
#
#             return res
#
# async def perform_http_request(
#     client: HttpClient,
#     url: str,
#     data: Optional[str],
#     include: bool,
#     #output_dir: Optional[str],
# ) -> str:
#     # perform request
#     start = time.time()
#     if data is not None:
#         http_events = await client.post(
#             url,
#             data=data.encode(),
#              headers={"content-type": "application/x-www-form-urlencoded"},
#         )
#         method = "POST"
#     else:
#         http_events = await client.get(url)
#         method = "GET"
#     elapsed = time.time() - start
#
#     # print speed
#     octets = 0
#     http3client="";
#     for http_event in http_events:
#         if isinstance(http_event, DataReceived):
#             octets += len(http_event.data)
#     print(
#         "Response received for %s %s : %d bytes in %.1f s (%.3f Mbps)"
#         % (method, parse.urlparse(url).path, octets, elapsed, octets * 8 / elapsed / 1000000)
#     )
#
#     for http_event in http_events:
#         if isinstance(http_event, HeadersReceived) and include:
#             headers = b""
#             for k, v in http_event.headers:
#                 headers += k + b": " + v + b"\r\n"
#             if headers:
#                 print(headers + b"\r\n")
#         elif isinstance(http_event, DataReceived):
#             http3client=http3client + http_event.data.decode('utf-8')
#     # output response
#     # if output_dir is not None:
#     #     output_path = os.path.join(
#     #         output_dir, os.path.basename(urlparse(url).path) or "index.html"
#     #     )
#     #     with open(output_path, "wb") as output_file:
#     #         write_response(
#     #             http_events=http_events, include=include, output_file=output_file
#     #         )
#     return http3client;
#
#
# def process_http_pushess(
#     client: HttpClient,
#     include: bool,
#     #output_dir: Optional[str],
# ) -> None:
#     for _, http_events in client.pushes.items():
#         method = ""
#         octets = 0
#         path = ""
#         for http_event in http_events:
#             if isinstance(http_event, DataReceived):
#                 octets += len(http_event.data)
#             elif isinstance(http_event, PushPromiseReceived):
#                 for header, value in http_event.headers:
#                     if header == b":method":
#                         method = value.decode()
#                     elif header == b":path":
#                         path = value.decode()
#         print("Push received for %s %s : %s bytes", method, path, octets)
#
#         # output response
#         # if output_dir is not None:
#         #     output_path = os.path.join(
#         #         output_dir, os.path.basename(path) or "index.html"
#         #     )
#         #     with open(output_path, "wb") as output_file:
#         #         write_response(
#         #             http_events=http_events, include=include, output_file=output_file
#         #         )
#



#import M2Crypto
#import OpenSSL
from youtube_dl import utils

from youtube_dl.compat import (
  compat_urllib_request
)
from threading import Thread
class HeadRequest(Thread,InfoExtractor):
    headrequeststring = 0
    video_id=''
    headers={}
    responseheader='';

    def __init__(self, args,vid,h,extract):
        Thread.__init__(self)

        super(InfoExtractor,self).__init__();
        self.    headrequeststring  = args
        self.    video_id  = vid
        self.    headers  = h
        self.    extract  = extract

    # The run method is overridden to define
    # the thread body
    def run(self):
        fail=True;
        nbtry=0;
        while fail and nbtry<10:
            try:
               s = compat_urllib_request.session()
               s.headers=self.headers;
#                url_or_request = urllib3.re(
#                    method="HEAD",
#                    url=sanitize_url(self.headrequeststring),
#                    redirect=True,headers=self.headers
#                )
#                url_or_request=sanitized_Request requests.Request('HEAD',url=sanitize_url(self.headrequeststring),headers=self.headers);#,allow_redirects=True,verify=False );
#                url_or_requestprep= url_or_request.prepare();
# #               del url_or_requestprep.headers['Connection']
#                self.responseheader =s.send(url_or_requestprep)
#                #self.responseheader = self._downloader.urlopen(url_or_request);

               #url_or_request = utils.sanitized_Request(self.headrequeststring, None, self.headers);
               # self.responseheader = self._downloader.urlopen(url_or_request)

               #force urllib3 because of a bug in urllib in Python36_32bits
               #TODO should evolve to 38 but I got back from it whithout remembering why..:/
               #self.responseheader = urllib3.PoolManager().request('HEAD',sanitize_url(self.headrequeststring), None, self.headers)

               self.responseheader = self._request_webpage(self.headrequeststring, self.video_id,   headers=self.headers  )
               print(self.responseheader.headers['content-length'])
               fail=False;
            except Exception as e:
                print(e)
                #traceback.print_exc()
                fail=True;
                time.sleep(1);
            finally:
                nbtry=nbtry+1;

class TVhaiIE(InfoExtractor):#TurnerBaseIE):
    _VALID_URL = r'https?://(?:www\.)?tvhai\.org(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

    _TESTS = [{
        'url': 'http://tvhai.org/xem-phim-dau-la-dai-luc-371842',
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
            return;
        video_id= matches[0];


        if embedlink.find('fembed')>=0:#https://www.fembed.com/v/ID

            #get server page video data
            prejsonwebpage = self._download_webpage('http://tvhai.org/preload/habet.php', video_id, headers={
                # 'Host': 'api-if.tvhaystream.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                # 'Accept': '*/*',
                # 'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                # 'Accept-Encoding': 'gzip, deflate, br',
                # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'Content-Length': '44',
                # 'Connection': 'keep-alive',
                # 'Sec-Fetch-Dest': 'empty',
                # 'Sec-Fetch-Mode': 'cors',
                # 'Sec-Fetch-Site': 'same-site',
                # 'Pragma': 'no-cache',
                # 'Cache-Control': 'no-cache',
                # 'Authorization': '%s %s' % (token_type, access_token),
                 'Referer': '%s?link=%s' % ( embed,embedlink),
                #'Origin': '%s' % ('https://play.tvhaystream.xyz'),
            });


            self._sort_formats(formats)
            return {
                'id': video_id,
                'title': ogtitle,
                'uploader': 'TODO',
                'uploader_id': 'TODO',
                'formats': formats,
                'description': ogdescription,  # livestream.get('content'),
                # 'thumbnail': '',  # livestream.get('thumbnailUrl'),
                'is_live': False,
                # 'timestamp': int_or_none(livestream.get('createdAt'), 1000),
                # 'view_count': int_or_none(livestream.get('watchingCount')),
            }

        else:  #https://play.tvhaystream.xyz/play/v1/ID
            prejsonwebpage=self._download_webpage(embedlink,video_id,headers={
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
            DOMAIN_API=matches[0];

            matches = re.findall(r'((?P<SCHEME>(?:https?))\:\/\/(?P<HOSTNAME>(?:www.|[a-zA-Z0-9.]+)[a-zA-Z0-9\-\.]+\.([a-zA-Z0-9]*))(?P<PORT>\:[0-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?P<PATH>[a-zA-Z0-9\-\.\/]+)?(?P<QUERY>(?:\?$|[a-zA-Z0-9\.\,\;\?\'\\\+&%\$\=~_\-\*]+))?(?P<FRAGMENT>#[a-zA-Z0-9\-\.]+)?)'
            ,DOMAIN_API);
            hostname=matches[0][2];

            matches = re.findall('var DOMAIN_LIST_RD[ \t\n]=[ \t\n]\[(?P<domainlist>.*)\]',prejsonwebpage);
            matches = re.findall('\"(?P<domain>[^\"]*)\"',matches[0]);

            DOMAIN_LIST_RD= matches;


            #apisingok=self._download_webpage('https://api-sing-02.tvhaystream.xyz/apiv2/views/%s'%video_id,show_path+'bis');
            # connect
            addr = '%s%s/%s' % (DOMAIN_API,idUser,video_id)#"https://api-plhq.tvhaystream.xyz/apiv4/5ee31dd5665f2d19d5af4a99/6121dce66cfe6c0a52ca86de";
            #addr = "https://api-plhq.tvhaystream.xyz/apiv4/5ee31dd5665f2d19d5af4a99/6121dce66cfe6c0a52ca86de";
            #addr = '%s%s/%s' % ("https://api-plhq.tvhaystream.xyz/apiv4/", idUser,    video_id)  # "https://api-plhq.tvhaystream.xyz/apiv4/5ee31dd5665f2d19d5af4a99/6121dce66cfe6c0a52ca86de";

            requestresult='';

            if False: # http3 path not here anymore

                print('Contact Http3 %s'%addr)
                # print( '%s%s/%s' % (DOMAIN_API,idUser,video_id));
                context = ssl._create_default_https_context()
                # enable PHA for TLS 1.3 connections if available
                # if context.post_handshake_auth is not None:
                #    context.post_handshake_auth = True
                # context.check_hostname=False;

                with socket.create_connection((hostname, 443)) as sock:
                    with context.wrap_socket(sock,
                                             server_hostname=hostname) as sslsock:
                        dercert = sslsock.getpeercert(True)
                cert = ssl.DER_cert_to_PEM_cert(dercert)

                # prepare configuration
                configuration = QuicConfiguration(
                    is_client=True, alpn_protocols=H3_ALPN
                )
                configuration.load_verify_locations(cadata=bytes(cert, 'utf-8'))
                connection = QuicConnection(configuration=configuration);
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
                        #'referrer=http://%3A%2F%2Ftvhai.org&typeend=html',
                        'referrer=http://tvhai.org&typeend=html',
                        False,
                        local_port,
                        True,
                    ));
                requestresult=future[0]
                loop.close()

                VALID_M3U = 'https?://(?:www\.)?(([\w^\/-]*)\/)*(?P<id>[^?#&]+)\.m3u8'
                matches = re.search(VALID_M3U,requestresult )
                m3u8url = matches[0];
                formats = self._extract_m3u8_formats(
                    m3u8url,
                    video_id, 'mp4')
                 #  https://m3u8-plhq.tvhaystream.xyz/m3u8/v3/5/6121dce66cfe6c0a52ca86de/1630510274/b7bfab92ee090d3ddce2989f62e2b1fd.m3u8
            else:
                headers = {
                    # 'Host': 'api-if.tvhaystream.xyz',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                    'Accept': '*/*',
                    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    # 'Content-Length': '44',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'cross-site',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    # 'Authorization': '%s %s' % (token_type, access_token),
                    # 'Referer': '%s' % ('https://play.tvhaystream.xyz'),
                    'Origin': '%s' % ('https://play.tvhaystream.xyz'),
                }
                videojsonhandle = self._download_json_handle(
                    addr ,
                    show_path, 'Downloading video JSON',
                    data=bytes('referrer=http://tvhai.org&typeend=html', 'utf-8'), headers=   headers , fatal=False)


                requestresult= videojsonhandle[0];
                print(requestresult);


                m3u8_doc='#EXTM3U\n';
                m3u8_doc+='#EXT-X-VERSION:3\n';
                m3u8_doc+='#EXT-X-TARGETDURATION:10\n';
                m3u8_doc+='#EXT-X-PLAYLIST-TYPE:VOD\n';
                # EXTM3U
                # EXT-X-VERSION:3
                # EXT-X-TARGETDURATION:10
                # EXT-X-PLAYLIST-TYPE:VOD
                # EXTINF:10,
                headers = {'Accept': '*/*',
                    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                            'User-Agent': 'Mozilla/5.0',# (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
                           #"Origin": "https://play.tvhaystream.xyz",
                           # "referer": "https://apird-tvhai.rdgogo.xyz",
                           #"Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                             "Accept-Encoding": "gzip, deflate",
                           #"TE": "trailers",
                          # "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                           #"Pragma": "no-cache", "DNT": "1",
                           #"Sec-GPC": "1", "Connection": "keep-alive"
                           }
                headreqs=[];

                idxdomain=0;
                idx=0
                while idx <len (requestresult['data'][1]):
                    id2=0
                    headreqs2=[]
                    while (id2+idx<len (requestresult['data'][1]) ) and (id2<50) :
                        v=requestresult['data'][1][idx+id2]
                        domain=DOMAIN_LIST_RD[idxdomain];
                        idxdomain=idxdomain+1
                        if idxdomain>=len(DOMAIN_LIST_RD):
                            idxdomain=0;
                        #thr=HeadRequest('https://apird-tvhai.rdgogo.xyz/rdv5/%s/%s/%s.rd' % (requestresult['quaity'], idUser, v),v,headers,self);
                        thr = HeadRequest(
                            'https://%s/stream/v5/%s.html' % (domain, v), v,
                            headers, self);
                        thr.set_downloader(self._downloader)
                        headreqs2.append(thr);
                        id2=id2+1;
                    for r in headreqs2:
                        r.start();
                    for r in headreqs2:
                        r.join();
                    headreqs.extend(headreqs2);
                    idx=idx+id2;

                    # for v in requestresult['data'][1]:
                    #     thr=HeadRequest('https://apird-tvhai.rdgogo.xyz/rdv5/%s/%s/%s.rd' % (requestresult['quaity'], idUser, v),v,headers,self);
                    #     thr.set_downloader(self._downloader)
                    #     headreqs.append(thr);


                idx=0
                idxdomain=0
                for v in requestresult['data'][1]:
                    domain = DOMAIN_LIST_RD[idxdomain];
                    idxdomain = idxdomain + 1
                    if idxdomain >= len(DOMAIN_LIST_RD):
                        idxdomain = 0;
                    v1= re.findall('\w+$',v);
                    m3Uchunk='https://%s/stream/v5/%s.html' % (domain, v)

                    # metachunk = self._request_webpage(m3Uchunk, show_path, #'note', 'errnote', fatal, data=data,
                    #                                    headers=headers,
                    #                           #   query=query, expected_status=expected_status
                    #                                   )
                    #
                    # print(metachunk.headers['content-length'])
                    chunksize=int(headreqs[idx].responseheader.headers['content-length']);

                    #print(m3Uchunk);
                    m3u8_doc +='#EXTINF:%s,\n' % requestresult['data'][0][idx];
                    m3u8_doc +='#EXT-X-BYTERANGE:%d@8\n'%chunksize;
                    m3u8_doc += m3Uchunk+'\n';
                    idx=idx+1
                m3u8_doc +='#EXT-X-ENDLIST\n';
                print(m3u8_doc)
                d=base64.b64encode(bytes(m3u8_doc, 'UTF-8'))
                dataurl='data:application/x-mpegURL;base64,' +d.decode(encoding="utf-8");
                formats = self._extract_m3u8_formats(
                dataurl,
                   video_id, 'mp4',entry_protocol='m3u8_native')

                # formats = self._parse_m3u8_formats(
                #     'data://application/x-mpegURL,'+m3u8_doc, video_id,
                #     # ext=mp4, entry_protocol=entry_protocol,
                #     # preference=preference, m3u8_id=m3u8_id, live=live
                # )
                #requestresult=videojsonhandle[0];

                # print("func_normal()={future}".format(**vars()))
            #print(future[0])
            # r'https?://(?:www\.)?tvhai\.org(([\w^\/-]*)\/)*(?P<id>[^\/?#&]+)'

            # VALID_M3U = 'https?://(?:www\.)?(([\w^\/-]*)\/)*(?P<id>[^?#&]+)\.m3u8'
            # matches = re.search(VALID_M3U,requestresult )
            # m3u8url = matches[0];
            # formats = self._extract_m3u8_formats(
            #     m3u8url,
            #     video_id, 'mp4')
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


