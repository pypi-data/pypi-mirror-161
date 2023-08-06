from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergePrimaryPhone(BaseMerge):
    def __check_suggest_phone__(
        self, phone, set_suggest_fields, set_unique_suggest_values
    ):
        suggest_phone_1 = False
        if (
            ProfileStructure.PHONE_NUMBER_1 not in set_suggest_fields
            and phone not in set_unique_suggest_values
        ):
            suggest_phone_1 = True
            set_suggest_fields.add(ProfileStructure.PHONE_NUMBER_1)
            set_unique_suggest_values.add(phone)
        return suggest_phone_1

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
        primary_phone = None
        phone_status = None
        suggest_phone_1 = False
        if profile_data:
            primary_phone = profile_data.get(ProfileStructure.PHONE_NUMBER)
            phone_status = profile_data.get("status")
            if primary_phone:
                suggest_phone_1 = self.__check_suggest_phone__(
                    phone=primary_phone,
                    set_suggest_fields=set_suggest_fields,
                    set_unique_suggest_values=set_unique_suggest_values,
                )
        field_value = self.__build_value__(
            value=primary_phone, suggest=suggest_phone_1, changealbe=False
        )
        field_value["status"] = phone_status
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
            tooltip_i18n="i18n_phone_merge_tooltip",
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        if profile_data:
            if type(profile_data) == str and CommonHelper().chuan_hoa_so_dien_thoai_v2(profile_data):
                suggest_filter_data.add(profile_data)
            elif type(profile_data) == dict and profile_data.get(
                ProfileStructure.PHONE_NUMBER
            ):
                suggest_filter_data.add(profile_data.get(ProfileStructure.PHONE_NUMBER))

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
        valid_phone = CommonHelper().chuan_hoa_so_dien_thoai_v2(origin_data)
        suggest_phone_1 = False
        if valid_phone:
            suggest_phone_1 = self.__check_suggest_phone__(
                phone=valid_phone,
                set_suggest_fields=set_suggest_fields,
                set_unique_suggest_values=set_unique_suggest_values,
            )
        field_value = self.__build_value__(
            value=valid_phone, suggest=suggest_phone_1, changealbe=False
        )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
            tooltip_i18n="i18n_phone_merge_tooltip",
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            suggest = source_data.get("field_value").get("suggest")
            phone = source_data.get("field_value").get("value")
            primary_phone = (
                target_data.get(ProfileStructure.PRIMARY_PHONE).get(
                    ProfileStructure.PHONE_NUMBER
                )
                if target_data.get(ProfileStructure.PRIMARY_PHONE)
                else None
            )

            set_phone = set(
                target_data.get(ProfileStructure.PHONE_NUMBER)
                if target_data.get(ProfileStructure.PHONE_NUMBER)
                else []
            )
            # Nếu primary_phone này ko được chọn, nó sẽ là secondary_phone
            if primary_phone:
                set_phone.add(primary_phone)
            valid_phone = CommonHelper().chuan_hoa_so_dien_thoai_v2(phone)
            if valid_phone:
                set_phone.add(valid_phone)
                if self.field_key == ProfileStructure.PRIMARY_PHONE and suggest:
                    primary_phone = valid_phone
            target_data[ProfileStructure.PHONE_NUMBER] = list(set_phone)
            CommonHelper.set_phone_profile(
                profile=target_data, primary_phone=primary_phone
            )

    def normalized_value(self, data):
        return data.get(self.field_key).get(ProfileStructure.PHONE_NUMBER) if data.get(self.field_key) else None
