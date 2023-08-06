def df_get_job_data():
    lst = []
    job_data = [
        {
            "id": 1,
            "name": "Làm ruộng",
            "display_in_form": True
        },
        {
            "id": 2,
            "name": "Bác sỹ",
            "display_in_form": True
        },
        {
            "id": 3,
            "name": "Bán hàng ăn uống",
            "display_in_form": True
        },
        {
            "id": 4,
            "name": "Bán hàng giải khát",
            "display_in_form": True
        },
        {
            "id": 5,
            "name": "Bất động sản",
            "display_in_form": True
        },
        {
            "id": 6,
            "name": "Bộ đội",
            "display_in_form": True
        },
        {
            "id": 7,
            "name": "Bộ đội xuất ngũ",
            "display_in_form": True
        },
        {
            "id": 8,
            "name": "Bốc vác",
            "display_in_form": True
        },
        {
            "id": 9,
            "name": "Buôn bán",
            "display_in_form": True
        },
        {
            "id": 10,
            "name": "Ca sỹ",
            "display_in_form": True
        },
        {
            "id": 11,
            "name": "Cán bộ",
            "display_in_form": True
        },
        {
            "id": 12,
            "name": "Cắt tóc",
            "display_in_form": True
        },
        {
            "id": 13,
            "name": "Cầu đường",
            "display_in_form": True
        },
        {
            "id": 14,
            "name": "Chăn nuôi",
            "display_in_form": True
        },
        {
            "id": 15,
            "name": "Chế biến nông sản",
            "display_in_form": True
        },
        {
            "id": 16,
            "name": "Chủ nhiệm HTX",
            "display_in_form": True
        },
        {
            "id": 17,
            "name": "Công an",
            "display_in_form": True
        },
        {
            "id": 18,
            "name": "Công nhân",
            "display_in_form": True
        },
        {
            "id": 19,
            "name": "Cơ khí",
            "display_in_form": True
        },
        {
            "id": 20,
            "name": "Cơ quan dân chính Đảng",
            "display_in_form": True
        },
        {
            "id": 21,
            "name": "Dạy học",
            "display_in_form": True
        },
        {
            "id": 22,
            "name": "Đánh bắt thuỷ sản",
            "display_in_form": True
        },
        {
            "id": 23,
            "name": "Điện toán ngân hàng",
            "display_in_form": True
        },
        {
            "id": 24,
            "name": "Điều dưỡng",
            "display_in_form": True
        },
        {
            "id": 25,
            "name": "Giám đốc",
            "display_in_form": True
        },
        {
            "id": 26,
            "name": "Giáo viên",
            "display_in_form": True
        },
        {
            "id": 27,
            "name": "Hải quan",
            "display_in_form": True
        },
        {
            "id": 28,
            "name": "Hành nghề y",
            "display_in_form": True
        },
        {
            "id": 29,
            "name": "Học sinh",
            "display_in_form": True
        },
        {
            "id": 30,
            "name": "Học sinh phổ thông",
            "display_in_form": True
        },
        {
            "id": 31,
            "name": "Học sinh trung cấp KTD Nghề",
            "display_in_form": True
        },
        {
            "id": 32,
            "name": "Học Viên",
            "display_in_form": True
        },
        {
            "id": 33,
            "name": "Hội hoạ",
            "display_in_form": True
        },
        {
            "id": 34,
            "name": "IT",
            "display_in_form": True
        },
        {
            "id": 35,
            "name": "Kế hoạch vật tư",
            "display_in_form": True
        },
        {
            "id": 36,
            "name": "Kế toán",
            "display_in_form": True
        },
        {
            "id": 37,
            "name": "Kiểm ngân",
            "display_in_form": True
        },
        {
            "id": 38,
            "name": "Kiểm sát viên",
            "display_in_form": True
        },
        {
            "id": 39,
            "name": "Kiến trúc",
            "display_in_form": True
        },
        {
            "id": 40,
            "name": "Kinh doanh",
            "display_in_form": True
        },
        {
            "id": 41,
            "name": "Kinh doanh Karaoke",
            "display_in_form": True
        },
        {
            "id": 42,
            "name": "Kỹ Sư",
            "display_in_form": True
        },
        {
            "id": 43,
            "name": "Kỹ thuật điện",
            "display_in_form": True
        },
        {
            "id": 44,
            "name": "Lái tàu hoả",
            "display_in_form": True
        },
        {
            "id": 45,
            "name": "Lái xe",
            "display_in_form": True
        },
        {
            "id": 46,
            "name": "Lao động tự do",
            "display_in_form": True
        },
        {
            "id": 47,
            "name": "Lâm nghiệp",
            "display_in_form": True
        },
        {
            "id": 48,
            "name": "Lập trình",
            "display_in_form": True
        },
        {
            "id": 49,
            "name": "Linh mục",
            "display_in_form": True
        },
        {
            "id": 50,
            "name": "Luật sư",
            "display_in_form": True
        },
        {
            "id": 51,
            "name": "Marketing",
            "display_in_form": True
        },
        {
            "id": 52,
            "name": "May mặc",
            "display_in_form": True
        },
        {
            "id": 53,
            "name": "Nha Sỹ",
            "display_in_form": True
        },
        {
            "id": 54,
            "name": "Nhà Báo",
            "display_in_form": True
        },
        {
            "id": 55,
            "name": "Ngân hàng",
            "display_in_form": True
        },
        {
            "id": 56,
            "name": "Nghỉ chế độ 176",
            "display_in_form": True
        },
        {
            "id": 57,
            "name": "Nghỉ hưu",
            "display_in_form": True
        },
        {
            "id": 58,
            "name": "Nhân viên",
            "display_in_form": True
        },
        {
            "id": 59,
            "name": "Nhân viên bảo vệ",
            "display_in_form": True
        },
        {
            "id": 60,
            "name": "Nhân viên nhà hàng",
            "display_in_form": True
        },
        {
            "id": 61,
            "name": "Nội trợ",
            "display_in_form": True
        },
        {
            "id": 62,
            "name": "P/Giám đốc",
            "display_in_form": True
        },
        {
            "id": 63,
            "name": "Phó Tổng giám đốc",
            "display_in_form": True
        },
        {
            "id": 64,
            "name": "Phụ xe ô tô",
            "display_in_form": True
        },
        {
            "id": 65,
            "name": "Sinh Viên",
            "display_in_form": True
        },
        {
            "id": 66,
            "name": "Sinh viên cao đẳng",
            "display_in_form": True
        },
        {
            "id": 67,
            "name": "Sinh viên đại học",
            "display_in_form": True
        },
        {
            "id": 68,
            "name": "Sơn",
            "display_in_form": True
        },
        {
            "id": 69,
            "name": "Sửa chữa điện tử",
            "display_in_form": True
        },
        {
            "id": 70,
            "name": "Sửa chữa ôtô điện máy",
            "display_in_form": True
        },
        {
            "id": 71,
            "name": "Sửa chữa xe máy",
            "display_in_form": True
        },
        {
            "id": 72,
            "name": "Thợ ảnh",
            "display_in_form": True
        },
        {
            "id": 73,
            "name": "Thợ hàn",
            "display_in_form": True
        },
        {
            "id": 74,
            "name": "Thợ mộc",
            "display_in_form": True
        },
        {
            "id": 75,
            "name": "Thợ sắt",
            "display_in_form": True
        },
        {
            "id": 76,
            "name": "Thợ Sơn",
            "display_in_form": True
        },
        {
            "id": 77,
            "name": "Thợ xây",
            "display_in_form": True
        },
        {
            "id": 78,
            "name": "Thú y",
            "display_in_form": True
        },
        {
            "id": 79,
            "name": "Thủ kho",
            "display_in_form": True
        },
        {
            "id": 80,
            "name": "Thủ quỹ",
            "display_in_form": True
        },
        {
            "id": 81,
            "name": "Thuế vụ",
            "display_in_form": True
        },
        {
            "id": 82,
            "name": "Thuỷ lợi",
            "display_in_form": True
        },
        {
            "id": 83,
            "name": "Thuỷ thủ tàu biển",
            "display_in_form": True
        },
        {
            "id": 84,
            "name": "Tổng Giám đốc",
            "display_in_form": True
        },
        {
            "id": 85,
            "name": "Tu sỹ",
            "display_in_form": True
        },
        {
            "id": 86,
            "name": "Văn nghệ sỹ",
            "display_in_form": True
        },
        {
            "id": 87,
            "name": "Vệ sinh môi trường",
            "display_in_form": True
        },
        {
            "id": 88,
            "name": "Viễn thông",
            "display_in_form": True
        },
        {
            "id": 89,
            "name": "Xe ôm",
            "display_in_form": True
        },
        {
            "id": 90,
            "name": "Xích lô",
            "display_in_form": True
        },
        {
            "id": 91,
            "name": "Y tá",
            "display_in_form": True
        },
        {
            "id": 92,
            "name": "Khác",
            "display_in_form": True
        },
        {
            "id": 93,
            "name": "Giảng viên",
            "display_in_form": True
        }
    ]
    for job in job_data:
        job["display_in_form"] = True
        lst.append(job)
    return lst
