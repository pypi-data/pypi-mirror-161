def df_get_account_type_data():
    data = [
        {"id": -1, "name": "Khác"},
        {"id": 0, "name": "Nhập Thủ Công"},
        {"id": 1, "name": "Số Điện Thoại"},
        {"id": 2, "name": "Facebook"},
        {"id": 3, "name": "G+"},
        {"id": 4, "name": "Landing Page"},
        {"id": 5, "name": "Nhập Từ File"},
        {"id": 6, "name": "Zalo"},
        {"id": 7, "name": "Instagram"},
        {"id": 8, "name": "Mobile App"},
        {"id": 9, "name": "Youtube"},
        {"id": 10, "name": "Zalo"},
        {"id": 11, "name": "Smart Wifi"},
        {"id": 12, "name": "Call Center"},
        {"id": 13, "name": "Social"},
        {"id": 15, "name": "Phong Vũ Odoo"},
        {"id": 16, "name": "Phong Vũ Magento"},
        {"id": 17, "name": "Phong Vũ Inhouse"},
        {"id": 18, "name": "Phong Vũ Asia"},
        {"id": 19, "name": "Face ID"},
        {"id": 20, "name": "Line"},
        {"id": 21, "name": "Website"},
        {"id": 22, "name": "POS"},
        {"id": 23, "name": "Core"},
    ]
    return data


def get_account_type_by_id(account_type_id):
    data_account_type = df_get_account_type_data()
    obj_data = next((x for x in data_account_type if x.get("id") == account_type_id), None)
    return obj_data.get("name") if obj_data else None
