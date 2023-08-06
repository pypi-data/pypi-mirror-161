import uuid
import re
from dateutil.parser import parse
import pytz
from datetime import datetime
import phonenumbers
from mobio.libs.profiling_mf import TagInteractiveStructure
from mobio.libs.profiling_mf.profiling_common import PhoneVerifyStatus, EmailValidateStatus


class CommonHelper:
    @staticmethod
    def normalize_uuid(some_uuid):
        if isinstance(some_uuid, str):
            return uuid.UUID(some_uuid)
        return some_uuid

    @staticmethod
    def create_tag_interactive():
        tag_interactive = dict(
            {
                TagInteractiveStructure.TAG_ID: None,
                TagInteractiveStructure.INTERACTIVE_TOTAL: 0,
                TagInteractiveStructure.INTERACTIVE_3_DAYS: 0,
                TagInteractiveStructure.INTERACTIVE_7_DAYS: 0,
                TagInteractiveStructure.INTERACTIVE_30_DAYS: 0,
                TagInteractiveStructure.LAST_ACTION_TIME: None,
            }
        )
        return tag_interactive

    @staticmethod
    def create_simple_data_type(_id=None, _name=None):
        return {"id": _id, "name": _name}

    @staticmethod
    def parse_time(dt):
        tz_str = """-12 Y
            -11 X NUT SST
            -10 W CKT HAST HST TAHT TKT
            -9 V AKST GAMT GIT HADT HNY
            -8 U AKDT CIST HAY HNP PST PT
            -7 T HAP HNR MST PDT
            -6 S CST EAST GALT HAR HNC MDT
            -5 R CDT COT EASST ECT EST ET HAC HNE PET
            -4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
            -3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
            -2 O BRST FNT PMDT UYST WGST
            -1 N AZOT CVT EGT
            0 Z EGST GMT UTC WET WT
            1 A CET DFT WAT WEDT WEST
            2 B CAT CEDT CEST EET SAST WAST
            3 C EAT EEDT EEST IDT MSK
            4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
            5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
            6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
            7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
            8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
            9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
            10 K AEST ChST PGT VLAT YAKST YAPT
            11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
            12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
            13 FJST NZDT
            11.5 NFT
            10.5 ACDT LHST
            9.5 ACST
            6.5 CCT MMT
            5.75 NPT
            5.5 SLT
            4.5 AFT IRDT
            3.5 IRST
            -2.5 HAT NDT
            -3.5 HNT NST NT
            -4.5 HLV VET
            -9.5 MART MIT"""
        tzd = {}
        for tz_descr in map(str.split, tz_str.split("\n")):
            tz_offset = int(float(tz_descr[0]) * 3600)
            for tz_code in tz_descr[1:]:
                tzd[tz_code] = tz_offset
        try:
            if isinstance(dt, datetime):
                result = dt
            else:
                result = parse(dt, tzinfos=tzd)
            return (
                result.astimezone(pytz.utc).replace(tzinfo=None)
                if result.tzinfo
                else result
            )
        except Exception as ex:
            print("UserHelper:: parse_time error: {}".format(ex))
            return None

    @staticmethod
    def validate_email(email):
        if not email:
            return False
        try:
            valid = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
        except Exception as ex:
            print('validate_email:ERROR: %s' % ex)
            valid = None
        return True if valid is not None else False

    def chuan_hoa_so_dien_thoai_theo_dau_so_moi(self, so_dien_thoai):
        so_dien_thoai = re.sub(r'^(0|\+84|84)12([068])', r'\g<1>7\g<2>', so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)121", "\g<1>79", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)122", "\g<1>77", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)12([345])", "\g<1>8\g<2>", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)127", "\g<1>81", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)129", "\g<1>82", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)16([2-9])", "\g<1>3\g<2>", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)18([68])", "\g<1>5\g<2>", so_dien_thoai)
        so_dien_thoai = re.sub("^(0|\+84|84)199", "\g<1>59", so_dien_thoai)

        return so_dien_thoai

    def validate_phone(self, phone_number):
        try:
            pattern_phone_number = "^(\+?84|0)?(1(2([0-9])|6([2-9])|88|86|99)|9([0-9]{1})|8([0-9]{1})|7[0|6-9]|3[2-9]|5[2|5|6|8|9])+([0-9]{7})$"
            valid = re.match(pattern_phone_number, phone_number)
        except Exception as ex:
            print('validate_phone:ERROR: %s' % ex)
            valid = None
        return True if valid is not None else False

    def chuan_hoa_so_dien_thoai_v2(self, so_dien_thoai):
        if not so_dien_thoai:
            return None
        so_dien_thoai = self.chuan_hoa_so_dien_thoai_theo_dau_so_moi(so_dien_thoai)
        try:
            parse_phone = phonenumbers.parse(so_dien_thoai, 'VN')
            if so_dien_thoai.startswith('+84') or so_dien_thoai.startswith('84'):
                is_valid = self.validate_phone(so_dien_thoai)
            else:
                is_valid = phonenumbers.is_valid_number(parse_phone)
            result = phonenumbers.format_number(parse_phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            print("chuan_hoa_so_dien_thoai_v2:: Exception: {},{} ".format(so_dien_thoai, str(e)))
            is_valid = False
            result = None
        if is_valid:
            return result
        else:
            return None

    @staticmethod
    def set_primary_email_from_secondary(profile):
        if len(profile.get('secondary_emails').get('secondary')) > 0:
            lst_secondary = list(profile.get('secondary_emails').get('secondary'))
            profile['primary_email'] = lst_secondary.pop(0)
            profile['secondary_emails']['secondary_size'] = len(lst_secondary)
            profile['secondary_emails']['secondary'] = lst_secondary
        return profile

    @staticmethod
    def set_primary_phone_from_secondary(profile):
        if len(profile['secondary_phones']['secondary']) > 0:
            lst_secondary = list(profile['secondary_phones']['secondary'])
            profile['primary_phone'] = lst_secondary.pop(0)
            profile['secondary_phones']['secondary_size'] = len(lst_secondary)
            profile['secondary_phones']['secondary'] = lst_secondary
        return profile

    @staticmethod
    def set_validate_email(profile, primary_email=None, check_valid_email=True):
        lst_udt_email = list()
        udt_primary_email = None
        lst_email = []
        for e in profile.get("email"):
            valid_email = dict()
            valid_email["email"] = e
            valid_email["status"] = EmailValidateStatus.Uncheck
            if (
                    profile.get("primary_email")
                    and profile.get("primary_email").get("email") == e
            ):
                valid_email["status"] = profile.get("primary_email").get("status")
                if valid_email.get("status") != EmailValidateStatus.Uncheck:
                    valid_email["last_check"] = (
                        profile.get("primary_email").get("last_check")
                        if profile.get("primary_email").get("last_check")
                        else datetime.utcnow()
                    )
                else:
                    lst_email.append(e)
            else:
                if (
                        profile.get("secondary_emails")
                        and len(profile.get("secondary_emails")) > 0
                ):
                    se = next(
                        (
                            x
                            for x in profile.get("secondary_emails").get("secondary")
                            if x.get("email") == e
                        ),
                        None,
                    )
                    if se:
                        valid_email["status"] = se.get("status")
                        if valid_email.get("status") != EmailValidateStatus.Uncheck:
                            valid_email["last_check"] = (
                                se.get("last_check")
                                if se.get("last_check")
                                else datetime.utcnow()
                            )
                        else:
                            lst_email.append(e)
            if primary_email and primary_email == e:
                udt_primary_email = valid_email
                continue
            lst_udt_email.append(valid_email)
        secondary_emails = dict()
        secondary_emails["secondary_size"] = len(lst_udt_email)
        secondary_emails["secondary"] = lst_udt_email
        profile["secondary_emails"] = secondary_emails
        profile["primary_email"] = None
        if udt_primary_email is None:
            profile = CommonHelper.set_primary_email_from_secondary(profile)
        else:
            profile["primary_email"] = udt_primary_email
        return profile

    @staticmethod
    def set_phone_profile(profile, primary_phone=None):
        lst_udt_phone = list()
        udt_primary_phone = None
        for p in profile.get("phone_number"):
            phone_profile = dict()
            phone_profile["phone_number"] = p
            phone_profile["status"] = PhoneVerifyStatus.UnVerify
            phone_profile["last_verify"] = datetime.utcnow()

            # primary_phone = profile.get('primary_phone')
            if (
                    profile.get("primary_phone")
                    and profile.get("primary_phone").get("phone_number") == p
            ):
                phone_profile["status"] = profile.get("primary_phone").get("status")
                if phone_profile.get("status") != PhoneVerifyStatus.UnVerify:
                    phone_profile["last_verify"] = (
                        profile.get("primary_phone").get("last_verify")
                        if profile.get("primary_phone").get("last_verify")
                        else datetime.utcnow()
                    )
            if profile.get("secondary_phones"):
                for se in profile.get("secondary_phones").get("secondary"):
                    if se.get("phone_number") == p:
                        phone_profile["status"] = se.get("status")
                        if phone_profile.get("status") != PhoneVerifyStatus.UnVerify:
                            phone_profile["last_verify"] = (
                                se.get("last_verify")
                                if se.get("last_verify")
                                else datetime.utcnow()
                            )
                        break
            if primary_phone and primary_phone == p:
                udt_primary_phone = phone_profile
                continue
            lst_udt_phone.append(phone_profile)
        secondary_phones = dict()
        secondary_phones["secondary_size"] = len(lst_udt_phone)
        secondary_phones["secondary"] = lst_udt_phone
        profile["secondary_phones"] = secondary_phones
        profile["primary_phone"] = None
        if udt_primary_phone is None:
            profile = CommonHelper.set_primary_phone_from_secondary(profile)
        else:
            profile["primary_phone"] = udt_primary_phone
        return profile

    def generate_social_unique_key(self, social_id, social_type):
        return "{}:{}".format(social_id, social_type)
