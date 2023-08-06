def df_get_religiousness_data():
    lst = []
    religiousness_data = [
        {
            "id": 1,
            "name": "Lương giáo",
            'display_in_form': True
        },
        {
            "id": 2,
            "name": "Phật giáo",
            'display_in_form': True
        },
        {
            "id": 3,
            "name": "Công giáo",
            'display_in_form': True
        },
        {
            "id": 4,
            "name": "Cao Đài",
            'display_in_form': True
        },
        {
            "id": 5,
            "name": "Hòa Hảo",
            'display_in_form': True
        },
        {
            "id": 6,
            "name": "Tin Lành",
            'display_in_form': True
        },
        {
            "id": 7,
            "name": "Hồi Giáo",
            'display_in_form': True
        },
        {
            "id": 8,
            "name": "Bà La Môn",
            'display_in_form': True
        },
        {
            "id": 9,
            "name": "Đạo Tứ ấn hiếu nghĩa",
            'display_in_form': True
        },
        {
            "id": 10,
            "name": "Tịnh độ cư sĩ Phật hội Việt Nam",
            'display_in_form': True
        },
        {
            "id": 11,
            "name": "Bửu sơn Kỳ hương",
            'display_in_form': True
        },
        {
            "id": 12,
            "name": "Minh Sư Đạo",
            'display_in_form': True
        },
        {
            "id": 13,
            "name": "Bahá'í",
            'display_in_form': True
        },
        {
            "id": 14,
            "name": "Minh Lý Đạo",
            'display_in_form': True
        }
    ]
    for religiousness in religiousness_data:
        religiousness['display_in_form'] = True
        lst.append(religiousness)
    return lst
