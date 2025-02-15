from __future__ import unicode_literals

import errno
import os
import socket
import time
import random
import re

from .common import FileDownloader
from ..compat import (
    compat_str,
    compat_urllib_error,
    compat_urllib_request,
)
from ..utils import (
    ContentTooShortError,
    encodeFilename,
    int_or_none,
    sanitize_open,
    sanitized_Request,
    write_xattr,
    XAttrMetadataError,
    XAttrUnavailableError,
)


from Crypto.Hash import MD5
from Crypto.Cipher import AES, Blowfish
from binascii import a2b_hex, b2a_hex

class HttpFD(FileDownloader):
    def real_download(self, filename, info_dict):
        url = info_dict['url']

        class DownloadContext(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            __delattr__ = dict.__delitem__

        ctx = DownloadContext()
        ctx.filename = filename
        ctx.tmpfilename = self.temp_name(filename)
        ctx.stream = None

        # Do not include the Accept-Encoding header
        headers = {'Youtubedl-no-compression': 'True'}
        add_headers = info_dict.get('http_headers')
        if add_headers:
            headers.update(add_headers)

        is_test = self.params.get('test', False)
        chunk_size = self._TEST_FILE_SIZE if is_test else (
            info_dict.get('downloader_options', {}).get('http_chunk_size')
            or self.params.get('http_chunk_size') or 0)

        ctx.open_mode = 'wb'
        ctx.resume_len = 0
        ctx.data_len = None
        ctx.block_size = self.params.get('buffersize', 1024)
        ctx.start_time = time.time()
        ctx.chunk_size = None

        if self.params.get('continuedl', True):
            # Establish possible resume length
            if os.path.isfile(encodeFilename(ctx.tmpfilename)):
                ctx.resume_len = os.path.getsize(
                    encodeFilename(ctx.tmpfilename))

        ctx.is_resume = ctx.resume_len > 0

        count = 0
        retries = self.params.get('retries', 0)

        class SucceedDownload(Exception):
            pass

        class RetryDownload(Exception):
            def __init__(self, source_error):
                self.source_error = source_error

        class NextFragment(Exception):
            pass

        def set_range(req, start, end):
            range_header = 'bytes=%d-' % start
            if end:
                range_header += compat_str(end)
            req.add_header('Range', range_header)

        def establish_connection():
            ctx.chunk_size = (random.randint(int(chunk_size * 0.95), chunk_size)
                              if not is_test and chunk_size else chunk_size)
            if ctx.resume_len > 0:
                range_start = ctx.resume_len
                if ctx.is_resume:
                    self.report_resuming_byte(ctx.resume_len)
                ctx.open_mode = 'ab'
            elif ctx.chunk_size > 0:
                range_start = 0
            else:
                range_start = None
            ctx.is_resume = False
            range_end = range_start + ctx.chunk_size - 1 if ctx.chunk_size else None
            if range_end and ctx.data_len is not None and range_end >= ctx.data_len:
                range_end = ctx.data_len - 1
            has_range = range_start is not None
            ctx.has_range = has_range
            request = sanitized_Request(url, None, headers)
            if has_range:
                set_range(request, range_start, range_end)
            # Establish connection
            try:
                try:
                    ctx.data = self.ydl.urlopen(request)
                except (compat_urllib_error.URLError, ) as err:
                    # reason may not be available, e.g. for urllib2.HTTPError on python 2.6
                    reason = getattr(err, 'reason', None)
                    if isinstance(reason, socket.timeout):
                        raise RetryDownload(err)
                    raise err
                # When trying to resume, Content-Range HTTP header of response has to be checked
                # to match the value of requested Range HTTP header. This is due to a webservers
                # that don't support resuming and serve a whole file with no Content-Range
                # set in response despite of requested Range (see
                # https://github.com/ytdl-org/youtube-dl/issues/6057#issuecomment-126129799)
                if has_range:
                    content_range = ctx.data.headers.get('Content-Range')
                    if content_range:
                        content_range_m = re.search(r'bytes (\d+)-(\d+)?(?:/(\d+))?', content_range)
                        # Content-Range is present and matches requested Range, resume is possible
                        if content_range_m:
                            if range_start == int(content_range_m.group(1)):
                                content_range_end = int_or_none(content_range_m.group(2))
                                content_len = int_or_none(content_range_m.group(3))
                                accept_content_len = (
                                    # Non-chunked download
                                    not ctx.chunk_size
                                    # Chunked download and requested piece or
                                    # its part is promised to be served
                                    or content_range_end == range_end
                                    or content_len < range_end)
                                if accept_content_len:
                                    ctx.data_len = content_len
                                    return
                    # Content-Range is either not present or invalid. Assuming remote webserver is
                    # trying to send the whole file, resume is not possible, so wiping the local file
                    # and performing entire redownload
                    self.report_unable_to_resume()
                    ctx.resume_len = 0
                    ctx.open_mode = 'wb'
                ctx.data_len = int_or_none(ctx.data.info().get('Content-length', None))
                return
            except (compat_urllib_error.HTTPError, ) as err:
                if err.code == 416:
                    # Unable to resume (requested range not satisfiable)
                    try:
                        # Open the connection again without the range header
                        ctx.data = self.ydl.urlopen(
                            sanitized_Request(url, None, headers))
                        content_length = ctx.data.info()['Content-Length']
                    except (compat_urllib_error.HTTPError, ) as err:
                        if err.code < 500 or err.code >= 600:
                            raise
                    else:
                        # Examine the reported length
                        if (content_length is not None
                                and (ctx.resume_len - 100 < int(content_length) < ctx.resume_len + 100)):
                            # The file had already been fully downloaded.
                            # Explanation to the above condition: in issue #175 it was revealed that
                            # YouTube sometimes adds or removes a few bytes from the end of the file,
                            # changing the file size slightly and causing problems for some users. So
                            # I decided to implement a suggested change and consider the file
                            # completely downloaded if the file size differs less than 100 bytes from
                            # the one in the hard drive.
                            self.report_file_already_downloaded(ctx.filename)
                            self.try_rename(ctx.tmpfilename, ctx.filename)
                            self._hook_progress({
                                'filename': ctx.filename,
                                'status': 'finished',
                                'downloaded_bytes': ctx.resume_len,
                                'total_bytes': ctx.resume_len,
                            })
                            raise SucceedDownload()
                        else:
                            # The length does not match, we start the download over
                            self.report_unable_to_resume()
                            ctx.resume_len = 0
                            ctx.open_mode = 'wb'
                            return
                elif err.code < 500 or err.code >= 600:
                    # Unexpected HTTP error
                    raise
                raise RetryDownload(err)
            except socket.error as err:
                if err.errno != errno.ECONNRESET:
                    # Connection reset is no problem, just retry
                    raise
                raise RetryDownload(err)

        def md5hex(data):
            """ return hex string of md5 of the given string """
            # type(data): bytes
            # returns: bytes
            h = MD5.new()
            h.update(data)
            return b2a_hex(h.digest())

        def hexaescrypt(data, key):
            """ returns hex string of aes encrypted data """
            c = AES.new(key.encode(), AES.MODE_ECB)
            return b2a_hex(c.encrypt(data))

        def genurlkey(songid, md5origin, mediaver=4, fmt=1):
            """ Calculate the deezer download url given the songid, origin and media+format """
            data_concat = b'\xa4'.join(_ for _ in [md5origin.encode(),
                                                   str(fmt).encode(),
                                                   str(songid).encode(),
                                                   str(mediaver).encode()])
            data = b'\xa4'.join([md5hex(data_concat), data_concat]) + b'\xa4'
            if len(data) % 16 != 0:
                data += b'\0' * (16 - len(data) % 16)
            return hexaescrypt(data, "jo6aey6haid2Teih")

        def calcbfkey(songid):
            """ Calculate the Blowfish decrypt key for a given songid """
            key = b"g4el58wc0zvf9na1"
            songid_md5 = md5hex(songid.encode())

            xor_op = lambda i: chr(songid_md5[i] ^ songid_md5[i + 16] ^ key[i])
            decrypt_key = "".join([xor_op(i) for i in range(16)])
            return decrypt_key

        def blowfishDecrypt(data, key):
            iv = a2b_hex("0001020304050607")
            c = Blowfish.new(key.encode(), Blowfish.MODE_CBC, iv)
            return c.decrypt(data)

        def decodefile(fh, key, fo):
            """
            decode   data from file  < fh>, and write to file  < fo>.
            decode  using blowfish with  < key>.
            Only every third 2048 byte block is encrypted.
            """
            blockSize = 2048
            i = 0

            while True:
                data=fh.read(blockSize)
                if not data:
                    break

                isEncrypted = ((i % 3) == 0)
                isWholeBlock = len(data) == blockSize

                if isEncrypted and isWholeBlock:
                    data = blowfishDecrypt(data, key)

                fo.write(data)
                i += 1
                if not isWholeBlock:
                    break;

        def download():
            data_len = ctx.data.info().get('Content-length', None)

            # Range HTTP header may be ignored/unsupported by a webserver
            # (e.g. extractor/scivee.py, extractor/bambuser.py).
            # However, for a test we still would like to download just a piece of a file.
            # To achieve this we limit data_len to _TEST_FILE_SIZE and manually control
            # block size when downloading a file.
            if is_test and (data_len is None or int(data_len) > self._TEST_FILE_SIZE):
                data_len = self._TEST_FILE_SIZE

            if data_len is not None:
                data_len = int(data_len) + ctx.resume_len
                min_data_len = self.params.get('min_filesize')
                max_data_len = self.params.get('max_filesize')
                if min_data_len is not None and data_len < min_data_len:
                    self.to_screen('\r[download] File is smaller than min-filesize (%s bytes < %s bytes). Aborting.' % (data_len, min_data_len))
                    return False
                if max_data_len is not None and data_len > max_data_len:
                    self.to_screen('\r[download] File is larger than max-filesize (%s bytes > %s bytes). Aborting.' % (data_len, max_data_len))
                    return False

            byte_counter = 0 + ctx.resume_len
            block_size = ctx.block_size
            start = time.time()

            # measure time over whole while-loop, so slow_down() and best_block_size() work together properly
            now = None  # needed for slow_down() in the first loop run
            before = start  # start measuring

            def retry(e):
                to_stdout = ctx.tmpfilename == '-'
                if ctx.stream is not None:
                    if not to_stdout:
                        ctx.stream.close()
                    ctx.stream = None
                ctx.resume_len = byte_counter if to_stdout else os.path.getsize(encodeFilename(ctx.tmpfilename))
                raise RetryDownload(e)

            dzrkey=None
            if info_dict.get('dzrdecode') and not dzrkey:
                #decode frame if require
                dzrid=info_dict['dzrdecode']
                dzrkey=calcbfkey(dzrid)

            framecount=-1

            while True:
                framecount=framecount+1

                try:
                    # Download and write
                    data_block = ctx.data.read(block_size if data_len is None else min(block_size, data_len - byte_counter))
                # socket.timeout is a subclass of socket.error but may not have
                # errno set
                except socket.timeout as e:
                    retry(e)
                except socket.error as e:
                    # SSLError on python 2 (inherits socket.error) may have
                    # no errno set but this error message
                    if e.errno in (errno.ECONNRESET, errno.ETIMEDOUT) or getattr(e, 'message', None) == 'The read operation timed out':
                        retry(e)
                    raise
                firsttime=byte_counter==0
                byte_counter += len(data_block)
                # exit loop when download is finished
                if len(data_block) == 0:
                    break
                #
                # TOHACKY check silence and/or detect meta data for stream cutting
                if self.params.get('onlinemetadata') :

                    now = time.time()
                    #if(byte_counter==0 or byte_counter>self.params.get('onlinemetadata')):
                    if  firsttime or now-start>self.params.get('onlinemetadata'):
                        start=now
                        if firsttime: #hacky
                            guess =  ctx.filename.partition('?')[0].rpartition('.')[2]
                            ctx.folder=ctx.filename[:len(ctx.filename)-len(guess)-1];

                        request=compat_urllib_request.Request(self.params.get('urlmetadata'))
                        request.add_header('Icy-MetaData', 1)
                        request.add_header('Accept-Encoding', 'gzip, deflate')
                        response=self.ydl._opener.open(request, timeout=self.ydl._socket_timeout)

                        try:
                            icy_metaint_header = response.headers.get('icy-metaint')
                            if icy_metaint_header is not None:
                                metaint = int(icy_metaint_header)+1
                                read_buffer = metaint + 255
                                content = response.read(read_buffer)

                                title = content[metaint:]
                                title = title.split(b';')[0].split(b'=')[1] #assume first key is StreamTitle
                                title = title.split(b'\'')[1].decode("utf-8")
                                title=title.replace('\#','')
                                title=title.replace('/','');
                                #print (title)
                                if title!='' and ctx.tmpfilename!=ctx.folder+'/'+title+'.mp3.part':
                                    dn = os.getcwd()
                                    dn = dn + os.path.sep + ctx.folder
                                    if dn and not os.path.exists(dn):
                                        os.makedirs(dn)
                                    ctx.tmpfilename = ctx.folder+'/'+title+'.mp3.part'
                                    ctx.filename = ctx.folder+'/'+title+'.mp3'
                                    ctx.stream.close();
                                    ctx.stream = None;
                            else:
                                response.close
                        except:
                            response.close
                            if not firsttime:
                                #stop metadata request on second fail
                                del self.params['onlinemetadata']
                #             print('Error')
                # Open destination file just in time
                if ctx.stream is None:
                    try:
                        ctx.stream, ctx.tmpfilename = sanitize_open(
                            ctx.tmpfilename, ctx.open_mode)
                        assert ctx.stream is not None
                        ctx.filename = self.undo_temp_name(ctx.tmpfilename)
                        self.report_destination(ctx.filename)
                    except (OSError, IOError) as err:
                        self.report_error('unable to open for writing: %s' % str(err))
                        return False

                    if self.params.get('xattr_set_filesize', False) and data_len is not None:
                        try:
                            write_xattr(ctx.tmpfilename, 'user.ytdl.filesize', str(data_len).encode('utf-8'))
                        except (XAttrUnavailableError, XAttrMetadataError) as err:
                            self.report_error('unable to set filesize xattr: %s' % str(err))

                try:
                    ctx.stream.write(data_block)
                except (IOError, OSError) as err:
                    self.to_stderr('\n')
                    self.report_error('unable to write data: %s' % str(err))
                    return False

                # Apply rate limit
                self.slow_down(start, now, byte_counter - ctx.resume_len)

                # end measuring of one loop run
                now = time.time()
                after = now

                # Adjust block size
                if not self.params.get('noresizebuffer', False):
                    block_size = self.best_block_size(after - before, len(data_block))

                before = after

                # Progress message
                speed = self.calc_speed(start, now, byte_counter - ctx.resume_len)
                if ctx.data_len is None:
                    eta = None
                else:
                    eta = self.calc_eta(start, time.time(), ctx.data_len - ctx.resume_len, byte_counter - ctx.resume_len)

                self._hook_progress({
                    'status': 'downloading',
                    'downloaded_bytes': byte_counter,
                    'total_bytes': ctx.data_len,
                    'tmpfilename': ctx.tmpfilename,
                    'filename': ctx.filename,
                    'eta': eta,
                    'speed': speed,
                    'elapsed': now - ctx.start_time,
                })

                if data_len is not None and byte_counter == data_len:
                    break

            if not is_test and ctx.chunk_size and ctx.data_len is not None and byte_counter < ctx.data_len:
                ctx.resume_len = byte_counter
                # ctx.block_size = block_size
                raise NextFragment()

            if ctx.stream is None:
                self.to_stderr('\n')
                self.report_error('Did not get any data blocks')
                return False
            if ctx.tmpfilename != '-':
                ctx.stream.close()

            if data_len is not None and byte_counter != data_len:
                err = ContentTooShortError(byte_counter, int(data_len))
                if count <= retries:
                    retry(err)
                raise err

            if dzrkey:
                fo=open(ctx.filename, "w+b")
                fi=open(ctx.tmpfilename, "rb")
                decodefile(fi, dzrkey, fo)
                fo.close()
                fi.close()
                os.unlink(ctx.tmpfilename)
            else:
                self.try_rename(ctx.tmpfilename, ctx.filename)


            # Update file modification time
            if self.params.get('updatetime', True):
                info_dict['filetime'] = self.try_utime(ctx.filename, ctx.data.info().get('last-modified', None))

            self._hook_progress({
                'downloaded_bytes': byte_counter,
                'total_bytes': byte_counter,
                'filename': ctx.filename,
                'status': 'finished',
                'elapsed': time.time() - ctx.start_time,
            })

            return True

        while count <= retries:
            try:
                establish_connection()
                return download()
            except RetryDownload as e:
                count += 1
                if count <= retries:
                    self.report_retry(e.source_error, count, retries)
                continue
            except NextFragment:
                continue
            except SucceedDownload:
                return True

        self.report_error('giving up after %s retries' % retries)
        return False