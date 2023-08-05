from datetime import datetime, timedelta
from random import randint, randrange
from uuid import uuid4
import iso8601 as iso8601
import slugify as slugify
from paketmutfak.utils.constants.error_codes import MessageCode
import re
import jwt
import math
from paketmutfak.utils.constants.PM import BillingStatus, OrderStatus
from paketmutfak.utils.constants.parameters import PAREKENDE_SATIS_FISI_LIMIT, TOLERANCE_PAYMENT, DYNAMO_DB_NULL_INDEX, \
    PAYMENT_PER_BASKET
from paketmutfak.utils.constants.platforms import BrandsPlatformStatus
from math import sin, radians, cos, asin, sqrt


def generate_uid():
    return datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())


def init_extra_log_params(log_id, sql_error_code=None, sql_statement=None, db_name=None, table_name=None,
                          request=None, args=None, error_code=None):

    extra_params = {"log_id": log_id}
    if sql_error_code is not None:
        extra_params["sql_error_code"] = sql_error_code
    if sql_statement is not None:
        extra_params["sql_statement"] = sql_statement
    if db_name is not None:
        extra_params["db_name"] = db_name
    if extra_params is not None:
        extra_params["table_name"] = table_name
    if request is not None:
        extra_params["request"] = request
    if args is not None:
        extra_params["args"] = args
    if error_code is not None:
        extra_params["error_code"] = error_code

    return extra_params


def date_format_checker(dates):
    if dates.get("start_date") is None or \
            dates.get("start_date") == "" or \
            dates.get("end_date") is None or \
            dates.get("end_date") == "":
        return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

    if not isinstance(dates.get("start_date"), str) or \
            not isinstance(dates.get("end_date"), str):
        return False, MessageCode.DATE_FORMAT_ERROR

    try:
        if not bool(datetime.strptime(dates.get("start_date"), "%Y-%m-%d")) or \
                not bool(datetime.strptime(dates.get("end_date"), "%Y-%m-%d")):
            return False, MessageCode.DATE_FORMAT_ERROR
    except Exception:
        return False, MessageCode.DATE_FORMAT_ERROR

    if dates.get("start_date") >= dates.get("end_date"):
        return False, MessageCode.START_END_DATE_ERROR

    return True, None


def generate_adisyon_no():
    return randint(10000, 99999)


def generate_basket_no():
    return randint(10000, 99999)


def edit_name_as_shorten(s):

    if type(s) != str:
        return s
    # split the string into db list
    split_list = s.split()
    if split_list[0] == "Joker" and split_list[1] == "-":
        # for yemekSepeti
        split_list = split_list[2:]
    elif split_list[0] == "Joker":
        split_list = split_list[1:]
    new = ""

    if len(split_list) < 2:
        return s

    # traverse in the list
    for i in range(len(split_list) - 1, 0, -1):
        s = split_list[i]
        # adds the capital first character
        new += (s[0].upper() + '.')
        break

    # l[-1] gives last item of list l. We
    # use title to print first character in
    # capital.
    last = ""
    for i in range(len(split_list) - 1):
        last += split_list[i].title() + " "
    last += new
    return last


def edit_phone_number_add_zero(phone_number):
    """
    This functions edit phone number as 05385133857,
    1-remove punctuation characters
    2-split last 10 digit
    3-then add 0 beginning of the number
    :param phone_number: Accepts all formatted numbers as strings
    :return: New phone number like as [0]538 513 38 57
    """
    try:
        new_phone_number = '0' + re.sub('[^A-Za-z0-9]+', '', phone_number)[-10:]
        # TODO: 0 sadece Tr code olan telefonlarda çalışması için koyuldu. Globalde generic olmalı
    except Exception as exp:
        print("Exception:", exp)
        return str(phone_number)
    else:
        return str(new_phone_number)


