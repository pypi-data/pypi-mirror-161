class OTMDeliverValues:
    OTM_MIN_BASKET_PRICE_MIN_VALUE = 1
    OTM_MIN_DELIVER_TIME_MIN_VALUE = 20
    OTM_MIN_DELIVER_TIME_MAX_VALUE = 55
    OTM_MAX_DELIVER_TIME_MIN_VALUE = 30
    OTM_MAX_DELIVER_TIME_MAX_VALUE = 65
    OTM_DELIVER_TIME_MULTIPLE_OF = 5


class TrendyolRegionStatus:
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class GetirRateLimits:
    OPEN_CLOSE_RATE_LIMITER = 30  # 30 saniye'de bir bu istek kullanılabilir.
    UPDATE_STATUS_RATE_LIMITER = 60  # 60 saniye'de bir bu istek kullanılabilir.


class GetirOrderStatus:
    CANCELLED = "cancel"
    PREPARE = "prepare"
    DELIVERED = "deliver"


class PlatformsOrderStatus:
    ACCEPTED = "Accepted"
    ON_DELIVERY = "OnDelivery"
    PREPARE = "Prepare"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class BrandsPlatformStatus:
    CLOSE = "Close"
    OPEN = "Open"


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
