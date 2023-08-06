def df_get_hobby_data():
    lst = []
    hobby_data = [
        {
            "id": 1,
            "name": "Công nghệ",
            "e_id": 101
        },
        {
            "id": 2,
            "name": "Điện thoại và máy tính bảng",
            "e_id": 102
        },
        {
            "id": 3,
            "name": "Máy tính và laptop",
            "e_id": 103
        },
        {
            "id": 4,
            "name": "Máy quay phim",
            "e_id": 104
        },
        {
            "id": 5,
            "name": "Thiết bị số. tivi & dàn âm thanh",
            "e_id": 105
        },
        {
            "id": 6,
            "name": "Thiết bị văn phòng",
            "e_id": 106
        },
        {
            "id": 7,
            "name": "Phần mềm",
            "e_id": 107
        },
        {
            "id": 8,
            "name": "Phụ kiện điện thoại",
            "e_id": 108
        },
        {
            "id": 9,
            "name": "Đồ gia dụng",
            "e_id": 201
        },
        {
            "id": 10,
            "name": "Khoa học",
            "e_id": 301
        },
        {
            "id": 11,
            "name": "Khoa học tự nhiên",
            "e_id": 302
        },
        {
            "id": 12,
            "name": "Khoa học xã hội",
            "e_id": 303
        },
        {
            "id": 13,
            "name": "Khoa học thường thức",
            "e_id": 304
        },
        {
            "id": 14,
            "name": "Thể thao",
            "e_id": 401
        },
        {
            "id": 15,
            "name": "Bóng đá",
            "e_id": 402
        },
        {
            "id": 16,
            "name": "Quần vợt",
            "e_id": 403
        },
        {
            "id": 17,
            "name": "Cầu lông",
            "e_id": 404
        },
        {
            "id": 18,
            "name": "Bóng bàn",
            "e_id": 405
        },
        {
            "id": 19,
            "name": "Bóng chuyền",
            "e_id": 406
        },
        {
            "id": 20,
            "name": "Bóng rổ",
            "e_id": 407
        },
        {
            "id": 21,
            "name": "Bơi",
            "e_id": 409
        },
        {
            "id": 22,
            "name": "Điền kinh",
            "e_id": 410
        },
        {
            "id": 23,
            "name": "Chạy",
            "e_id": 411
        },
        {
            "id": 24,
            "name": "Đi bộ",
            "e_id": 412
        },
        {
            "id": 25,
            "name": "Thể dục & sức khỏe",
            "e_id": 413
        },
        {
            "id": 26,
            "name": "Khiêu vũ, nhảy",
            "e_id": 415
        },
        {
            "id": 27,
            "name": "Yoga",
            "e_id": 416
        },
        {
            "id": 28,
            "name": "Wusu",
            "e_id": 417
        },
        {
            "id": 29,
            "name": "Taekwondo",
            "e_id": 418
        },
        {
            "id": 30,
            "name": "Karatedo",
            "e_id": 419
        },
        {
            "id": 31,
            "name": "Võ cổ truyền",
            "e_id": 420
        },
        {
            "id": 32,
            "name": "Boxing",
            "e_id": 421
        },
        {
            "id": 33,
            "name": "Du lịch",
            "e_id": 501
        },
        {
            "id": 34,
            "name": "Du lịch việt nam",
            "e_id": 502
        },
        {
            "id": 35,
            "name": "Du lịch nước ngoài",
            "e_id": 503
        },
        {
            "id": 36,
            "name": "Giải trí",
            "e_id": 601
        },
        {
            "id": 37,
            "name": "Showbiz",
            "e_id": 602
        },
        {
            "id": 38,
            "name": "Phim",
            "e_id": 603
        },
        {
            "id": 39,
            "name": "Phim hài",
            "e_id": 604
        },
        {
            "id": 40,
            "name": "Phim hàn",
            "e_id": 605
        },
        {
            "id": 41,
            "name": "Phim Trung quốc",
            "e_id": 606
        },
        {
            "id": 42,
            "name": "Phim hành động",
            "e_id": 607
        },
        {
            "id": 43,
            "name": "Phim khoa học viễn tưởng",
            "e_id": 608
        },
        {
            "id": 44,
            "name": "Phim hoạt hình",
            "e_id": 609
        },
        {
            "id": 45,
            "name": "Âm nhạc",
            "e_id": 610
        },
        {
            "id": 46,
            "name": "Nhạc cụ",
            "e_id": 611
        },
        {
            "id": 47,
            "name": "Câu cá",
            "e_id": 612
        },
        {
            "id": 48,
            "name": "Xăm hình",
            "e_id": 613
        },
        {
            "id": 49,
            "name": "Thời trang",
            "e_id": 614
        },
        {
            "id": 50,
            "name": "Làm đẹp",
            "e_id": 615
        },
        {
            "id": 51,
            "name": "Chương trình ti vi",
            "e_id": 616
        },
        {
            "id": 52,
            "name": "Trò chơi truyền hình",
            "e_id": 617
        },
        {
            "id": 53,
            "name": "Đọc",
            "e_id": 618
        },
        {
            "id": 54,
            "name": "Sổ xố",
            "e_id": 619
        },
        {
            "id": 55,
            "name": "Nghệ thuật",
            "e_id": 620
        },
        {
            "id": 56,
            "name": "Tử vi",
            "e_id": 621
        },
        {
            "id": 57,
            "name": "Game",
            "e_id": 622
        },
        {
            "id": 58,
            "name": "Kỹ năng sống",
            "e_id": 623
        },
        {
            "id": 59,
            "name": "Phong thủy",
            "e_id": 624
        },
        {
            "id": 60,
            "name": "Văn chương",
            "e_id": 625
        },
        {
            "id": 61,
            "name": "Truyện cười",
            "e_id": 626
        },
        {
            "id": 62,
            "name": "Ảnh, Chụp ảnh",
            "e_id": 627
        },
        {
            "id": 63,
            "name": "Vẽ",
            "e_id": 628
        },
        {
            "id": 64,
            "name": "Kinh doanh và công nghiệp",
            "e_id": 701
        },
        {
            "id": 65,
            "name": "Kinh doanh",
            "e_id": 702
        },
        {
            "id": 66,
            "name": "Doanh nghiệp",
            "e_id": 703
        },
        {
            "id": 67,
            "name": "Địa ốc",
            "e_id": 704
        },
        {
            "id": 68,
            "name": "Chứng khoán",
            "e_id": 705
        },
        {
            "id": 69,
            "name": "Vàng",
            "e_id": 706
        },
        {
            "id": 70,
            "name": "Giá cả thị trường",
            "e_id": 707
        },
        {
            "id": 71,
            "name": "Tài chính",
            "e_id": 708
        },
        {
            "id": 72,
            "name": "Ngân hàng",
            "e_id": 709
        },
        {
            "id": 73,
            "name": "Khởi nghiệp",
            "e_id": 710
        },
        {
            "id": 74,
            "name": "Mua sắm và thời trang",
            "e_id": 801
        },
        {
            "id": 75,
            "name": "Mua sắm",
            "e_id": 802
        },
        {
            "id": 76,
            "name": "Mỹ phẩm",
            "e_id": 803
        },
        {
            "id": 77,
            "name": "Quần áo",
            "e_id": 804
        },
        {
            "id": 78,
            "name": "Giày dép",
            "e_id": 805
        },
        {
            "id": 79,
            "name": "Phụ kiện thời trang",
            "e_id": 806
        },
        {
            "id": 80,
            "name": "Đồ trang sức",
            "e_id": 807
        },
        {
            "id": 81,
            "name": "Đồ thể thao",
            "e_id": 808
        },
        {
            "id": 82,
            "name": "Thức ăn và đồ uống",
            "e_id": 901
        },
        {
            "id": 83,
            "name": "Làm bánh",
            "e_id": 902
        },
        {
            "id": 84,
            "name": "Nấu ăn",
            "e_id": 903
        },
        {
            "id": 85,
            "name": "Nhà hàng",
            "e_id": 904
        },
        {
            "id": 86,
            "name": "Cà phê",
            "e_id": 905
        },
        {
            "id": 87,
            "name": "Đồ uống có cồn",
            "e_id": 906
        },
        {
            "id": 88,
            "name": "Vấn đề chính trị xã hội",
            "e_id": 1001
        },
        {
            "id": 89,
            "name": "Chính trị",
            "e_id": 1002
        },
        {
            "id": 90,
            "name": "Quân đội",
            "e_id": 1003
        },
        {
            "id": 91,
            "name": "Luật",
            "e_id": 1004
        },
        {
            "id": 92,
            "name": "Tôn giáo",
            "e_id": 1005
        },
        {
            "id": 93,
            "name": "Đạo phật",
            "e_id": 1006
        },
        {
            "id": 94,
            "name": "Thiên chúa giáo",
            "e_id": 1007
        },
        {
            "id": 95,
            "name": "Đạo hồi",
            "e_id": 1008
        },
        {
            "id": 96,
            "name": "Tâm linh",
            "e_id": 1009
        },
        {
            "id": 97,
            "name": "Chuyện xã hội",
            "e_id": 1010
        },
        {
            "id": 98,
            "name": "Gia đình và các mối quan hệ",
            "e_id": 1101
        },
        {
            "id": 99,
            "name": "Hẹn hò",
            "e_id": 1102
        },
        {
            "id": 100,
            "name": "Đám cưới",
            "e_id": 1103
        },
        {
            "id": 101,
            "name": "Gia đình",
            "e_id": 1104
        },
        {
            "id": 102,
            "name": "Nuôi dạy con",
            "e_id": 1105
        },
        {
            "id": 103,
            "name": "Làm mẹ",
            "e_id": 1106
        },
        {
            "id": 104,
            "name": "Sức khỏe",
            "e_id": 1107
        },
        {
            "id": 105,
            "name": "Tâm sự",
            "e_id": 1108
        },
        {
            "id": 106,
            "name": "Giáo dục",
            "e_id": 1201
        },
        {
            "id": 107,
            "name": "Tuyển sinh",
            "e_id": 1202
        },
        {
            "id": 108,
            "name": "Du học",
            "e_id": 1203
        },
        {
            "id": 109,
            "name": "Học tiếng Anh",
            "e_id": 1204
        },
        {
            "id": 110,
            "name": "Học tiếng Pháp",
            "e_id": 1205
        },
        {
            "id": 111,
            "name": "Học tiếng Trung",
            "e_id": 1206
        },
        {
            "id": 112,
            "name": "Học tiếng nhật",
            "e_id": 1207
        },
        {
            "id": 113,
            "name": "Học tiếng hàn",
            "e_id": 1208
        },
        {
            "id": 114,
            "name": "Học toán",
            "e_id": 1209
        },
        {
            "id": 115,
            "name": "Học hóa",
            "e_id": 1210
        },
        {
            "id": 116,
            "name": "Học lý",
            "e_id": 1211
        },
        {
            "id": 117,
            "name": "Phương tiện",
            "e_id": 1301
        },
        {
            "id": 118,
            "name": "Ô tô",
            "e_id": 1302
        },
        {
            "id": 119,
            "name": "Xe máy",
            "e_id": 1303
        },
        {
            "id": 120,
            "name": "Xe máy Dream",
            "e_id": 1304
        },
        {
            "id": 121,
            "name": "Xe máy Exciter",
            "e_id": 1305
        },
        {
            "id": 122,
            "name": "Xe đạp",
            "e_id": 1306
        },
        {
            "id": 123,
            "name": "Xe máy Vespa",
            "e_id": 1307
        },
        {
            "id": 124,
            "name": "Xe máy Winner",
            "e_id": 1308
        },
        {
            "id": 125,
            "name": "Xe máy SH",
            "e_id": 1309
        },
        {
            "id": 126,
            "name": "Lịch sử và văn hóa",
            "e_id": 1401
        },
        {
            "id": 127,
            "name": "Lịch sử",
            "e_id": 1402
        },
        {
            "id": 128,
            "name": "Văn hóa",
            "e_id": 1403
        },
        {
            "id": 129,
            "name": "Nhà",
            "e_id": 1501
        },
        {
            "id": 130,
            "name": "Nội thất",
            "e_id": 1502
        },
        {
            "id": 131,
            "name": "Ngoại thất",
            "e_id": 1503
        },
        {
            "id": 132,
            "name": "Thú cưng",
            "e_id": 1601
        },
        {
            "id": 133,
            "name": "Gà chọi",
            "e_id": 1602
        },
        {
            "id": 134,
            "name": "Cây cảnh",
            "e_id": 1603
        },
        {
            "id": 135,
            "name": "Hoa",
            "e_id": 1604
        },
        {
            "id": 136,
            "name": "Hoa lan",
            "e_id": 1605
        },
        {
            "id": 137,
            "name": "Hoa hồng",
            "e_id": 1606
        },
        {
            "id": 138,
            "name": "Cá cảnh",
            "e_id": 1607
        },
        {
            "id": 139,
            "name": "Cắm hoa",
            "e_id": 1608
        },
        {
            "id": 140,
            "name": "Sưu Tầm",
            "e_id": 1609
        },
        {
            "id": 141,
            "name": "Nông nghiệp",
            "e_id": 1701
        },
        {
            "id": 142,
            "name": "Kiến trúc",
            "e_id": 1702
        },
        {
            "id": 143,
            "name": "Xây dựng",
            "e_id": 1703
        },
        {
            "id": 144,
            "name": "Thiết kế",
            "e_id": 1704
        },
        {
            "id": 145,
            "name": "Kinh tế học",
            "e_id": 1705
        },
        {
            "id": 146,
            "name": "Kỹ thuật",
            "e_id": 1706
        },
        {
            "id": 147,
            "name": "Quảng cáo",
            "e_id": 1707
        },
        {
            "id": 148,
            "name": "Handmade",
            "e_id": 1708
        },
        {
            "id": 149,
            "name": "Lập trình",
            "e_id": 1709
        },
        {
            "id": 150,
            "name": "Đồ cổ",
            "e_id": 202
        },
        {
            "id": 151,
            "name": "Đồ đã qua sử dụng",
            "e_id": 203
        },
        {
            "id": 152,
            "name": "Đồng hồ đeo tay",
            "e_id": 204
        },
        {
            "id": 153,
            "name": "Đồ bơi",
            "e_id": 205
        },
        {
            "id": 154,
            "name": "Đàn ghita",
            "e_id": 206
        },
        {
            "id": 155,
            "name": "Cờ vua/Cờ tướng",
            "e_id": 408
        },
        {
            "id": 156,
            "name": "Gym",
            "e_id": 414
        },
        {
            "id": 157,
            "name": "Võ thuật",
            "e_id": 422
        },
        {
            "id": 158,
            "name": "Điêu khắc",
            "e_id": 629
        },
        {
            "id": 159,
            "name": "Truyện ma kinh dị",
            "e_id": 630
        },
        {
            "id": 160,
            "name": "Truyện tranh",
            "e_id": 631
        },
        {
            "id": 161,
            "name": "Trang điểm",
            "e_id": 632
        },
        {
            "id": 162,
            "name": "Tạo mẫu tóc",
            "e_id": 633
        },
        {
            "id": 163,
            "name": "Môn Sinh học",
            "e_id": 1212
        },
        {
            "id": 164,
            "name": "Học tiếng Thái Lan",
            "e_id": 1213
        },
        {
            "id": 165,
            "name": "Phụ tùng ô tô",
            "e_id": 1310
        },
        {
            "id": 166,
            "name": "Phụ tùng xe máy",
            "e_id": 1311
        },
        {
            "id": 167,
            "name": "Xe máy điện",
            "e_id": 1312
        },
        {
            "id": 168,
            "name": "Xe đạp điện",
            "e_id": 1313
        },
        {
            "id": 169,
            "name": "Xe máy Win",
            "e_id": 1314
        },
        {
            "id": 170,
            "name": "Xe máy SimSon",
            "e_id": 1315
        },
        {
            "id": 171,
            "name": "Xe buýt",
            "e_id": 1316
        },
        {
            "id": 172,
            "name": "Hạt giống",
            "e_id": 1610
        },
        {
            "id": 173,
            "name": "Phim Thái Lan",
            "e_id": 1801
        },
        {
            "id": 174,
            "name": "Phim ma/Kinh dị",
            "e_id": 1802
        },
        {
            "id": 175,
            "name": "Phim võ thuật",
            "e_id": 1803
        },
        {
            "id": 176,
            "name": "Dược sĩ",
            "e_id": 1901
        },
        {
            "id": 177,
            "name": "Y học/Y khoa",
            "e_id": 1902
        },
        {
            "id": 178,
            "name": "Dược phẩm/Thuốc chữa bệnh",
            "e_id": 1903
        },
        {
            "id": 179,
            "name": "Chăn nuôi",
            "e_id": 2001
        },
        {
            "id": 180,
            "name": "Thú ý",
            "e_id": 2002
        },
        {
            "id": 181,
            "name": "Vận chuyển",
            "e_id": 2003
        },
        {
            "id": 182,
            "name": "Lái xe",
            "e_id": 2004
        },
        {
            "id": 183,
            "name": "Diễn giả",
            "e_id": 2005
        },
        {
            "id": 184,
            "name": "Gia sư",
            "e_id": 2006
        },
        {
            "id": 185,
            "name": "Kế toán",
            "e_id": 2007
        },
        {
            "id": 186,
            "name": "Tiếp thị",
            "e_id": 2008
        },
        {
            "id": 187,
            "name": "Thông dịch viên",
            "e_id": 2009
        },
        {
            "id": 188,
            "name": "Nghề mộc/Đồ gỗ",
            "e_id": 2010
        },
        {
            "id": 189,
            "name": "Đồ thêu",
            "e_id": 2011
        },
        {
            "id": 190,
            "name": "May mặc",
            "e_id": 2012
        },
        {
            "id": 191,
            "name": "Thủy sản",
            "e_id": 2013
        },
        {
            "id": 192,
            "name": "Xe taxi",
            "e_id": 2014
        },
        {
            "id": 193,
            "name": "Mạng viễn thông",
            "e_id": 2015
        },
        {
            "id": 194,
            "name": "Công nghệ sinh học",
            "e_id": 2016
        },
        {
            "id": 195,
            "name": "Tranh đá quý",
            "e_id": 2017
        },
        {
            "id": 196,
            "name": "Cơ khí",
            "e_id": 2018
        },
        {
            "id": 197,
            "name": "Thanh lý",
            "e_id": 2019
        },
        {
            "id": 198,
            "name": "Phụ kiện thú cưng",
            "e_id": 2020
        },
        {
            "id": 199,
            "name": "Đồ chơi",
            "e_id": 2021
        },
        {
            "id": 200,
            "name": "Thủ công mỹ nghệ",
            "e_id": 2022
        },
        {
            "id": 201,
            "name": "Linh kiện điện tử",
            "e_id": 2023
        },
        {
            "id": 202,
            "name": "Dụng cụ thể thao",
            "e_id": 2024
        },
        {
            "id": 203,
            "name": "Tổ chức sự kiện",
            "e_id": 2025
        },
        {
            "id": 204,
            "name": "Triết học",
            "e_id": 2026
        },
        {
            "id": 205,
            "name": "Đồ lót/Nội y",
            "e_id": 2027
        },
        {
            "id": 206,
            "name": "Tiểu thuyết/Truyện ngắn",
            "e_id": 2028
        },
        {
            "id": 207,
            "name": "Bảo hiểm",
            "e_id": 2029
        },
        {
            "id": 208,
            "name": "Thiết bị điện/Điện tử",
            "e_id": 2030
        },
        {
            "id": 209,
            "name": "Mẹo vặt/Thủ thuật",
            "e_id": 2031
        },
        {
            "id": 300,
            "name": "Kỹ sư",
            "e_id": 2032
        },
        {
            "id": 301,
            "name": "Đồ gốm",
            "e_id": 2033
        },
        {
            "id": 302,
            "name": "Công an",
            "e_id": 2034
        },
        {
            "id": 303,
            "name": "Dịch thuật",
            "e_id": 2035
        },
        {
            "id": 304,
            "name": "Phụ tùng xe điện",
            "e_id": 2036
        },
        {
            "id": 305,
            "name": "Rượu mạnh",
            "e_id": 2037
        },
        {
            "id": 306,
            "name": "Đan móc",
            "e_id": 2038
        },
        {
            "id": 307,
            "name": "Thợ sửa xe",
            "e_id": 2039
        }
    ]
    for hobby in hobby_data:
        hobby["display_in_form"] = True
        lst.append(hobby)
    return lst