def generate_token():
    """
    This function generate token which have 24 hours expired time with RSA256 algorithm.
    To generate private and public key apply these steps on command line:
        1 - ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
        2 - openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
        3 - cat jwtRS256.key -> correspond private key
        4 - cat jwtRS256.key.pub -> correspond public key
    :return:
    """
    private_key = b'copy paste from 3.step'
    public_key = b'copy paste from 4.step'
    encoded = jwt.encode({"name": "Emre", "surname": "Ozgun",
                          'exp': datetime.utcnow() + timedelta(hours=24)}, private_key, algorithm="RS256")

    # To decode token use public key
    decoded = jwt.decode(encoded, public_key, algorithms=["RS256"])

    return decoded

"""
@application.errorhandler(400)
def bad_request(error):
    x = type(error.description)
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({'message_code': original_error.message}), 400)
    # handle other "Bad Request"-errors
    return error


@application.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'message_code': error.description}), 500)
"""


def find_distance_between_points(point_1, point_2):
    try:
        distance = math.sqrt((float(point_1[0]) - float(point_2[0]))**2 + (float(point_1[1]) - float(point_2[1]))**2)
    except Exception:
        return None
    else:
        return distance


def process_order_list_from_archive_for_general(order_list, result_object, member):
    yemeksepeti_count = 0
    getir_count = 0
    trendyol_count = 0
    gelal_count = 0
    personel_count = 0
    cancelled_count = 0

    # billing_status_index : 1 (pending,zombie,completed,cancelled)
    # delivery_method_index : 2
    # (1:pm_courier, 2:platform_courier, 3:hand_delivery,4:restaurant_courier,5:hand_delivery_to_pm_employees)
    # platform_name_index : 4
    for order in order_list:
        if order[1] == 'COMPLETED':
            if order[2] == '1' or order[2] == '2':
                if order[4] == 'YemekSepeti':
                    yemeksepeti_count += 1
                if order[4] == 'Getir':
                    getir_count += 1
                if order[4] == 'Trendyol':
                    trendyol_count += 1
            if order[2] == '3':
                gelal_count += 1
            if order[2] == '5':
                personel_count += 1
        if order[1] == 'CANCELLED':
            cancelled_count += 1

    orde_count = yemeksepeti_count + getir_count + trendyol_count + gelal_count + personel_count + cancelled_count

    result_object['member_list'].append({
        'member_name': member[1],
        'yemeksepeti_count': yemeksepeti_count,
        'getir_count': getir_count,
        'trendyol_count': trendyol_count,
        'gelal_count': gelal_count,
        'personel_count': personel_count,
        'cancelled_count': cancelled_count,
        'member_total': orde_count
    })

    result_object['total'] = {
        'yemeksepeti_total': result_object['total']['yemeksepeti_total'] + yemeksepeti_count,
        'getir_total': result_object['total']['getir_total'] + getir_count,
        'trendyol_total': result_object['total']['trendyol_total'] + trendyol_count,
        'gelal_total': result_object['total']['gelal_total'] + gelal_count,
        'personel_total': result_object['total']['personel_total'] + personel_count,
        'cancelled_total': result_object['total']['cancelled_total'] + cancelled_count,
        'total': result_object['total']['total'] + orde_count
    }

    return ''


def process_order_list_from_archive_for_members(order_list, result_object, member):
    pm_total_order = 0
    not_delivery_fee = 0

    # billing_status_index : 1 (pending,zombie,completed,cancelled)
    # delivery_method_index : 2
    # (1:pm_courier,2:platform_courier,3:hand_delivery,4:restaurant_courier,5:hand_delivery_to_pm_employees)
    # has_restaurant_transfer_payment_index : 4 (1,0)
    for order in order_list:
        if order[1] == 'COMPLETED':
            if order[2] == '1':
                pm_total_order += 1
        if order[4] == 0:
            not_delivery_fee += 1

    result_object['member_list'].append({
        'member_name': member[1],
        'pm_total_order': pm_total_order,
        'not_delivery_fee': not_delivery_fee,
        'member_total': pm_total_order - not_delivery_fee
    })

    result_object['total'] = {
        'pm_total_order': result_object['total']['pm_total_order'] + pm_total_order,
        'not_delivery_fee': result_object['total']['not_delivery_fee'] + not_delivery_fee,
        'total': result_object['total']['total'] + pm_total_order - not_delivery_fee
    }

    return ''


