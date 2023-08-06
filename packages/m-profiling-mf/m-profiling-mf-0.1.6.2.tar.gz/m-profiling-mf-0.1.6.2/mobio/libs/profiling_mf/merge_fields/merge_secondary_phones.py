from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import ProfileHistoryChangeType


class MergeSecondaryPhones(BaseMerge):
    def serialize_data(
        self,
        suggest_data,
        profile_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_property,
        display_type,
        translate_key,
        predict=None
    ):
        lst_phone_2 = []
        if (
            type(profile_data) == dict
            and self.field_key == ProfileStructure.SECONDARY_PHONES
        ):
            for phone in profile_data.get("secondary"):
                # suggest = (
                #     True
                #     if phone.get(ProfileStructure.PHONE_NUMBER)
                #     not in set_unique_suggest_values
                #     else False
                # )
                status = phone.get("status")
                value = phone.get(ProfileStructure.PHONE_NUMBER)
                field_value = self.__build_value__(
                    value=value, suggest=True, changealbe=False
                )
                field_value["status"] = status
                lst_phone_2.append(field_value)
                # set_unique_suggest_values.add(phone.get(ProfileStructure.PHONE_NUMBER))

            suggest_data[self.field_key] = self.build_merge_data(
                translate_key=translate_key,
                field_property=field_property,
                display_type=display_type,
                displayable=True,
                editable=False,
                mergeable=True,
                order=1,
                group=MergeListGroup.INFORMATION,
                value=lst_phone_2,
            )

    def set_filter_value(self, suggest_filter_data: set, profile_data):
        if type(profile_data) == dict:
            for phone in profile_data.get("secondary"):
                suggest_filter_data.add(phone.get(ProfileStructure.PHONE_NUMBER))

    def serialize_origin_data(
        self,
        suggest_data,
        origin_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_property,
        display_type,
        translate_key,
    ):
        if origin_data:
            lst_phone_2 = []
            if type(origin_data) == list:
                for phone in origin_data:
                    phone_valid = CommonHelper().chuan_hoa_so_dien_thoai_v2(phone)
                    if phone_valid:
                        field_value = self.__build_value__(
                            value=phone_valid, suggest=True, changealbe=False
                        )
                        lst_phone_2.append(field_value)
                        # set_unique_suggest_values.add(phone_valid)
            elif type(origin_data) == str:
                phone_valid = CommonHelper().chuan_hoa_so_dien_thoai_v2(origin_data)
                if phone_valid:
                    field_value = self.__build_value__(
                        value=phone_valid, suggest=True, changealbe=False
                    )
                    lst_phone_2.append(field_value)
                    # set_unique_suggest_values.add(phone_valid)
            else:
                print('key: {}, origin_data: {} is not valid'.format(self.field_key, origin_data))
            suggest_data[ProfileStructure.SECONDARY_PHONES] = self.build_merge_data(
                translate_key=translate_key,
                field_property=field_property,
                display_type=display_type,
                displayable=True,
                editable=False,
                mergeable=True,
                order=1,
                group=MergeListGroup.INFORMATION,
                value=lst_phone_2,
            )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            primary_phone = (
                target_data.get(ProfileStructure.PRIMARY_PHONE).get(
                    ProfileStructure.PHONE_NUMBER
                )
                if target_data.get(ProfileStructure.PRIMARY_PHONE)
                else None
            )
            # normalize lại data
            target_data[ProfileStructure.PHONE_NUMBER] = (
                target_data.get(ProfileStructure.PHONE_NUMBER)
                if target_data.get(ProfileStructure.PHONE_NUMBER)
                else []
            )
            # set_phone = [] khi đây là master_data, nếu không thì set_data sẽ là tất cả phone
            set_phone = set(
                target_data.get(ProfileStructure.PHONE_NUMBER) if not is_master_data else []
            )
            # add primary_phone vào set_phone để tránh bị mất primary_phone
            if primary_phone:
                set_phone.add(primary_phone)
            for source_phone in source_data.get("field_value"):
                phone = source_phone.get("value")
                suggest = source_phone.get("suggest")
                phone_valid = CommonHelper().chuan_hoa_so_dien_thoai_v2(phone)
                if phone_valid and suggest:
                    set_phone.add(phone_valid)
            target_data[ProfileStructure.PHONE_NUMBER] = list(set_phone)
            CommonHelper().set_phone_profile(profile=target_data, primary_phone=primary_phone)

    def normalized_value(self, data):
        if self.field_key == ProfileStructure.SECONDARY_PHONES:
            try:
                result = [x.get(ProfileStructure.PHONE_NUMBER) for x in data.get(self.field_key).get("secondary")]
            except Exception as ex:
                print("{}:: {}".format(self.field_key, ex))
                result = []
        elif self.field_key in [ProfileStructure.PHONE_NUMBER_2, ProfileStructure.PHONE_NUMBER]:
            result = [x for x in data.get(ProfileStructure.PHONE_NUMBER) or []]
        else:
            result = []
        return result

    def get_normalized_value(self, data):
        lst_value = []
        lst_key = [ProfileStructure.PHONE_NUMBER_2, ProfileStructure.PHONE_NUMBER, ProfileStructure.SECONDARY_PHONES]
        for key in lst_key:
            if data.get(key):
                value = data.get(key)
                if type(value) == list:
                    lst_value.extend(value)
                else:
                    lst_value.append(value)
        return lst_value

    def get_add_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.ADD not in data:
            data[ProfileHistoryChangeType.ADD] = []
        return [x.get(ProfileStructure.PHONE_NUMBER) for x in data.get(ProfileHistoryChangeType.ADD)]

    def get_remove_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.REMOVE not in data:
            data[ProfileHistoryChangeType.REMOVE] = []
        return [x.get(ProfileStructure.PHONE_NUMBER) for x in data.get(ProfileHistoryChangeType.REMOVE)]