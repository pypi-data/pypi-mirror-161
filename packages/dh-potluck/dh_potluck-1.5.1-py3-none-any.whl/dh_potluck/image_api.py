import base64
from enum import Enum

from flask import current_app

DEFAULT_PROD_CDN_URLS = ['https://dashhudson-static.s3.amazonaws.com', 'https://cdn.dashhudson.com']
DEFAULT_PROD_IMAGE_API_URL = 'https://images.dashhudson.com'
DEFAULT_DEV_IMAGE_API_URL = 'https://images.dhdev.io'


class ImageApi:
    class FitType(Enum):
        INSIDE = 'inside'
        COVER = 'cover'

    @classmethod
    def build_url(
        cls,
        url_orig: str,
        w: int = None,
        h: int = None,
        fit: FitType = None,
        download: bool = False,
        extension: str = 'jpg',
    ):
        """
        Returns a formatted URL to the Image API service
        :param url_orig: String, full URL to Dash Hudson image
            e.g. https://dashhudson-dev.s3.amazonaws.com/images/items/1532976128.41429521549.jpeg
        :param w: Int, requested width
        :param h: Int, requested height
        :param fit: FitType, how the image should be fit into the dimensions
            INSIDE: fit the image inside the bounds, maintaining aspect ratio
            COVER: fit the image to the size of the box, using a center crop if necessary
        :param download: Bool, flag that's sent to the image API to receive a download header,
            default False
        :param extension: String, image file extension, default 'jpg'
        """
        host = cls._get_image_api_host_for_url(url_orig)

        url = url_orig.encode('utf-8')
        url_bytes = base64.urlsafe_b64encode(url)
        encoded_path = str(url_bytes, 'utf-8')

        params = []
        if w is not None:
            params.append(f'w={w}')
        if h is not None:
            params.append(f'h={h}')
        if fit is not None:
            params.append(f'fit={fit.value}')
        if download:
            params.append('download=true')

        param_string = f'?{"&".join(params)}' if len(params) > 0 else ''

        return f'{host}/{encoded_path}.{extension}{param_string}'

    @classmethod
    def _get_image_api_host_for_url(cls, url_orig):
        prod_cdn_urls = current_app.config.get(
            'DH_POTLUCK_PROD_IMAGE_CDN_URLS', DEFAULT_PROD_CDN_URLS
        )
        for cdn_url in prod_cdn_urls:
            if url_orig.startswith(cdn_url):
                host = current_app.config.get(
                    'DH_POTLUCK_PROD_IMAGE_API_URL', DEFAULT_PROD_IMAGE_API_URL
                )
                break
        else:
            host = current_app.config.get('DH_POTLUCK_DEV_IMAGE_API_URL', DEFAULT_DEV_IMAGE_API_URL)
        return host
