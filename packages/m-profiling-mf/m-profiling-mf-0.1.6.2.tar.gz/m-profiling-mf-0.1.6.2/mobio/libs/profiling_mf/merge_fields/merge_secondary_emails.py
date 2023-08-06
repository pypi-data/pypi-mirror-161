from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import ProfileHistoryChangeType


class MergeSecondaryEmails(BaseMerge):
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
        lst_email_2 = []
        if (
            type(profile_data) == dict
            and self.field_key == ProfileStructure.SECONDARY_EMAILS
        ):
            for email in profile_data.get("secondary"):
                # suggest = (
                #     True
                #     if email.get(ProfileStructure.EMAIL)
                #     not in set_unique_suggest_values
                #     else False
                # )
                status = email.get("status")
                value = email.get(ProfileStructure.EMAIL)
                field_value = self.__build_value__(
                    value=value, suggest=True, changealbe=False
                )
                field_value["status"] = status
                lst_email_2.append(field_value)
                # set_unique_suggest_values.add(email.get(ProfileStructure.EMAIL))
            suggest_data[self.field_key] = self.build_merge_data(
                translate_key=translate_key,
                field_property=field_property,
                display_type=display_type,
                displayable=True,
                editable=False,
                mergeable=True,
                order=1,
                group=MergeListGroup.INFORMATION,
                value=lst_email_2,
            )

    def set_filter_value(self, suggest_filter_data: set, profile_data):
        if type(profile_data) == dict:
            for email in profile_data.get("secondary"):
                suggest_filter_data.add(email.get(ProfileStructure.EMAIL))

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
        lst_email_2 = []
        if origin_data:
            if type(origin_data) == list:
                for email in origin_data:
                    if CommonHelper.validate_email(email):
                        # suggest = (
                        #     True if email not in set_unique_suggest_values else False
                        # )
                        field_value = self.__build_value__(
                            value=email, suggest=True, changealbe=False
                        )
                        lst_email_2.append(field_value)
                        # set_unique_suggest_values.add(email)
            elif type(origin_data) == str:
                if CommonHelper.validate_email(origin_data):
                    # suggest = (
                    #     True if origin_data not in set_unique_suggest_values else False
                    # )
                    field_value = self.__build_value__(
                        value=origin_data, suggest=True, changealbe=False
                    )
                    lst_email_2.append(field_value)
                    # set_unique_suggest_values.add(origin_data)
            else:
                print(
                    "key: {}, origin_data: {} is not valid".format(
                        self.field_key, origin_data
                    )
                )
        suggest_data[ProfileStructure.SECONDARY_EMAILS] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_email_2,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            primary_email = (
                target_data.get(ProfileStructure.PRIMARY_EMAIL).get(
                    ProfileStructure.EMAIL
                )
                if target_data.get(ProfileStructure.PRIMARY_EMAIL)
                else None
            )
            # normalize lại data
            target_data[ProfileStructure.EMAIL] = (
                target_data.get(ProfileStructure.EMAIL)
                if target_data.get(ProfileStructure.EMAIL)
                else []
            )
            # set_email = [] khi đây là master_data, nếu không thì set_data sẽ là tất cả email
            set_email = set(
                target_data.get(ProfileStructure.EMAIL) if not is_master_data else []
            )
            # add primary_email vào set_email để tránh bị mất primary_email
            if primary_email:
                set_email.add(primary_email)

            for source_email in source_data.get("field_value"):
                suggest = source_email.get("suggest")
                email = source_email.get("value")
                if email and CommonHelper.validate_email(email):
                    email = str(email).lower().strip()
                    if suggest:
                        set_email.add(email)

            target_data[ProfileStructure.EMAIL] = list(set_email)
            CommonHelper.set_validate_email(
                profile=target_data,
                primary_email=primary_email,
                check_valid_email=False,
            )

    def normalized_value(self, data):
        if self.field_key == ProfileStructure.SECONDARY_EMAILS:
            try:
                result = [x.get(ProfileStructure.EMAIL) for x in data.get(self.field_key).get("secondary")]
            except Exception as ex:
                print("{}:: {}".format(self.field_key, ex))
                result = []
        elif self.field_key in [ProfileStructure.EMAIL, ProfileStructure.EMAIL_2]:
            result = [x for x in data.get(ProfileStructure.EMAIL) or []]
        else:
            result = []
        return result

    def get_normalized_value(self, data):
        lst_value = []
        lst_key = [ProfileStructure.EMAIL_2, ProfileStructure.EMAIL, ProfileStructure.SECONDARY_EMAILS]
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
        return [
            x.get(ProfileStructure.EMAIL)
            for x in data.get(ProfileHistoryChangeType.ADD)
        ]

    def get_remove_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.REMOVE not in data:
            data[ProfileHistoryChangeType.REMOVE] = []
        return [
            x.get(ProfileStructure.EMAIL)
            for x in data.get(ProfileHistoryChangeType.REMOVE)
        ]
