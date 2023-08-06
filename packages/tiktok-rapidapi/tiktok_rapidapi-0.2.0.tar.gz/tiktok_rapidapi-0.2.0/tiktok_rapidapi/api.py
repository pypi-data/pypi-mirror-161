"""
Daniil Kot, Telegram: @ktspn
Made with love and soul, as part of the work at Kotspin
"""
import asyncio
import time
from typing import List, Optional, Union, Dict, AnyStr
from urllib.parse import urlencode
from purl import URL

import aiohttp

from .schemas import TikTokCommentModel
from .schemas import TikTokUserModel
from .schemas import TikTokVideoModel


class TikTokRapidAPI(object):
    def __init__(self, rapidapi_host: AnyStr, rapidapi_key: AnyStr):
        """
        Buy a plan here: https://rapidapi.com/ponds4552/api/tiktok-best-experience/

        :param rapidapi_host: X-RapidAPI-Host header & Base URL
        :param rapidapi_key: X-RapidAPI-Key header
        """
        self.headers = {
            "X-RapidAPI-Host": rapidapi_host,
            "X-Rapidapi-User": rapidapi_key,
            "X-Rapidapi-Subscription": "custom",
        }
        self.rapidapi_host = rapidapi_host

    async def __get_request(self, path: AnyStr, params: Optional[Dict] = None) -> Dict:
        """

        :param path: Request path
        :param params: Request query parameters
        :return: JSON Response Dict
        """

        if params:
            query_string = urlencode(params)
        else:
            query_string = ""

        url = URL(
            host=self.rapidapi_host,
            path=path,
            query=query_string,
            scheme="https"
        ).as_string()

        while True:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url=url) as response:
                    try:
                        json_response = await response.json()
                    except aiohttp.client.ContentTypeError:
                        continue
                    if json_response.get('status') == "ok":
                        break
            await asyncio.sleep(0.2)

        response_data = json_response.get("data") or {}
        return response_data

    async def get_user_feed_by_username(self, username: AnyStr, max_cursor: int) -> List[
        TikTokVideoModel]:
        """
        You can GET a user's Feed by their Username.
        Method: /user/{username}/feed

        :param username: TikTok username (i.e. @redbull)
        :param max_cursor: Max cursor in timestamp milliseconds (i.e. 1630342868000)
        :return: List of TikTokVideoModel
        """
        params = {"max_cursor": str(max_cursor)}
        path = f"/user/{username}/feed"

        response_data = await self.__get_request(path=path, params=params)
        dict_videos = response_data.get("aweme_list") or []
        videos = [TikTokVideoModel.parse_obj(dict_video) for dict_video in dict_videos]

        return videos

    async def get_user_full_feed_by_username(self, username: AnyStr):
        """
        Using the has_more parameter, we get all the data.
        You can GET a user's Feed by their Username.
        Method: /user/{username}/feed

        :param username: TikTok username (i.e. @redbull)
        :return: List of TikTokVideoModel
        """
        max_cursor = int(time.time() * 1000)

        while True:
            params = {"max_cursor": str(max_cursor)}
            path = f"/user/{username}/feed"

            response_data = await self.__get_request(path=path, params=params)
            dict_videos = response_data.get("aweme_list") or []
            yield [TikTokVideoModel.parse_obj(dict_video) for dict_video in dict_videos]

            if not response_data.get("has_more") or not response_data.get("max_cursor"):
                break

            max_cursor = response_data.get("max_cursor")

    async def get_user_data_by_username(self, username: AnyStr) -> TikTokUserModel:
        """
        You can GET a user's Data by their Username.
        Method: /user/{username}

        :param username: TikTok username (i.e. @redbull)
        :return: TikTokUserModel object
        """
        path = f"/user/{username}"

        response_data = await self.__get_request(path=path)
        user = TikTokUserModel.parse_obj(response_data)

        return user

    async def get_user_feed_by_id(self, user_id: AnyStr, max_cursor: int) -> List[TikTokVideoModel]:
        """
        You can GET a user's Feed by their ID (uid/id).
        Method: /user/id/{id}/feed

        :param user_id: TikTok user ID (i.e. 6615502023793623045)
        :param max_cursor: Max cursor in timestamp milliseconds (i.e. 1630342868000)
        :return: List of TikTokVideoModel
        """
        params = {"max_cursor": str(max_cursor)}
        path = f"/user/id/{user_id}/feed"

        response_data = await self.__get_request(path=path, params=params)
        dict_videos = response_data.get("aweme_list") or []
        videos = [TikTokVideoModel.parse_obj(dict_video) for dict_video in dict_videos]

        return videos

    async def get_user_data_by_id(self, user_id: AnyStr) -> TikTokUserModel:
        """
        You can GET a user's Data (including uniqueId [username]) by their ID (uid/id).
        Method: /user/id/{id}

        :param user_id: TikTok user ID (i.e. 6615502023793623045)
        :return: TikTokUserModel object
        """
        path = f"/user/id/{user_id}"

        response_data = await self.__get_request(path=path)
        user = TikTokUserModel.parse_obj(response_data)

        return user

    async def get_video_data_by_url(self, video_url: AnyStr) -> TikTokVideoModel:
        """
        You can GET a Video by its URL.
        Method: /

        :param video_url: TikTok video URL (i.e. https://www.tiktok.com/@nike/video/6998558492558740742)
        :return: TikTokVideoModel object
        """
        params = {"url": str(video_url)}
        path = "/"

        response_data = await self.__get_request(path=path, params=params)
        video = TikTokVideoModel.parse_obj(response_data)

        return video

    async def get_video_data_by_id(self, video_id: AnyStr) -> TikTokVideoModel:
        """
        You can GET a Video by its ID.
        Method: /video/{id}

        :param video_id: TikTok video ID (i.e. 6998558492558740742)
        :return: TikTokVideoModel object
        """
        path = f"/video/{video_id}"

        response_data = await self.__get_request(path=path)
        if response_data:
            video = TikTokVideoModel.parse_obj(response_data)
            return video
        return None

    async def get_comments_by_video_id(self, video_id: AnyStr, max_cursor: int) -> List[TikTokCommentModel]:
        """
        You can GET video's Comments by its ID.
        Method: /user/id/{id}/feed

        :param video_id: TikTok Video ID (i.e. 7017394975730060545)
        :param max_cursor: Max cursor in comment count (i.e. 20)
        :return: List of TikTokCommentModel
        """
        params = {"max_cursor": str(max_cursor)}
        path = f"/comments/{video_id}"

        response_data = await self.__get_request(path=path, params=params)
        dict_comments = response_data.get("comments") or []
        if dict_comments:
            comments = [TikTokCommentModel.parse_obj(dict_comment) for dict_comment in dict_comments]
            return comments
        else:
            return []

    async def get_all_comments_by_video_id(self, video_id: AnyStr):
        """
        You can GET ALL video's Comments by its ID.
        Method: /user/id/{id}/feed

        :param video_id: TikTok Video ID (i.e. 7017394975730060545)
        :return: List of TikTokCommentModel
        """
        max_cursor = 0

        while True:
            params = {"max_cursor": str(max_cursor)}
            path = f"/comments/{video_id}"

            response_data = await self.__get_request(path=path, params=params)
            dict_comments = response_data.get("comments") or []
            yield [TikTokCommentModel.parse_obj(dict_comment) for dict_comment in dict_comments]

            if not response_data.get("has_more") or not response_data.get("cursor"):
                break

            max_cursor = response_data.get("cursor")
