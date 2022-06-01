# coding: utf-8
from __future__ import unicode_literals

from urllib.parse import unquote

from .common import InfoExtractor
from ..utils import (
    merge_dicts,
    urljoin,
    sanitized_Request,
    urlencode_postdata,
)


class QPicIE(InfoExtractor):
    _VALID_URL = r'https://(?:mp\.)?weixin\.qq\.com/s/(?P<id>\S+)'
    _TESTS = [{
        'url': 'https://mp.weixin.qq.com/s/775csCtDJ_iEWYEM95UCOw',
        'info_dict': {
            'id': '2997',
            'ext': 'mp4',
            'title': 'Episode 02',
            'description': 'md5:2927701ea2f7e901de8bfa8d39b2852d',
            'series': 'The Asterisk War  (OmU.)',
            'season_number': 1,
            'episode': 'Episode 02',
            'episode_number': 2,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        # DRM Protected
        'url': 'https://www.wakanim.tv/de/v2/catalogue/episode/7843/sword-art-online-alicization-omu-arc-2-folge-15-omu',
        'only_matching': True,
    }]
    _GEO_BYPASS = False


    def _robustregex(self,variable,reg,webpage):#(?P<id>\d+)
        try:
            return self._search_regex(r'var '+variable+' = "'+reg, webpage, variable, group='id')
        except:
            try:
                return self._search_regex(r'var ' + variable + ' = "" \|\| "' + reg, webpage, variable,
                                          group='id')
            except:
                    return self._search_regex(r'var ' + variable + ' = "" \|\| "" \|\| "' + reg, webpage, variable,
                                              group='id')

    def _real_extract(self, url):
        self.video_id = self._match_id(url)
# '
#       var mid = "" || "" || "2247564867";
#       var biz = "" || "MzUxMDY1MDU5MA==";
#       var sessionid = "" || "svr_d1267e42c38";'
        webpage = self._download_webpage(url, self.video_id)
        self.mid=self.  _robustregex('mid','(?P<id>[^"]+)',webpage)
        self.bid=self.  _robustregex('biz','(?P<id>[^"]+)',webpage)
        self.sessionid=self.  _robustregex('sessionid','(?P<id>[^"]+)',webpage)
        try:
            self.msg_title=self._search_regex(r'var msg_title = \'(?P<id>[^\']+)\'', webpage, 'msg_title',  group='id')
        except:
            self.msg_title =self.video_id
        try:
            self.msg_desc=self._search_regex(r'var msg_desc = htmlDecode\(\"(?P<id>[^\"]+)\"', webpage, 'msg_desc',  group='id')
        except:
            self.msg_desc =self.video_id
        self.mpvid=self._search_regex(
            r'data-mpvid="(?P<id>[^"]+)"', webpage, 'mpvid',
            group='id')

        cookies = self._get_cookies('https://mp.weixin.qq.com')
        self.Cookie=''
        for c in cookies:
            self.Cookie=self.Cookie+c+'='+cookies[c].value+'; '
        return self._continueextraction(url)

    def _continueextraction(self, url):
        posturl_data = {
        }
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
            'Accept': '*/*',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://mp.weixin.qq.com',
            'Connection': 'keep-alive',
            'Referer': url,
            'Cookie': self.Cookie,#'rewardsn=; wxtokenkey=777; wwapp.vid=; wwapp.cst=; wwapp.deviceid=',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0',
            'Content-Length': '0',
            'TE': 'trailers',
        }
        posturl='https://mp.weixin.qq.com/mp/appmsgreport?action=page_time&__biz=%s&uin=&key=&pass_ticket=&wxtoken=777&devicetype=&clientversion=&__biz=%s&appmsg_token=&x5=0&f=json'%(self.bid,self.bid)
        post_data='report_bizuin=%s&title=视频编辑中级班 第七课：​制作视觉错位效果的小技巧&mid=%s&idx=2&subscene=10000&sessionid=%s&enterid=1651478058&read_cnt=0&old_like_cnt=0&like_cnt=0&screen_width=1903&screen_height=531&screen_num=8&idkey=64469_15_1&copyright_stat=1&ori_article_type=摄影_后期处理&video_cnt=1&read_screen_num=7&is_finished_read=0&scene=&content_len=206212&start_time=1651478055335&end_time=1651479470933&handup_time=0&total_height=4125&exit_height=3367&img_640_cnt=0&img_0_cnt=0&img_300_cnt=0&wtime=18238&ftime=4365&ptime=9953&onload_time=18238&reward_heads_total=0&reward_heads_fail=0&outer_pic=0&publish_time=1634313660&item_show_type=0&page_req_info={"startGetAppmsgExtTime":1651478064027,"startGetAppmsgAdTime":1651478064066,"receiveGetAppmsgExt":"200|1651478068764","receiveGetAppmsgAd":"200|1651478065140","domCompleteTime":1651478064073}&is_darkmode=0&search_click_id=0&webp_total=1&webp_lossy=1&webp_lossless=1&webp_alpha=1&webp_animation=1&download_cdn_webp_img_cnt=0&download_img_cnt=0&download_cdn_img_cnt=0&img_cnt=7&report_time=1651479470&source=&req_id=021562EfnmYNRb7yXFRhPIA2&recommend_version=&class_id=&ascene=-1&hotspotjson={"hotspotinfolist":[]}&is_pay_subscribe=0&is_paid=0&preview_percent=0&is_finished_preview=0&fee=&pay_cnt=undefined&worthy_cnt=undefined&exptype=&expsessionid=&'%(self.bid,self.mid,self.sessionid)
        check_req = sanitized_Request(posturl, posturl_data, headers)

        check_response = self._download_webpage(check_req, None,
                                                note='Confirming login')
        posturl='https://mp.weixin.qq.com/mp/videoplayer?vid=%s&mid=%s&idx=1&__biz=%s&sessionid=%sf=json'% (self.mpvid, self.mid,self.bid,self.sessionid)
        check_req = sanitized_Request(posturl, urlencode_postdata(posturl_data),headers)

        check_response = self._download_webpage(check_req, None,
                                                note='Confirming json')

        check_req = 'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_cover&vid=%s&mid=%s&idx=1&__biz=%s&sessionid=%s&f=json' % (
        self.mpvid, self.mid, self.bid, self.sessionid)
        check_response = self._download_json(check_req, self.video_id, headers=headers,
                                             note='json thumb')

        thumb=check_response['url']
        check_req = 'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_play_url&preview=0&vid=%s&mid=%s&idx=1&__biz=%s&sessionid=%s&f=json' % (
        self.mpvid, self.mid, self.bid, self.sessionid)
        check_response = self._download_json(check_req, self.video_id, headers=headers,
                                             note='json formats')

        #'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_play_url&preview=0&__biz=MzUxMDY1MDU5MA==&mid=2247564867&idx=2&vid=wxv_2021433135942434816&uin=&key=&pass_ticket=&wxtoken=777&devicetype=&clientversion=&__biz=MzUxMDY1MDU5MA%3D%3D&appmsg_token=&x5=0&f=json'
        #'https://mp.weixin.qq.com/mp/videoplayer?vid=wxv_2021433135942434816&mid=2247564867&idx=1&__biz=MzUxMDY1MDU5MA==&sessionid=svr_d1267e42c38&f=json'
        #self._download_webpage()
        forminfo=check_response['url_info']
        formats=[]
        duration=0
        for f in forminfo:
            formats.append(f)
            duration=int(f['duration_ms'])/1000
        self._sort_formats(formats);

        return {'id': self.video_id,
                'title': self.msg_title,
                'description': self.msg_desc ,
                'formats': formats,
                'thumbnail':thumb,
         }