def process_order_list_from_archive_for_couriers(order_list, result_object, courier):
    pm_couriers_total_order = 0
    not_courier_payment = 0
    courier_payment = 0

    # billing_status_index : 1 (pending,zombie,completed,cancelled)
    # delivery_method_index : 2
    # (1:pm_courier,2:platform_courier,3:hand_delivery,4:restaurant_courier,5:hand_delivery_to_pm_employees)
    # has_courier_payment : 4 (1,0)
    for order in order_list:
        if order[1] == 'COMPLETED':
            if order[2] == '1':
                pm_couriers_total_order += 1
                if order[4] == 1:
                    courier_payment += 1
                else:
                    not_courier_payment += 1

    result_object['courier_list'].append({
        'courier_name': courier[1],
        'pm_couriers_total_order': pm_couriers_total_order,
        'not_courier_payment': not_courier_payment,
        'courier_payment': courier_payment,
        'total_payment': courier_payment * PAYMENT_PER_BASKET,
    })

    result_object['total'] = {
        'pm_couriers_total_order': result_object['total']['pm_couriers_total_order'] + pm_couriers_total_order,
        'not_courier_payment': result_object['total']['not_courier_payment'] + not_courier_payment,
        'courier_payment': result_object['total']['courier_payment'] + courier_payment,
        'total_payment': result_object['total']['total_payment'] + courier_payment * PAYMENT_PER_BASKET
    }

    return ''


def check_dates_validation(start_date, end_date):
    return False if start_date > end_date else True


# this method get payment object by uniq_brand
def update_payments(current_payment_obj, row):
    edited_payments = row['edited_payments']

    if edited_payments and len(edited_payments) >= 1:
        payments = edited_payments[len(edited_payments) - 1]['payments']
        for payment in payments:
            if payment['name'] == 'Online Satış Kanalları':
                payment['name'] = 'Online Satış Kanalları-' + row['platform_name']

            if payment['name'] in current_payment_obj:
                current_payment_obj[payment['name']]['total_price'] += float(payment['price'])
            else:
                current_payment_obj[payment['name']] = {'payment': payment['name'],
                                                        'platform': row['platform_name'],
                                                        'total_price': float(payment['price'])}
    else:
        current_payment_obj['WRONG_ARCHIVE_DATA'] = {'payment': 'WRONG_PAYMENT_TYPE',
                                                     'platform': row['platform_name'],
                                                     'total_price': float(row['total_price'])}

    return current_payment_obj


def check_payments_price_with_total_price(payment_methods: dict, total_price: float):
    try:
        payments_total_price = sum([float(payment.get("price")) for payment in payment_methods])
    except KeyError as keyErr:
        return False, str(keyErr)
    except ValueError as valErr:
        return False, str(valErr)
    except Exception as exp:
        return False, str(exp)
    else:
        msg = "Payments price and total price are not incompatible"
        return [True, "OK"] \
            if float(abs(float(payments_total_price) - float(total_price))) <= TOLERANCE_PAYMENT else [False, msg]


def check_price_format(price):
    """
        This function check price available for decimal and two digit after dot '.'
    :param price: str
    :return:
    """
    if price is None or price == "":
        return False, MessageCode.PRICE_FORMAT_ERROR

    if re.match(r'^\d{0,5}(\.\d{1,10})?$', price) is None:
        return False, MessageCode.PRICE_FORMAT_ERROR
    else:

        price = str(round(float(price), 2))
        if float(price) > PAREKENDE_SATIS_FISI_LIMIT:
            return False, MessageCode.PERAKENDE_PRICE_LIMIT_ERROR
        else:
            return True, price


