import os
from mobio.libs.caching import LruCache, StoreType
from mobio.sdks.admin import MobioAdminSDK


class CommonMerchant:
    MERGE_WHEN = 0.95
    PREFIX_DYNAMIC_FIELD = "_dyn"
    PREFIX_CRITERIA = "cri"
    ADMIN_HOST = os.environ.get("ADMIN_HOST")
    MOBIO_TOKEN = "Basic " + os.environ.get("YEK_REWOP", "f38b67fa-22f3-4680-9d01-c36b23bd0cad")


class ProfileStructure:
    THIRD_PARTY_INFO = "third_party_info"
    PROFILE_GROUP = "profile_group"
    BUSINESS_CASE_ID = "business_case_id"
    SOURCE_ID = "source_id"
    SOURCE_TYPE = "source_type"
    MERCHANT_ID = "merchant_id"
    PROFILE_ID = "profile_id"
    CREATED_TIME = "created_time"
    UPDATED_TIME = "updated_time"
    EMAIL = "email"
    EMAIL_1 = "email_1"
    EMAIL_2 = "email_2"
    PHONE_NUMBER = "phone_number"
    PHONE_NUMBER_1 = "phone_number_1"
    PHONE_NUMBER_2 = "phone_number_2"
    SOCIAL_USER = "social_user"
    SOCIAL_NAME = "social_name"
    SOCIAL_ID = "social_id"
    ID_SOCIAL = "id_social"
    SOCIAL_TYPE = "social_type"
    SOCIAL_ID_TYPE = "social_id_type"
    PEOPLE_ID = "people_id"
    IDENTIFY_CODE = "identify_code"
    DRIVER_LICENSE = "driver_license"
    PASSPORT = "passport"
    IS_COMPANY = "is_company"
    TAX_CODE = "tax_code"
    TAX_NAME = "tax_name"
    TAX_ADDRESS = "tax_address"
    LAT = "lat"
    LON = "lon"
    CREATED_ACCOUNT_TYPE = "created_account_type"
    BANK_ACC = "bank_acc"
    GENDER = "gender"
    BIRTHDAY = "birthday"
    BIRTH_YEAR = "birth_year"
    BIRTH_DATE = "birth_date"
    BIRTH_MONTH = "birth_month"
    BIRTH_MONTH_DATE = "birth_month_date"
    MARITAL_STATUS = "marital_status"
    NAME = "name"
    DISPLAY_NAME = "display_name"
    PASSWORD = "password"
    ADDRESS = "address"
    PROFILE_ADDRESS = "profile_address"
    PROVINCE_CODE = "province_code"
    DISTRICT_CODE = "district_code"
    WARD_CODE = "ward_code"
    FAX = "fax"
    OPERATION = "operation"
    JOB = "job"
    HOBBY = "hobby"
    TAGS = "tags"
    TAGS_SEARCH = "tags_search"
    PROFILE_TAGS = "profile_tags"
    RELIGIOUSNESS = "religiousness"
    NATION = "nation"
    AVATAR = "avatar"
    COMPANY = "company"
    FACE_ID = "face_id"
    INCOME_LOW_THRESHOLD = "income_low_threshold"
    INCOME_HIGH_THRESHOLD = "income_high_threshold"
    INCOME_TYPE = "income_type"
    BUDGET_LOW_THRESHOLD = "budget_low_threshold"
    BUDGET_HIGH_THRESHOLD = "budget_high_threshold"
    FREQUENTLY_DEMANDS = "frequently_demands"
    LST_PHONE_DELETED = "lst_phone_deleted"
    LST_EMAIL_DELETED = "lst_email_deleted"
    DEGREE = "DEGREE".lower()
    INCOME_FAMILY = "income_family"
    RELATIONSHIP_DATA = "relationship_data"
    RELATION_WITH_CHILDS = "relation_with_childs"
    CHILDS = "CHILDS".lower()
    NUMBER_CHILDS = "number_childs"
    CHILD_ID = "child_id"
    NTH = "nth"
    CUSTOMER_ID = "customer_id"
    CUSTOMER_CREATED_TIME = "customer_created_time"
    PARTNER_POINT = "partner_point"
    IS_STAFF_UPDATE = "is_staff_update"
    SOCIAL_TAGS = "social_tags"
    LENDING_LIMIT = "lending_limit"
    SOURCE = "source"
    PRIMARY_EMAIL = "primary_email"
    SECONDARY_EMAILS = "secondary_emails"
    PRIMARY_PHONE = "primary_phone"
    SECONDARY_PHONES = "secondary_phones"
    PREDICT = "predict"
    IS_NON_PROFILE = "is_non_profile"
    CARD = "card"
    CARDS = "cards"
    PUSH_ID = "push_id"
    POINT = "point"
    RANK_POINT = "rank_point"
    AGE = "age"
    DEVICES = "devices"
    TAGS_INTERACTIVE = "tags_interactive"
    SALARY = "salary"
    CIF_CODE = "cif"
    CLV = "clv"
    NUMBER_TRANSACTION = "number_transactions"
    PROFILE_IDENTIFY = "profile_identify"
    LAST_PAYMENT = "last_payment"
    MERGEABLE = "mergeable"
    DEVICE_TYPES = "device_types"
    ISP = 'isp'
    HIDDEN_AUDIENCE = "hidden_audience"


class ProfileByIdentifyStructure:
    MERCHANT_ID = "merchant_id"
    PROFILE_ID = "profile_id"
    IDENTIFY_VALUE = "identify_value"
    IDENTIFY_TYPE = "identify_type"
    IS_VERIFY = "is_verify"
    DATE_VERIFY = "date_verify"


