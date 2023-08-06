from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergePrimaryEmail(BaseMerge):
    def __check_suggest_email__(
        self, email, set_suggest_fields, set_unique_suggest_values
    ):
        suggest_email_1 = False
        if (
            ProfileStructure.EMAIL_1 not in set_suggest_fields
            and email not in set_unique_suggest_values
        ):
            suggest_email_1 = True
            set_suggest_fields.add(ProfileStructure.EMAIL_1)
            set_unique_suggest_values.add(email)
        return suggest_email_1

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
        primary_email = None
        email_status = None
        suggest_email_1 = False
        if profile_data:
            primary_email = profile_data.get(ProfileStructure.EMAIL)
            email_status = profile_data.get("status")
            if primary_email:
                suggest_email_1 = self.__check_suggest_email__(
                    email=primary_email,
                    set_suggest_fields=set_suggest_fields,
                    set_unique_suggest_values=set_unique_suggest_values,
                )
        field_value = self.__build_value__(
            value=primary_email, suggest=suggest_email_1, changealbe=False
        )
        field_value["status"] = email_status
        suggest_data[ProfileStructure.PRIMARY_EMAIL] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
            tooltip_i18n="i18n_email_merge_tooltip",
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        if profile_data:
            if type(profile_data) == dict:
                suggest_filter_data.add(profile_data.get(ProfileStructure.EMAIL))
            elif type(profile_data) == str and CommonHelper.validate_email(profile_data):
                suggest_filter_data.add(profile_data)

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
        suggest_email_1 = False
        email_valid = None
        if CommonHelper.validate_email(origin_data):
            email_valid = origin_data.lower().strip()
            suggest_email_1 = self.__check_suggest_email__(
                email=email_valid,
                set_suggest_fields=set_suggest_fields,
                set_unique_suggest_values=set_unique_suggest_values,
            )
        field_value = self.__build_value__(
            value=email_valid, suggest=suggest_email_1, changealbe=False
        )
        suggest_data[ProfileStructure.PRIMARY_EMAIL] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
            tooltip_i18n="i18n_email_merge_tooltip",
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            suggest = source_data.get("field_value").get("suggest")
            email = source_data.get("field_value").get("value")
            primary_email = (
                target_data.get(ProfileStructure.PRIMARY_EMAIL).get(
                    ProfileStructure.EMAIL
                )
                if target_data.get(ProfileStructure.PRIMARY_EMAIL)
                else None
            )

            set_email = set(
                target_data.get(ProfileStructure.EMAIL)
                if target_data.get(ProfileStructure.EMAIL)
                else []
            )
            # Nếu primary_email này ko được chọn, nó sẽ là secondary_email
            if primary_email:
                set_email.add(primary_email)

            if email and CommonHelper.validate_email(email):
                email = str(email).lower().strip()
                set_email.add(email)
                if self.field_key == ProfileStructure.PRIMARY_EMAIL and suggest:
                    primary_email = email
            target_data[ProfileStructure.EMAIL] = list(set_email)
            CommonHelper.set_validate_email(
                profile=target_data,
                primary_email=primary_email,
                check_valid_email=False,
            )

    def normalized_value(self, data):
        return data.get(self.field_key).get(ProfileStructure.EMAIL) if data.get(self.field_key) else None