def check_payment(payment: dict):
    """
        '{ "name": "CIO Kart", "note": "", "id": "12", "code": "CIOKT", "price": "71.4"}'
        This function check payment available as above format
    :param payment: object
    :return:
    """
    if not isinstance(payment, object):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    payment_price = payment.get('price')
    price_format, price_data = check_price_format(price=payment_price)
    if price_format is False:
        return False, price_data
    else:
        payment['price'] = price_data

    return True, payment


def check_if_exist_other_pending_billing_status_on_basket(basket, current_order_id):
    for order in basket.get('orders'):
        if current_order_id != order.get('order_id') and order.get('billing_status') == BillingStatus.PENDING:
            return True
    return False


def check_payment_methods(methods):
    if not isinstance(methods, list):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    new_methods = []
    for method in methods:
        payment_check, payment_data = check_payment(method)
        if payment_check is False:
            return False, payment_data
        else:
            new_methods.append(payment_data)

    return True, new_methods


"""
from datetime import datetime
from pytz import timezone
import iso8601


now_datetime = datetime.now().astimezone().replace(microsecond=0)

converted_datetime = now_datetime.astimezone(timezone('Asia/Kolkata')) #timezone'u çeviriyor
str_converted_datetime = converted_datetime.isoformat() # stringe çevirmek için
str_to_datetime_converted = iso8601.parse_date(str_converted_datetime) # çevrilmiş stringi geri datetime yapmak
"""


def difference_datetime_as_sec(first_date, second_date):
    """
    :param first_date: isoformat 8601 datetime
    :param second_date: isoformat 8601 datetime
    :return: second as float
    """
    try:
        datetime_first = iso8601.parse_date(first_date)
        datetime_second = iso8601.parse_date(second_date)
    except Exception as exp:
        print("Wrong format first_date, second_date. ", exp)
        return None
    else:
        return (datetime_first - datetime_second).total_seconds()


def order_type_format_checker(order_type):

    if order_type is None or order_type == "":
        return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

    if not isinstance(order_type, str):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    if order_type != OrderStatus.PENDING and order_type != OrderStatus.PREPARING and order_type != OrderStatus.PREPARED:
        return False, MessageCode.INVALID_ORDER_TYPE_ERROR

    return True, ""


def update_order_status_format_checker(order_status):
    if order_status is None or order_status == "":
        return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

    if not isinstance(order_status, str):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    if order_status != OrderStatus.PENDING and \
            order_status != OrderStatus.PREPARING and \
            order_status != OrderStatus.PREPARED and \
            order_status != OrderStatus.CANCELLED:
        return False, MessageCode.INVALID_ORDER_TYPE_ERROR

    return True, ""


def rest_open_close_format_checker(rest_status):
    if rest_status is None or rest_status == "":
        return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

    if not isinstance(rest_status, str):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    if rest_status != BrandsPlatformStatus.OPEN and \
            rest_status != BrandsPlatformStatus.CLOSE:
        return False, MessageCode.INVALID_RESTAURANT_STATUS_ERROR

    return True, ""


def extract_dates_as_str(date_1: str, date_2: str):
    try:
        x = datetime.strptime(date_1, "%Y-%m-%dT%H:%M:%S%z") - datetime.strptime(date_2, "%Y-%m-%dT%H:%M:%S%z")
    except TypeError:
        return 0.0
    except Exception:
        return 0.0
    else:
        return x.total_seconds()


def edit_phone_number(phone: str):

    if type(phone) != str:
        return False, ""
    elif len(phone) == 10 and phone.isdigit():
        return True, phone
    elif len(phone) == 11 and phone.isdigit() and phone[0] == "0":
        return True, phone[1:]
    else:
        return False, ""


def check_param(param):
    if param is None:
        return DYNAMO_DB_NULL_INDEX
    elif (type(param) != str) and (type(param) != dict):
        return DYNAMO_DB_NULL_INDEX
    elif param == '':
        return DYNAMO_DB_NULL_INDEX
    elif type(param) == dict:
        param = {
            'latitude': str(param.get('latitude')),
            'longitude': str(param.get('longitude')),
            'speed': str(param.get('speed')),
            'heading': str(param.get('heading')),
            'altitude': str(param.get('altitude')),
            'accuracy': str(param.get('accuracy')),
            'altitudeAccuracy': str(param.get('altitudeAccuracy'))
        }
        return param
    else:
        return param


