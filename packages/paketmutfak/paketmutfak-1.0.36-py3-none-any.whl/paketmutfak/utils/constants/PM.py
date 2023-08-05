class OTMCommandTypes:
    COMMAND_TYPE_CREATE = "Oluşturma"
    COMMAND_TYPE_DELETE = "Silme"
    COMMAND_TYPE_UPDATE = "Düzenleme"
    COMMAND_TYPE_ACTIVATE = "Uygulanma"
    COMMAND_TYPE_FAIL = "Başarısız"


class OrderStatus:
    ROBOT = "ROBOT"
    SCHEDULED = "SCHEDULED"
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    ASSIGNED_TO_COURIER = "ASSIGNED_TO_COURIER"
    ON_THE_WAY = "ONTHEWAY"
    DELIVERED = "DELIVERED"
    NOT_DELIVERED = "NOTDELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class BasketStatus:
    PENDING = "PENDING"
    ASSIGNED_TO_COURIER = "ASSIGNED_TO_COURIER"
    READY_TO_ON_THE_WAY = "READY_TO_ONTHEWAY"
    ON_THE_WAY = "ONTHEWAY"
    COMPLETED = "COMPLETED"


class BillingStatus:
    PENDING = "PENDING"
    ZOMBIE = "ZOMBIE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CourierStatus:
    NOT_AVAILABLE = "NOT_AVAILABLE"
    PENDING = "PENDING"
    ASSIGNED_BASKET = "ASSIGNED_BASKET"
    READY_TO_ON_THE_WAY = "READY_TO_ONTHEWAY"
    ON_THE_WAY_TO_DELIVER = "ONTHEWAY_TO_DELIVER"
    ON_THE_WAY_TO_BASE = "ONTHEWAY_TO_BASE"


class TableNames:
    AUTHORIZATION_TYPES = "Authorization_Types"
    BASKETS = "Baskets"
    BASKETS_ORDERS = "Baskets_Orders"
    BASKET_STATUS = "Basket_Status"
    BILLING_STATUS = "Billing_Status"
    BRAND_PLATFORM_REGIONS = "Brand_Platform_Regions"
    BUILDING_PM_REGIONS_STATUS = "Building_PM_Regions_Status"
    BUILDINGS_EMPLOYEES = "Buildings_Employees"
    BUILDINGS_KITCHEN = "Buildings_Kitchen"
    CASH_ENTRY = "Cash_Entry"
    COMMAND_TYPES = "Command_Types"
    CONFIG_STORE = "Config_Store"
    COURIER_CONTRACT_TYPE = "Courier_Contract_Type"
    COURIER_OPERATION_HISTORY = "Courier_Operation_History"
    COURIERS_STATUS = "Couriers_Status"
    CUSTOMER_TYPES = "Customer_Types"
    DELIVERY_METHODS = "Delivery_Methods"
    END_OF_DAY_STATUS = "End_Of_Day_Status"
    ERROR_MESSAGES = "Error_Messages"
    KDS_TYPE = "Kds_Type"
    MEMBERS = "Members"
    MEMBERS_BRANDS = "Members_Brands"
    METADATA = "Metadata"
    ORDER_STATUS = "Order_Status"
    ORDER_TYPE = "Order_Type"
    ORDERS = "Orders"
    ORDERS_ARCHIVE = "Orders_Archive"
    OTM_PLATFORMS = "OTM_Platforms"
    OTM_REGIONS = "OTM_Regions"
    OTM_REGIONS_COMMANDS_HISTORY = "OTM_Regions_Commands_History"
    PAYMENT_LOCATION = "Payment_Locations"
    PAYMENT_METHODS = "Payment_Methods"
    PERMISSION_TYPES = "Permission_Types"
    PLATFORMS_PM_REGIONS = "Platform_Pm_Regions"
    PLATFORM_PRODUCTS = "Platform_Products"
    PLATFORM_PRODUCTS_OPTIONS = "Platform_Products_Options"
    PLATFORMS = "Platforms"
    PM_BUILDINGS = "PM_Buildings"
    PM_BUILDINGS_AREAS = "PM_Buildings_Areas"
    PM_REGIONS = "PM_Regions"
    PM_REGIONS_OF_OTM_REGIONS = "PM_Regions_of_OTM_Regions"
    PM_USERS = "Pm_Users"
    POS = "POS"
    POS_PAYMENT_METHOD = "POS_Payment_Method"
    PRODUCTS = "Products"
    PRODUCTS_CATEGORY = "Products_Category"
    PRODUCTS_OPTIONS = "Products_Options"
    RESTAURANTS = "Restaurants"
    RESTAURANTS_OF_OTM_REGIONS = "Restaurants_of_OTM_Regions"
    RESTAURANTS_PLATFORMS_INFORMATION = "Restaurants_Platforms_Information"
    TURKEY_ADDRESSES = "Turkey_Addresses"
    Z_ENTRY = "Z_Entry"
    ORDERS_SEARCH_RECORDS = "Orders_Search_Records"
    MAJOR_ERRORS = "Major_Errors"
    MAJOR_ERRORS_TYPE = "Major_Errors_Type"
    REQUESTS = "Requests"
    ACCESS_MODE = "Access_Mode"
    USER_PANEL_ACCESS = "User_Panel_Access"
    APPLICATIONS_PANELS = "Applications_Panels"
    PANEL_REQUESTS = "Panel_Requests"


class AccessModes:
    EDIT = "Düzenle"
    VIEW = "Görüntüle"
    UNAUTHORIZED = "Yetkisiz"