class QPicEXTIE(QPicIE):
    _VALID_URL = r'https://(?:mp\.)?weixin\.qq\.com/s\?__biz=(?P<biz>[^&]+)&mid=(?P<mid>[^&]+)&idx=(?P<idx>[^&]+)&sn=(?P<sn>[^&]+)&chksm=(?P<chksm>[^&]+)&scene=(?P<scene>\d+)'


    def _real_extract(self, url):
        m=self._match_valid_url(url)
        self.bid=m.group('biz')
        self.mid=m.group('mid')
        self.idx=m.group('idx')
        self.sn=m.group('sn')
        self.chksm=m.group('chksm')
        self.scene=m.group('scene')
        self.video_id =self.chksm

        webpage = self._download_webpage(url,self.video_id)

        self.mid=self.  _robustregex('mid','(?P<id>[^"]+)',webpage)
        self.bid=self.  _robustregex('biz','(?P<id>[^"]+)',webpage)
        self.sessionid=self.  _robustregex('sessionid','(?P<id>[^"]+)',webpage)
        try:
            self.msg_title=self._search_regex(r'var msg_title = \'(?P<id>[^\']+)\'', webpage, 'msg_title',  group='id')
        except:
            self.msg_title =self.video_id
        try:
            self.msg_desc=self._search_regex(r'var msg_desc = htmlDecode\(\"(?P<id>[^\"]+)\"', webpage, 'msg_desc',  group='id')
        except:
            self.msg_desc =self.video_id

        self.mpvid=self._search_regex(
            r'data-mpvid="(?P<id>[^"]+)"', webpage, 'mpvid',
            group='id')

        cookies = self._get_cookies('https://mp.weixin.qq.com')
        self.Cookie=''
        for c in cookies:
            self.Cookie=self.Cookie+c+'='+cookies[c].value+'; '

        return self._continueextraction(url)
