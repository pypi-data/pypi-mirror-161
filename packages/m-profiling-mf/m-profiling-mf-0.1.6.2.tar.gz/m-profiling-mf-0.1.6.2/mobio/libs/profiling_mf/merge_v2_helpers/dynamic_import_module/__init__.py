from importlib import import_module
from mobio.libs.profiling_mf import ProfileStructure, CommonMerchant, Device
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge


def dynamic_import_merge_v2(field_name: str):
    field_import = str(field_name)
    if field_import in [
        ProfileStructure.PHONE_NUMBER_1,
        ProfileStructure.PRIMARY_PHONE,
    ]:
        field_import = ProfileStructure.PRIMARY_PHONE
    elif field_import in [
        ProfileStructure.SECONDARY_PHONES,
        ProfileStructure.PHONE_NUMBER,
        ProfileStructure.PHONE_NUMBER_2,
    ]:
        field_import = ProfileStructure.SECONDARY_PHONES
    elif field_import in [ProfileStructure.EMAIL_1, ProfileStructure.PRIMARY_EMAIL]:
        field_import = ProfileStructure.PRIMARY_EMAIL
    elif field_import in [
        ProfileStructure.SECONDARY_EMAILS,
        ProfileStructure.EMAIL,
        ProfileStructure.EMAIL_2,
    ]:
        field_import = ProfileStructure.SECONDARY_EMAILS
    elif field_import in [
        "device",
        ProfileStructure.DEVICES,
        Device.DEVICE_ID
    ]:
        field_import = ProfileStructure.DEVICES
    elif field_import.startswith(CommonMerchant.PREFIX_DYNAMIC_FIELD):
        field_import = "dynamic"
    elif field_import in [ProfileStructure.ADDRESS, ProfileStructure.PROFILE_ADDRESS]:
        field_import = ProfileStructure.ADDRESS
    elif field_import == "_id":
        field_import = "id"
    elif field_import in [ProfileStructure.TAGS, ProfileStructure.PROFILE_TAGS, ProfileStructure.TAGS_SEARCH]:
        field_import = "profile_tags"
    try:
        class_name = "Merge" + field_import.title().replace("_", "")
        if not field_import.startswith("."):
            field_import = ".merge_{}".format(field_import)
        merge_module = import_module(field_import, package="mobio.libs.profiling_mf.merge_fields")

        merge_class = getattr(merge_module, class_name)
        instance = merge_class(field_name)
    except (AttributeError, AssertionError, ModuleNotFoundError):
        raise ImportError(
            "{} is not part of our export collection!".format(field_import)
        )
    else:
        if not issubclass(merge_class, BaseMerge):
            raise ImportError(
                "We currently don't have {}, but you are welcome to send in the request for it!".format(
                    merge_class
                )
            )
    return instance