class CourierOperationTxnCodes:
    GPS = "CUR_GPS"
    CREATE_BASKET_AND_ASSIGN = "CUR_CREATE_BASKET_AND_ASSING"
    NOT_AVAILABLE = "CUR_NOT_AVAILABEL"
    RETURN_BUILDING = "CUR_RETURN_BUILDING"
    BASKET_ON_THE_WAY = "CUR_BASKET_ONTHEWAY"
    BASKET_CLEAR = "CUR_BASKET_CLEAR"
    ON_BUILDING = "CUR_ON_BUILDING"
    BASKET_FINISHED = "CUR_BASKET_FINISHED"
    ORDER_ON_THE_WAY = "CUR_ORDER_ONTHEWAY"
    ORDER_DELIVERED = "CUR_ORDER_DELIVERED"
    ORDER_NOT_DELIVERED = "CUR_ORDER_NOT_DELIVERED"


class PlatformIds:
    YS = 1
    GT = 2
    TY = 3


class PlatformNames:
    GT = "Getir"
    YS = "Yemeksepeti"
    TY = "Trendyol"
    PHONE = "Telefon ile Sipariş"
    HAND_DELIVERY = "Gel Al Siparişi"
    PM_EMPLOYEE = "Paket Mutfak Çalışan Siparişi"
    ADDITIONAL = "Ek Sipariş"


class BuildingRegionstatus:
    NOT_INTEGRATED = "NOT_INTEGRATED"
    NOT_CREATED = "NOT_CREATED"
    CREATED = "CREATED"
    COMPLETED = "COMPLETED"


class WorkingStatus:
    PASSIVE = 0
    ACTIVE = 1
    PENDING = 2


class CourierContractTypes:
    PART_TIME = "Part Time"
    FULL_TIME = "Full Time"


class OrderTypes:
    MANUEL_ORDER_WITH_PHONE = "MANUEL_ORDER_WITH_PHONE"
    HAND_DELIVERY = "HAND_DELIVERY_ORDER"
    EMPLOYEE = "EMPLOYEE_ORDER"
    PLATFORM = "PLATFORM"
    MANUEL_ORDER = "MANUEL_ORDER"
    ADDITIONAL = "ADDITIONAL_ORDER"


class EndOfDayStatus:
    PENDING = 'PENDING'
    STARTED = 'THE_DAY_STARTED'
    OVER = 'THE_DAY_OVER'


class DeliveryMethod:
    HAND_DELIVERY_TO_PM_EMPLOYEES = "HAND_DELIVERY_TO_PM_EMPLOYEES"
    PM_COURIER = "PM_COURIER"
    PLATFORM_COURIER = "PLATFORM_COURIER"
    HAND_DELIVERY = "HAND_DELIVERY"
    RESTAURANT_COURIER = "RESTAURANT_COURIER"


class PaymentLocations:
    ONLINE = "ONLINE"
    AT_THE_DOOR = "AT_THE_DOOR"
    AT_THE_RESTAURANT = "AT_RESTAURANT"


class UserTypes:
    BUILDING_MANAGER = "BUILDING_MANAGER"
    OPERATION_SPECIALIST = "OPERATION_SPECIALIST"
    OPERATION_DIRECTOR = "OPERATION_DIRECTOR"
    DIRECTOR_OF_SALES = "DIRECTOR_OF_SALES"
    COURIER_CHIEF = "COURIER_CHIEF"
    ACCOUNTING_DIRECTOR = "ACCOUNTING_DIRECTOR"
    ACCOUNTING_EMPLOYEE = "ACCOUNTING_EMPLOYEE"
    CRAFT = "CRAFT"
    KITCHENS_DIRECTOR = "KITCHENS_DIRECTOR"
    MARKETING_EMPLOYEE = "MARKETING_EMPLOYEE"
    CO_FOUNDER = "CO-FOUNDER"
    MEMBER = "MEMBER"
    KITCHEN_EMPLOYEE = "KITCHEN_EMPLOYEE"
    COURIER = "COURIER"


class UserTypesId:
    BUILDING_MANAGER = 1
    OPERATION_SPECIALIST = 2
    OPERATION_DIRECTOR = 3
    DIRECTOR_OF_SALES = 4
    COURIER_CHIEF = 5
    ACCOUNTING_DIRECTOR = 6
    ACCOUNTING_EMPLOYEE = 7
    CRAFT = 8
    KITCHENS_DIRECTOR = 9
    MARKETING_EMPLOYEE = 10
    CO_FOUNDER = 11
    MEMBER = 12
    KITCHEN_EMPLOYEE = 13
    COURIER = 14


class CustomerTypes:
    PM_EMPLOYEE = "PM-EMPLOYEE"
    PLATFORM_CUSTOMER = "PLATFORM-CUSTOMER"
    CUSTOMER = "CUSTOMER"


class KdsTypes:
    KDS_1 = "KDS_1"
    KDS_2 = "KDS_2"
    KDS_3 = "KDS_3"


PLATFORMS_DICT = {
    PlatformNames.YS: "1",
    PlatformNames.GT: "2",
    PlatformNames.TY: "3"
}

# todo: silinebilir

# class CancelledBillsContants:
#     EXCEL_NAME = "İptal_Adisyonlar"
#     PDF_NAME = "İptal_Adisyonlar"
#     BRAND = "Şube"
#     ORDER_NO = "Sipariş No"
#     BRAND_SHIPPING_COSTS = "Üye'den G.Ü Alınacak mi"
#     COURIER_BONUS = "Kuryeye Prim Verilecek mi"
#     DESCRIPTION = "Açıklama"
#     YES = "Evet"
#     NO = "Hayır"