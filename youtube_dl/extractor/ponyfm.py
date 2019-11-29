# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    try_get,
    unified_strdate,
    unified_timestamp
)


class PonyfmIE(InfoExtractor):
    _VALID_URL = r'''(?x)
                        (?:https?)://
                        (?:pony\.fm)/
                        (?:tracks)/
                        (?P<id>\d+)\-
                        (?P<display_id>[^\?]+)
                  '''
    _TESTS = [{
        'url': 'https://pony.fm/tracks/43462-summer-wind-fallout-equestria-skybolt',
        'md5': '9891bdffa040628ef7b7093fa4c3beb4',
        'info_dict': {
            'id': '43462',
            'ext': 'flac',
            'title': 'Summer Wind (Fallout: Equestria) - SkyBolt',
            'thumbnails': list,
            'description': 'md5:9b36840b55efc4e9e1229669f1f119d0',
            'uploader': 'SkyBoltsMusic',
            'uploader_id': 14407,
            'upload_date': '20191126',
            'timestamp': 1574746510,
            'uploader_url': 'https://pony.fm/skyboltsmusic',
            'channel': 'SkyBoltsMusic',
            'channel_id': 14407,
            'channel_url': 'https://pony.fm/skyboltsmusic',
            'view_count': 76,
            'like_count': 0,
            'duration': 180.13,
            'artist': 'SkyBoltsMusic',
            'genre': 'Swing'
        },
        'params': {
            'skip_download': True
        }
    }]

    def _real_extract(self, url):
        audio_id = self._match_id(url)
        api_url = 'https://pony.fm/api/web/tracks/' + audio_id
        json_data = self._download_json(api_url, audio_id)
        data = try_get(json_data, lambda x: x['track'], expected_type=dict)
        if data is None:
            raise ExtractorError('Track not found', video_id=audio_id, expected=True)
        
        thumbnail_list = try_get(data, lambda x: x['covers'], expected_type=dict)
        thumbnails = []
        for i, thumb in enumerate(thumbnail_list.items()):
            thumbnails.append({
                'url': thumb[1],
                'preference': -1 if "original" in thumb[1] else -2
            })

        timestamp = try_get(data, lambda x: x['published_at'], expected_type=str)

        uploader = try_get(data, lambda x: x['user']['name'], expected_type=str)
        uploader_id = try_get(data, lambda x: x['user']['id'], expected_type=int)
        uploader_url = try_get(data, lambda x: x['user']['url'], expected_type=str)
        
        description = try_get(data, lambda x: x['description'], expected_type=str)
        lyrics = try_get(data, lambda x: x['lyrics'], expected_type=str)
        
        formats = []
        format_list = try_get(data, lambda x: x['formats'], expected_type=list)
        for format in format_list:
            ext = format.get('extension')
            formats.append({
                'url': format.get('url'),
                'ext': ext,
                'format': format.get('name'),
                'preference': -2 if ext == 'mp3' else -1
            })
        self._sort_formats(formats)

        return {
            'id': audio_id,
            'display_id': try_get(data, lambda x: x['slug'], expected_type=str),
            'title': try_get(data, lambda x: x['title'], expected_type=str),
            'thumbnails': thumbnails,
            'description': "\nLYRICS:\n\n".join([description, lyrics]),
            'uploader': uploader,
            'timestamp': unified_timestamp(timestamp),
            'upload_date': unified_strdate(timestamp),
            'uploader_url': uploader_url,
            'uploader_id': uploader_id,
            'channel': uploader,
            'channel_id': uploader_id,
            'channel_url': uploader_url,
            'view_count': try_get(data, lambda x: x['stats']['plays'], expected_type=int),
            'like_count': try_get(data, lambda x: x['stats']['favourites'], expected_type=int),
            'duration': try_get(data, lambda x: float(x['duration']), expected_type=float),
            'artist': uploader,
            'genre': try_get(data, lambda x: x['genre']['name'], expected_type=str),
            'formats': formats
        }

    # TODO: add support for album download
