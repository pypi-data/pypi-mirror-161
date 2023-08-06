def df_get_operation_data():
    lst = []
    operation_data = [
        {
            "id": 1,
            "name": "An ninh - Bảo vệ"
        },
        {
            "id": 2,
            "name": "Báo chí - Truyền hình"
        },
        {
            "id": 3,
            "name": "Bảo hiểm"
        },
        {
            "id": 4,
            "name": "Phiên dịch"
        },
        {
            "id": 5,
            "name": "Phim"
        },
        {
            "id": 6,
            "name": "Cơ khí chế tạo máy"
        },
        {
            "id": 7,
            "name": "Thế thao"
        },
        {
            "id": 8,
            "name": "Y tế"
        },
        {
            "id": 9,
            "name": "Giáo dục"
        },
        {
            "id": 10,
            "name": "Ẩm thực"
        },
        {
            "id": 11,
            "name": "Khoa học - Kỹ thuật"
        },
        {
            "id": 12,
            "name": "Địa chất"
        },
        {
            "id": 13,
            "name": "Môi trường"
        },
        {
            "id": 14,
            "name": "Nông nghiệp"
        }
    ]
    for operation in operation_data:
        operation["display_in_form"] = True
        lst.append(operation)
    return lst
