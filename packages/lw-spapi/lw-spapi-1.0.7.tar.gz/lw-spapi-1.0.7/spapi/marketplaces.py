"""
Country    marketplaceId    Country code
Canada    A2EUQ1WTGCTBG2    CA
United States of America    ATVPDKIKX0DER    US
Mexico    A1AM78C64UM0Y8    MX
Brazil    A2Q3Y263D00KWC    BR
Europe

Country    marketplaceId    Country code
Spain    A1RKKUPIHCS9HS    ES
United Kingdom    A1F83G8C2ARO7P    GB
France    A13V1IB3VIYZZH    FR
Netherlands    A1805IZSGTT6HS    NL
Germany    A1PA6795UKMFR9    DE
Italy    APJ6JRA9NG5V4    IT
Sweden    A2NODRKZP88ZB9    SE
Poland    A1C3SOZRARQ6R3    PL
Turkey    A33AVAJ2PDY3EV    TR
United Arab Emirates    A2VIGQ35RCS4UG    AE
India    A21TJRUUN4KGV    IN
Far East

Country    marketplaceId    Country code
Singapore    A19VAU5U5O7RUS    SG
Australia    A39IBJ37TRP1C6    AU
Japan    A1VC38T7YXB528    JP
"""
from enum import Enum


class AWS_ENV(Enum):
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"


# BASE_URL = 'https://sandbox.sellingpartnerapi-na.amazon.com'

BASE_URL = 'https://sellingpartnerapi'


class Marketplaces(Enum):
    """Enumeration for MWS marketplaces, containing endpoints and marketplace IDs.
    Example, endpoint and ID for UK marketplace:
        endpoint = Marketplaces.UK.endpoint
        marketplace_id = Marketplaces.UK.marketplace_id
    """

    AE = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A2VIGQ35RCS4UG", "eu-west-1")
    DE = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1PA6795UKMFR9", "eu-west-1")
    PL = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1C3SOZRARQ6R3", "eu-west-1")
    EG = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "ARBP9OOSHTCHU", "eu-west-1")
    ES = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1RKKUPIHCS9HS", "eu-west-1")
    FR = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A13V1IB3VIYZZH", "eu-west-1")
    GB = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1F83G8C2ARO7P", "eu-west-1")
    IN = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A21TJRUUN4KGV", "eu-west-1")
    IT = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "APJ6JRA9NG5V4", "eu-west-1")
    NL = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1805IZSGTT6HS", "eu-west-1")
    SA = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A17E79C6D8DWNP", "eu-west-1")
    SE = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A2NODRKZP88ZB9", "eu-west-1")
    TR = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A33AVAJ2PDY3EV", "eu-west-1")
    UK = ("%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL}, "A1F83G8C2ARO7P", "eu-west-1")  # alias for GB

    AU = ("%(BASE_URL)s-fe.amazon.com" % {'BASE_URL': BASE_URL}, "A39IBJ37TRP1C6", "us-west-2")
    JP = ("%(BASE_URL)s-fe.amazon.com" % {'BASE_URL': BASE_URL}, "A1VC38T7YXB528", "us-west-2")
    SG = ("%(BASE_URL)s-fe.amazon.com" % {'BASE_URL': BASE_URL}, "A19VAU5U5O7RUS", "us-west-2")

    US = ("%(BASE_URL)s-na.amazon.com" % {'BASE_URL': BASE_URL}, "ATVPDKIKX0DER", "us-east-1")
    BR = ("%(BASE_URL)s-na.amazon.com" % {'BASE_URL': BASE_URL}, "A2Q3Y263D00KWC", "us-east-1")
    CA = ("%(BASE_URL)s-na.amazon.com" % {'BASE_URL': BASE_URL}, "A2EUQ1WTGCTBG2", "us-east-1")
    MX = ("%(BASE_URL)s-na.amazon.com" % {'BASE_URL': BASE_URL}, "A1AM78C64UM0Y8", "us-east-1")

    def __init__(self, endpoint, marketplace_id, region):
        """Easy dot access like: Marketplaces.endpoint ."""
        self.endpoint = endpoint
        self.marketplace_id = marketplace_id
        self.region = region


# 销售区域 API 端点
class RegionMarketplaces(Enum):
    # 北美（加拿大、美国、墨西哥和巴西商城）
    NA = (
        "%(BASE_URL)s-na.amazon.com" % {'BASE_URL': BASE_URL},
        (
            "ATVPDKIKX0DER", "A2Q3Y263D00KWC", "A2EUQ1WTGCTBG2", "A1AM78C64UM0Y8"
        ),
        "us-east-1"
    )

    # 欧洲（西班牙、英国、法国、荷兰、德国、意大利、土耳其、阿联酋和印度商城）
    EU = (
        "%(BASE_URL)s-eu.amazon.com" % {'BASE_URL': BASE_URL},
        (
            "A2VIGQ35RCS4UG", "A1PA6795UKMFR9", "A1C3SOZRARQ6R3", "ARBP9OOSHTCHU", "A1RKKUPIHCS9HS",
            "A13V1IB3VIYZZH", "A1F83G8C2ARO7P", "A21TJRUUN4KGV", "APJ6JRA9NG5V4", "A1805IZSGTT6HS",
            "A17E79C6D8DWNP", "A2NODRKZP88ZB9", "A33AVAJ2PDY3EV"
        ),
        "eu-west-1"
    )

    # 远东（新加坡、澳大利亚和日本商城）
    FE = (
        "%(BASE_URL)s-fe.amazon.com" % {'BASE_URL': BASE_URL},
        (
            "A39IBJ37TRP1C6", "A1VC38T7YXB528", "A19VAU5U5O7RUS"
        ),
        "us-west-2"
    )

    def __init__(self, endpoint, marketplace_ids, region_name):
        self.endpoint = endpoint
        self.marketplace_ids = marketplace_ids
        self.region_name = region_name
