import uuid
import requests
from mobio.libs.profiling_mf import CommonMerchant, lru_cache, MobioModuleHost, p_mf_admin_sdk
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_v2_helpers.dynamic_import_module import (
    dynamic_import_merge_v2,
)
from mobio.libs.profiling_mf.profiling_common import (
    UnificationStructure,
    UnificationMatchRule,
    UnificationMatchType,
    UnificationNormalizedType,
)


class ProfilingHelper:
    @lru_cache.add_for_class()
    def __get_unification_rules__(self, merchant_id):
        # profiling_host = p_mf_admin_sdk
        profiling_host = p_mf_admin_sdk.request_get_merchant_config_host(merchant_id=str(merchant_id), key=MobioModuleHost.PROFILING_APP_API_SERVICE_HOST)
        headers = {
            "Authorization": CommonMerchant.MOBIO_TOKEN,
            "X-Merchant-ID": merchant_id,
        }
        response = requests.get(
            profiling_host + "/profiling/v3.0/unification/list", headers=headers
        )
        response.raise_for_status()
        unification_rules = response.json().get("unification_rules") or []
        return unification_rules

    def check_data_source_valid(self, merchant_id, data):
        all_rules = self.__get_unification_rules__(merchant_id=merchant_id)
        source = data.get("source")
        if not source:
            fields = ["source"]
            return (
                False,
                fields,
                {
                    "fields": fields,
                    "detail": "missing: " + ", ".join(fields),
                    "code": "01",
                },
            )
        or_operator = []
        rule = next(
            (
                x
                for x in all_rules
                if x.get(UnificationStructure.SOURCE).lower() == str(source).lower()
            ),
            None,
        )
        if not rule:
            rule = next(
                (x for x in all_rules if x.get(UnificationStructure.IS_DEFAULT)), None,
            )
        if not rule:
            fields = ["source"]
            return (
                False,
                fields,
                {"fields": fields, "detail": "missing rule", "code": "02"},
            )

        lst_field_required = []
        for rule_operator in rule.get(UnificationStructure.OPERATORS):
            match_all_rule = []
            fields = []
            for k, v in rule_operator.get(UnificationStructure.FIELDS).items():
                fields.append(k)
                instance = dynamic_import_merge_v2(k)
                if not instance:
                    print(
                        "KEY: {} is not has rule in dynamic_import_merge_v2".format(k)
                    )
                    match_all_rule.append(False)
                    continue
                instance_value = instance.get_normalized_value(data=data)

                if instance_value:
                    # match_all_rule.append(True)
                    matched_rule = False
                    normalized_type = v.get(UnificationMatchRule.NORMALIZED_TYPE)
                    match_type = v.get(UnificationMatchRule.MATCH_TYPE)
                    if match_type in [
                        UnificationMatchType.EXACT_NORMALIZED,
                        UnificationMatchType.EXACT,
                    ]:
                        if normalized_type == UnificationNormalizedType.PHONE_NUMBER:
                            if type(instance_value) == list:
                                for phone in instance_value:
                                    valid_phone = CommonHelper().chuan_hoa_so_dien_thoai_v2(
                                        phone
                                    )
                                    if valid_phone:
                                        matched_rule = True
                            else:
                                valid_phone = CommonHelper().chuan_hoa_so_dien_thoai_v2(
                                    instance_value
                                )
                                if valid_phone:
                                    matched_rule = True

                        elif normalized_type == UnificationNormalizedType.EMAIL:
                            if type(instance_value) == list:
                                for email in instance_value:
                                    email = str(email).lower().strip()
                                    if CommonHelper().validate_email(email):
                                        matched_rule = True
                            else:
                                email = str(instance_value).lower().strip()
                                if CommonHelper().validate_email(email):
                                    matched_rule = True
                        elif normalized_type in [
                            UnificationNormalizedType.UUID,
                            UnificationNormalizedType.INT,
                            UnificationNormalizedType.FLOAT,
                            UnificationNormalizedType.STRING,
                        ]:

                            if type(instance_value) == list:
                                for single_instance_value in instance_value:
                                    try:
                                        single_instance_value = (
                                            uuid.UUID(single_instance_value)
                                            if normalized_type
                                            == UnificationNormalizedType.UUID
                                            else int(single_instance_value)
                                            if normalized_type
                                            == UnificationNormalizedType.INT
                                            else float(single_instance_value)
                                            if normalized_type
                                            == UnificationNormalizedType.FLOAT
                                            else str(single_instance_value)
                                        )
                                        if single_instance_value is not None:
                                            matched_rule = True
                                    except:
                                        matched_rule = False
                            else:
                                try:
                                    value = (
                                        uuid.UUID(instance_value)
                                        if normalized_type
                                        == UnificationNormalizedType.UUID
                                        else int(instance_value)
                                        if normalized_type
                                        == UnificationNormalizedType.INT
                                        else float(instance_value)
                                        if normalized_type
                                        == UnificationNormalizedType.FLOAT
                                        else str(instance_value)
                                    )
                                    if value is not None:
                                        matched_rule = True
                                except:
                                    matched_rule = False

                    elif match_type in [UnificationMatchType.FUZZY]:
                        matched_rule = True
                    match_all_rule.append(matched_rule)
                else:
                    match_all_rule.append(False)
                    # break
            lst_field_required.append(fields)
            if all(match_all_rule):
                return True, [], {}
        if lst_field_required:
            fields = [[str(y) for y in x] for x in lst_field_required]
            return (
                False,
                fields[0],
                {
                    "fields": fields,
                    "detail": "missing: "
                    + ", ".join(
                        ["[" + ",".join([str(y) for y in x]) + "]" for x in fields]
                    ),
                    "code": "01",
                },
            )


if __name__ == "__main__":
    r = ProfilingHelper().check_data_source_valid(
        merchant_id="0ff54084-a607-46f7-aeb4-8854ab8e6292",
        data={"source": "test", "primary_phone": "0832201234", "name": "n1"},
    )
    print(r)
