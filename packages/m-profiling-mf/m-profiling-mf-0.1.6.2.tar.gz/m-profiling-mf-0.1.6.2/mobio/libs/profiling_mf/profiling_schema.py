from marshmallow import Schema, fields, validate

from mobio.libs.profiling_mf.profiling_common import SocialType, SocialIdType


class SocialUserSchema(Schema):
    social_id = fields.Str(required=True)
    social_type = fields.Int(
        required=True,
        validate=validate.OneOf(
            [
                SocialType.FACEBOOK,
                SocialType.ZALO,
                SocialType.INSTAGRAM,
                SocialType.YOUTUBE,
                SocialType.APP,
                SocialType.LINE,
                SocialType.MOBIO_CHAT_TOOL,
            ]
        ),
    )
    access_token = fields.Str(allow_none=True, default=None)
    social_id_type = fields.Int(
        allow_none=True, default=SocialIdType.PAGE, missing=SocialIdType.PAGE
    )
    social_name = fields.Str(allow_none=True, default=None)
    page_id = fields.Str(allow_none=True, default=None, missing=None)
    app_id = fields.Str(allow_none=True, default=None, missing=None)


class VibCardSchema(Schema):
    account_serno = fields.Str(required=True)
    annual_fees_next_action_date = fields.DateTime(allow_none=True, missing=None)
    card_id = fields.Str(required=True)
    card_limit = fields.Float(required=True)
    card_name = fields.Str(required=True)
    card_no = fields.Str(required=True)
    card_open_date = fields.DateTime(required=True)
    card_type = fields.Str(required=True)
    card_type_id = fields.Str(required=True)
    is_primary_card = fields.Boolean(required=True)
    status = fields.Str(required=True)


class UdtSchema(Schema):
    id = fields.Int(required=True, allow_none=False)
    value = fields.Str(required=True)


class HobbySchema(Schema):
    id = fields.Int(required=True, allow_none=False)
    name = fields.Str(required=True)


class PushIdSchema(Schema):
    push_id = fields.Str(required=True)
    os_type = fields.Int(required=True)
    app_id = fields.Str(required=True)
    lang = fields.Str(required=False, allow_none=True, missing="vi", default="vi")
    is_logged = fields.Boolean(required=False, allow_none=True, missing=False, default=False)
    last_access = fields.DateTime(required=False, allow_none=True, missing=None, default=None)
    count_fail = fields.Int(required=False, allow_none=True, missing=0, default=0)
    device_id = fields.Str(required=False, allow_none=True, missing=None, default=None)
    accept_push = fields.Boolean(required=False, allow_none=True, missing=True, default=True)


class CardSchema(Schema):
    id = fields.Str(required=True, allow_none=False)
    card_id = fields.Str(required=True, allow_none=False)
    card_name = fields.Str(required=True, allow_none=False)
    card_code = fields.Str(required=True, allow_none=False)
    is_primary = fields.Boolean(required=False, default=False, missing=False, allow_none=True)
    card_status = fields.Int(required=True, allow_none=False)
    expiry_time = fields.DateTime(required=False, allow_none=True)


class ProfileTagSchema(Schema):
    id = fields.UUID(required=True)
    merchant_id = fields.UUID(required=True)
    tag = fields.Str(required=True)
    tag_type = fields.Int(required=True)


class DeviceTypeSchema(Schema):
    device_type = fields.Str(required=True, allow_none=False)
    device_name = fields.Str(required=True, allow_none=False)


class DeviceSchema(Schema):
    device_id = fields.Str(required=True, validate=validate.Length(min=3))
    device_name = fields.Str(allow_none=True)
    source = fields.Str(required=True, validate=validate.Length(min=3))


class ProfileByIdentifySchema(Schema):
    merchant_id = fields.List(fields.UUID, allow_none=True)
    profile_id = fields.UUID(allow_none=True)
    identify_value = fields.Str(required=True, validate=validate.Length(min=3))
    identify_type = fields.Str(required=True, validate=validate.Length(min=3))
    is_verify = fields.Boolean(allow_none=True, missing=False)
    date_verify = fields.DateTime(allow_none=True, missing=None)
    verify_by = fields.Str(allow_none=True, missing=None)
