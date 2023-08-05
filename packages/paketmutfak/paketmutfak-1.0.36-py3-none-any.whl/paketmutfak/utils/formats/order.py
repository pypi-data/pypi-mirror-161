from random import randint
from datetime import datetime
from paketmutfak.utils.functions.general import generate_uid


def get_pm_products_format():

    item = {
        "id": None,
        "name": None,
        "description": None,
        "price": None,
        "preparation_time": None,
        "title": None,
        "brand_id": None,
        "pm_restaurant_id": None
    }

    return item


def get_pm_products_options_format():

    item = {
        "id": None,
        "name": None,
        "product_id": None,
        "price": None,
        "type": None,
        "brand_id": None,
        "pm_restaurant_id": None
    }

    return item


def get_pm_options_format(option_id, name: str = None, price: str = None):
    item = {
        "id": option_id,
        "name": name,
        "price": price
    }

    return item


def get_pm_extra_ingredients_format(extra_ingredient_id, name: str = None, price: str = None):
    item = {
        "id": extra_ingredient_id,
        "name": name,
        "price": price
    }

    return item


def get_pm_removed_ingredients_format(removed_ingredient_id, name: str = None):
    item = {
        "id": removed_ingredient_id,
        "name": name
    }

    return item


def get_pm_order_products_format(product_id, name: str = None, quantity: str = None, note: str = None,
                                 price: str = None, unit_price: str = None, extra_ingredients=[],
                                 removed_ingredients=[], options=[], extra_products=[], order_index: str = ""):
    """
        ingredients içerisinde tüm order_products verilerini tutar. Nested şekilde ilerlemektedir.
    :return:
    """
    if product_id is None:
        product_id = "1"  # TODO: Doğru bir yaklaşım mı generate promotion id

    order_products = {
        "id": product_id,
        "hash-id": product_id + order_index,
        "name": name,
        "quantity": quantity,
        "note": note,
        "price": price,
        "unit_price": unit_price,
        "extra_ingredients": extra_ingredients,
        "removed_ingredients": removed_ingredients,
        "options": options,
        "products": extra_products
    }

    return order_products


def get_pm_order_products_json_format():
    return {"products": []}


def get_pm_promotions_format(promotion_id, name: str = None):
    if promotion_id is None:
        promotion_id = "1"  # TODO: Doğru bir yaklaşım mı generate promotion id

    promotions = {
        "id": promotion_id,
        "name": name
    }
    return promotions


def get_pm_promotions_json_format():
    return {"promotions": []}


def get_pm_dynamodb_order_format():
    order_time = datetime.now().astimezone().replace(microsecond=0).isoformat()
    order_id = generate_uid()

    item = {
        "order_id": order_id,
        "payments": {
            "note": None,
            "remaining_balance": None,
            "methods": [],
            "cancelation_info": {
                "description": None,
                "option": None
            },
            "has_courier_payment": "0",
            "has_restaurant_transfer_price": "0"
        },
        "edited_payments": [],
        "original_request": {},
        "payment_method": None,
        "platform_code": None,
        "building_name": None,
        "pm_region_id": None,
        "pm_region_name": None,
        "address_id": None,
        "pm_restaurant_id": None,
        "app_cancelation_note": None,
        "delivery_method": None,
        "delivery_status": "PENDING",
        "billing_status": "PENDING",
        "order_contents": None,
        "promotions": None,
        "courier_id": None,
        "customer_type": None,
        "order_type": None,
        "is_scheduled_order": "0",
        "platform_confirmation_code": None,
        "platform_delivery_price": None,
        "courier_app_operation": {
            "on_the_way": {
                "lat": None,
                "long": None,
                "created_at": None
            },
            "delivered": {
                "lat": None,
                "long": None,
                "created_at": None
            },
            "notdelivered": {
                "lat": None,
                "long": None,
                "created_at": None
            }
        },
        "is_dirty_payment": "0",
        "total_price": None,
        "discount_price": "0.00",
        "adisyon_no": None,
        "order_note": None,
        "platform_name": None,
        "payment_location": None,
        "customer_info": {
            "e-mail": None,
            "full_name": None,
            "address": {
                "city": None,
                "doorNumber": None,
                "district": None,
                "latitude": None,
                "address_description": None,
                "company": None,
                "full_address": None,
                "neighborhood": None,
                "floor": None,
                "email": None,
                "apartmentNumber": None,
                "longitude": None
            },
            "phone": []
        },
        "customer_handover_time": None,
        "preparation_starting_time": None,
        "average_preparation_time": str(randint(5, 20)),
        "preparation_end_time": None,
        "order_time": order_time,
        "courier_handover_time": None,
        "start_deliver_time": None,
        "print_count": "0",
        "updated_at": order_time,
        "created_at": order_time,
        "utc_date": str(datetime.now().astimezone().replace(microsecond=0).date()),
        "distance_between_building_and_order_address": None
    }

    return item

def get_constant_cancel_options():

    cancel_options_json = {"cancel_options": [
        {
            "id": "1",
            "name": "Müşteri istemedi."
        },
        {
            "id": "2",
            "name": "Malzemeler eksik."
        },
        {
            "id": "2",
            "name": "Elektrikler kesildi."
        }
    ]}

    return cancel_options_json


class TotalOrderStatus:
    def __init__(self):
        self.object = {
            'preparing': 0,
            'pending': 0,
            'ontheway': 0,
            'delivered': 0,
            'not_delivered': 0,
            'payment_completed': 0,
            'payment_cancelled': 0,
            'others': 0,
            'total': 0,
        }

    def update_status(self, order):
        self.object['total'] += 1

        if order['delivery_status'] == 'PREPARING':
            self.object['preparing'] += 1
        elif order['delivery_status'] == 'PREPARED':
            self.object['pending'] += 1
        elif order['delivery_status'] == 'ONTHEWAY':
            self.object['ontheway'] += 1
        elif order['delivery_status'] == 'DELIVERED':
            self.object['delivered'] += 1
        elif order['delivery_status'] == 'NOTDELIVERED':
            self.object['not_delivered'] += 1
        else:
            self.object['others'] += 1

        if order['billing_status'] == 'COMPLETED':
            self.object['payment_completed'] += 1
        if order['billing_status'] == 'CANCELLED':
            self.object['payment_cancelled'] += 1
