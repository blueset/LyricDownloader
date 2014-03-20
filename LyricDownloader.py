#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Xin Wang
# @Date:   2014-03-20 19:58:41
# @Email:  i@wangx.in

import re
import requests
import xml.etree.ElementTree as ET


class LyricDownloader:

    def __conv(self, i):
        r = i % 0x100000000
        if i >= 0 and r > 0x80000000:
            r = r - 0x100000000
        if i < 0 and r < 0x80000000:
            r = r + 0x100000000
        return r

    def __dec_to_hex(self, dec):
        return str(hex(dec))[2:].upper()

    def __hex_string(self, key):
        key = key.strip().encode('utf_16_le')
        result = ''
        for i in key:
            c = ord(i)
            result += self.__dec_to_hex((c - c % 16) / 16)
            result += self.__dec_to_hex(c % 16)
        return result

    def __retrieve_lrc(self, artist, title, lrc_id):
        code = self.qianqian_code(artist, title, lrc_id)
        url = 'http://ttlrccnc.qianqian.com/dll/lyricsvr.dll?dl?Id=%s&Code=%s' % (lrc_id, code)
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36',
            'Host': 'ttlrccnc.qianqian.com',

        }
        r = requests.get(url, headers=header)
        if u'errcode' in r.text:
            return None
        return r.text

    def qianqian_code(self, artist, title, lrc_id):
        lrc_id = int(lrc_id)
        combined = (artist + title).encode('utf-8')
        length = len(combined)
        song = []
        for i in combined:
            char = repr(i)[3:5]
            song.append(int(char, 16))
        int_val1 = 0
        int_val2 = 0
        int_val3 = 0
        int_val1 = (lrc_id & 0x0000FF00) >> 8
        if lrc_id & 0xFF0000 == 0:
            int_val3 = 0xFF & ~int_val1
        else:
            int_val3 = 0xFF & ((lrc_id & 0x00FF0000) >> 16)
        int_val3 = int_val3 | ((0xFF & lrc_id) << 8)
        int_val3 = int_val3 << 8
        int_val3 = int_val3 | (0xFF & int_val1)
        int_val3 = int_val3 << 8
        if lrc_id & 0xFF000000 == 0:
            int_val3 = int_val3 | (0xFF & (~lrc_id))
        else:
            int_val3 = int_val3 | (0xFF & (lrc_id >> 24))

        u_bound = length - 1
        while u_bound >= 0:
            c = song[u_bound]
            if c >= 0x80:
                c -= 0x100
            int_val1 = (c + int_val2) & 0x00000000FFFFFFFF
            int_val2 = (int_val2 << (u_bound % 2 + 4)) & 0x00000000FFFFFFFF
            int_val2 = (int_val1 + int_val2) & 0x00000000FFFFFFFF
            u_bound -= 1
        u_bound = 0
        int_val1 = 0
        while (u_bound <= length - 1):
            c = song[u_bound]
            if c >= 128:
                c -= 256
            int_val4 = (c + int_val1) & 0x00000000FFFFFFFF
            int_val1 = (int_val1 << (u_bound % 2 + 3)) & 0x00000000FFFFFFFF
            int_val1 = (int_val1 + int_val4) & 0x00000000FFFFFFFF
            u_bound += 1
        int_val5 = self.__conv(int_val2 ^ int_val3)
        int_val5 = self.__conv(int_val5 + (int_val1 | lrc_id))
        int_val5 = self.__conv(int_val5 * (int_val1 | int_val3))
        int_val5 = self.__conv(int_val5 * (int_val2 ^ lrc_id))

        int_val6 = int_val5
        if int_val6 > 0x80000000:
            int_val5 = int_val6 - 0x100000000
        return int_val5

    def get_lyric_list(self, artist, title):
        url = 'http://ttlrccnc.qianqian.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' % (
            self.__hex_string(artist), self.__hex_string(title))
        r = requests.get(url)
        # print r.content
        root = ET.fromstring(r.content)
        lyrics = []
        for item in root:
            lyrics.append(item.attrib)
        return lyrics

    def get_plain(self, artist, title):
        lrc = self.get_lrc(artist, title)
        if lrc is None:
            return None
        plain = re.sub(r'\[[^\]].*?\]', '', lrc)
        plain = re.sub(r'\n+', '\n', plain)
        return plain

    def get_lrc(self, artist, title):
        lrc_list = self.get_lyric_list(artist, title)
        if not lrc_list:
            return None
        lrc_id = lrc_list[0]['id']
        lrc = self.__retrieve_lrc(artist, title, lrc_id)
        return lrc


if __name__ == '__main__':
    artist = u'布衣乐队'
    title = u'秋天'
    lrc = LyricDownloader()
    print lrc.get_plain(artist, title)