def check_price_diff(price_1, price_2):
    """
        if price_1 bigger than price_2 is True, otherwise is False
    """
    try:
        float_price_1 = float(price_1)
        float_price_2 = float(price_2)

        if float_price_1 >= float_price_2:
            return True, "is_valid"
        else:
            return False, MessageCode.DISCOUNT_PRICE_BIGGER_THAN_TOTAL
    except Exception:
        return False, MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE


def sum_two_price(price_1, price_2):
    try:
        float_price_1 = float(price_1)
        float_price_2 = float(price_2)

        total_price = str(float_price_1 + float_price_2)
    except Exception:
        return False, MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE
    else:
        return True, total_price


def check_otm_deliver_times(otm_data):

    if otm_data.get("max_delivery_time") - otm_data.get("min_delivery_time") != 10:
        return False, MessageCode.MAX_AND_MIN_DELIVERY_TIME_ERROR_3

    if not otm_data.get("default_preparation_time").isdigit() and int(otm_data.get("default_preparation_time")) < 0:
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE
    return True, ""


def is_valid_email(email):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|db-z]{2,}\b'

        if re.fullmatch(regex, email):
            return True
        else:
            return False
    except Exception:
        return False


def check_phone_number_format(phone_number):
    """
        :param phone_number: must be 10 digit
        :return:
    """
    if type(phone_number) != str:
        return False
    elif len(phone_number) != 10:
        return False

    return True


def generate_user_name(usernames, name, surname):
    try:
        count = 0
        new_user_name = name + "_" + surname
        new_user_name = slugify(new_user_name).lower()

        new_user_name_temp = new_user_name

        while 1:
            if new_user_name_temp not in usernames:
                return new_user_name_temp
            else:
                count += 1
                new_user_name_temp = new_user_name + str(count)
    except Exception:
        return None


def generate_otp_password_message():
    """
        This function generate one-time password message.
        Return: 1 - message with otp code for mail body
                2 - subject for mail
                3 - otp generated time as iso format
                4 - generated otp code
    """
    subject_caption = "ŞİFRE YENİLEME HAKKINDA"
    generated_number = randrange(100000, 1000000)
    generated_number_str = str(generated_number)
    otp_generated_time = datetime.now().astimezone().replace(microsecond=0).isoformat()
    message = f"Giriş yapmanız için geçici şifreniz: {generated_number_str}"

    return message, subject_caption,  otp_generated_time, generated_number


def calculate_distance_and_work_time_by_location_list(location_list):
    time = timedelta(seconds=0)
    total = 0
    first_lat = float(location_list[0]['latitude'])
    first_lon = float(location_list[0]['longitude'])

    first_time = location_list[0]['created_at']

    for x in range(1, len(location_list)):
        lat = float(location_list[x]['latitude'])
        lon = float(location_list[x]['longitude'])
        total += haversine_distance(first_lat, first_lon, lat, lon)
        first_lat = lat
        first_lon = lon

        current_time = datetime.strptime(location_list[x]['created_at'], "%Y-%m-%d %H:%M:%S")
        time += (current_time - first_time)
        first_time = current_time

    return total * 1000, time


def haversine_distance(lat1, lon1, lat2, lon2):
    """
        Calculate the great circle distance in kilometers between two points
        on the earth (specified in decimal degrees)
        """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def my_dict(obj):
    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(my_dict(item))
        else:
            element = my_dict(val)
        result[key] = element
    return result


def platform_id_format_checker(platform_id, platform_ids):

    if platform_id is None or platform_id == "":
        return False, MessageCode.MISSING_DATA_ERROR_MESSAGE

    if not isinstance(platform_id, str):
        return False, MessageCode.WRONG_DATA_ERROR_MESSAGE

    if platform_id not in platform_ids:
        return False, MessageCode.PLATFORM_NOT_FOUND

    return True, ""
