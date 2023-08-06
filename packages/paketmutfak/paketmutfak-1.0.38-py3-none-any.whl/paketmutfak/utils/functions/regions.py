from paketmutfak.utils.constants.error_codes import MessageCode


def adress_coordinates_format_checker(address):

    if address.get("longitude") is None or address.get("latitude") is None:

        if address.get("full_address") is None or address.get("full_address") == "":

            if address.get("neighbourhood_name") is None or address.get("neighbourhood_name"):
                return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

            if not isinstance(address.get("neighbourhood_name"), str):
                return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

        else:
            if not isinstance(address.get("full_address"), str):
                return False, MessageCode.WRONG_DATA_ERROR_MESSAGE
    else:
        if not isinstance(address.get("longitude"), float) or \
                not isinstance(address.get("latitude"), float):
            return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    return True, ""


def check_otm_deliver_times(otm_data):

    if otm_data.get("max_delivery_time") - otm_data.get("min_delivery_time") != 10:
        return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_3

    return True, ""


def check_otm_update_deliver_data(otm_data, otm_time_information):

    if "min_deliver_time" in otm_data:

        if otm_data.get("min_deliver_time") % 5 != 0:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_2

        if "max_deliver_time" in otm_data:
            max_deliver_time = otm_data.get("max_deliver_time")
        else:
            max_deliver_time = otm_time_information.get("max_deliver_time")

        if max_deliver_time - otm_data.get("min_deliver_time") != 10:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_3

    if "max_deliver_time" in otm_data:

        if otm_data.get("max_deliver_time") % 5 != 0:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_2

        if "min_deliver_time" in otm_data:
            min_deliver_time = otm_data.get("min_deliver_time")
        else:
            min_deliver_time = otm_time_information.get("min_deliver_time")

        if otm_data.get("max_deliver_time") - min_deliver_time != 10:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_3

    return True, ""


def check_restaurant_deliver_data(rest_deliver_data):

    for rest_id, deliver_data in rest_deliver_data.items():
        if deliver_data.get("max_delivery_time") % 5 != 0 or \
                deliver_data.get("min_delivery_time") % 5 != 0:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_2

        if deliver_data.get("max_delivery_time") - deliver_data.get("min_delivery_time") != 10:
            return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_3

    return True, None