class Device:
    DEVICE_ID = "device_id"
    SOURCE = "source"
    DEVICE_NAME = "device_name"


class DeviceTypeStructure:
    DEVICE_TYPE = "device_type"
    DEVICE_NAME = "device_name"


class ProfileTagsStructure:
    ID = "id"
    TAG = "tag"
    TAG_TYPE = "tag_type"
    MERCHANT_ID = "merchant_id"


class TagInteractiveStructure:
    TAG_ID = "tag_id"
    INTERACTIVE_TOTAL = "interactive_total"
    INTERACTIVE_3_DAYS = "interactive_3_day"
    INTERACTIVE_7_DAYS = "interactive_7_day"
    INTERACTIVE_30_DAYS = "interactive_30_day"
    LAST_ACTION_TIME = "last_action_time"


class Environment:
    HOST = 'HOST'
    ADMIN_HOST = 'ADMIN_HOST'
    REDIS_URI = 'REDIS_URI'
    REDIS_HOST = 'REDIS_HOST'
    REDIS_PORT = 'REDIS_PORT'
    KAFKA_BROKER = 'KAFKA_BROKER'


class MobioModuleHost:
    PROFILING_HOST = "profiling_host"
    PROFILING_APP_API_SERVICE_HOST = "profiling-v4-app-api-service-host"
    PROFILING_APP_INTERNAL_SERVICE_HOST = "profiling-v4-app-internal-api-service-host"
    PROFILING_APP_EXTERNAL_SERVICE_HOST = "profiling-v4-app-external-api-service-host"

    USER_EVENT_HOST = "event_host"
    USER_EVENT_APP_API_SERVICE_HOST = "user-event-app-api-service-host"

    ADS_HOST = "ads_host"
    ADS_APP_API_SERVICE_HOST = "ads-app-api-service-host"

    AU_HOST = "au_host"
    AU_APP_API_SERVICE_HOST = "audience-app-api-service-host"
    AU_v2_APP_API_SERVICE_HOST = "audience-v2-app-api-service-host"

    BASE_HOST = "base_host"

    CHATTOOL_HOST = "chattool_host"
    CHATTOOL_APP_API_SERVICE_HOST = "chattool-app-api-service-host"
    CHATTOOL_APP_SOCKET_SERVICE_HOST = "chattool-app-socket-service-host"

    CRM_HOST = "crm_host"

    EMK_HOST = "emk_host"
    EMK_APP_API_SERVICE_HOST = "emk-app-api-service-host"

    LOYALTY_HOST = "loyalty_host"
    LOYALTY_API_APP_SERVICE_HOST = "loyalty-api-app-service-host"
    LOYALTY_API_EXTERNAL_SERVICE_HOST = "loyalty-api-external-service-host"
    LOYALTY_API_MINIPOS_APP_SERVICE_HOST = "loyalty-api-minipos-app-service-host"
    LOYALTY_API_MOBILE_APP_SERVICE_HOST = "loyalty-api-mobile-app-service-host"
    LOYALTY_API_TRANSACTION_APP_SERVICE_HOST = "loyalty-api-transaction-app-service-host"

    MKT_HOST = "mkt_host"

    NM_HOST = "nm_host"
    NM_APP_API_NOTIFICATION_SERVICE_HOST = "nm-app-api-notification-service-host"
    NM_APP_API_ONPREMISE_SERVICE_HOST = "nm-app-api-onpremise-service-host"
    NM_APP_API_SEND_MESSAGE_SERVICE_HOST = "nm-app-api-send-message-service-host"
    NM_APP_API_SERVICE_HOST = "nm-app-api-service-host"
    NM_APP_SOCKET_SERVICE_HOST = "nm-app-socket-service-host"
    NM_APP_WEB_API_SERVICE_HOST = "nm-app-web-api-service-host"

    SALE_HOST = "sale_host"
    SALE_API_APP_SERVICE_HOST = "sale-api-app-service-host"
    SALE_API_FILTER_APP_SERVICE_HOST = "sale-api-filter-app-service-host"
    SALE_API_REPORT_APP_SERVICE_HOST = "sale-api-report-app-service-host"

    SOCIAL_HOST = "social_host"
    SOCIAL_API_APP_SERVICE_HOST = "social-api-app-service-host"
    SOCIAL_REPORT_APP_SERVICE_HOST = "social-reports-app-service-host"

    TICKET_HOST = "ticket_host"
    TICKET_APP_API_SERVICE_HOST = "ticket-app-api-service-host"


lru_cache = LruCache(
    store_type=StoreType.REDIS,
    # config_file_name=APP_CONFIG_FILE_PATH,
    cache_prefix="profiling_mf",
    redis_uri=os.getenv(Environment.REDIS_URI),
)


p_mf_admin_sdk = MobioAdminSDK()
p_mf_admin_sdk.config(
    admin_host=os.getenv(Environment.ADMIN_HOST),  # admin host
    redis_uri=os.getenv(Environment.REDIS_URI),  # redis uri
    module_use="profiling_mf",  # liên hệ admin để khai báo tên của module
    module_encrypt="gw5HNauilRF1ZqWZhuJeYz6+CuCA4gba752905f7239644e2f20238d3a85fc3",  # liên hệ admin để lấy mã
    api_admin_version="api/v2.1",  # danh sách api có thể sử dụng ["v1.0", "api/v2.0", "api/v2.1"]
)