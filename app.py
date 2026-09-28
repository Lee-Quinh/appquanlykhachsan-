Import streamlit as st
Import sqlite3
Import pandas as pd
From datetime import datetime, date
Import os

# =========================================================
# CẤU HÌNH APP
# =========================================================

St.set_page_config(
    Page_title=”Hotel Room Management”,
    Page_icon=””,
    Layout=”wide”,
    Initial_sidebar_state=”expanded”
)

DB_FILE = “hotel.db”


# =========================================================
# DATABASE
# =========================================================

Def get_connection():
    Conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    Conn.row_factory = sqlite3.Row
    Return conn


Def init_database():
    Conn = get_connection()
    Cursor = conn.cursor()

    # Bảng phòng
    Cursor.execute(“””
        CREATE TABLE IF NOT EXISTS rooms (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Room_number TEXT UNIQUE NOT NULL,
            Room_type TEXT NOT NULL,
            Floor INTEGER NOT NULL,
            Price REAL NOT NULL,
            Status TEXT NOT NULL DEFAULT ‘Trống’,
            Note TEXT DEFAULT ‘’
        )
    “””)

    # Bảng đặt phòng
    Cursor.execute(“””
        CREATE TABLE IF NOT EXISTS bookings (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Guest_name TEXT NOT NULL,
            Phone TEXT,
            Room_number TEXT NOT NULL,
            Room_type TEXT,
            Check_in TEXT NOT NULL,
            Check_out TEXT NOT NULL,
            Guests INTEGER DEFAULT 1,
            Price_per_night REAL DEFAULT 0,
            Total_amount REAL DEFAULT 0,
            Status TEXT DEFAULT ‘Đã đặt’,
            Created_at TEXT
        )
    “””)

    # Bảng lịch sử
    Cursor.execute(“””
        CREATE TABLE IF NOT EXISTS history (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Room_number TEXT,
            Action TEXT,
            Guest_name TEXT,
            Amount REAL DEFAULT 0,
            Action_time TEXT
        )
    “””)

    # Nếu chưa có phòng thì tạo dữ liệu mẫu
    Cursor.execute(“SELECT COUNT(*) FROM rooms”)
    Room_count = cursor.fetchone()[0]

    If room_count == 0:
        Rooms = [
            (“101”, “Standard”, 1, 650000, “Trống”, “”),
            (“102”, “Standard”, 1, 650000, “Trống”, “”),
            (“103”, “Standard”, 1, 650000, “Trống”, “”),
            (“104”, “Standard”, 1, 650000, “Trống”, “”),
            (“201”, “Deluxe”, 2, 850000, “Trống”, “”),
            (“202”, “Deluxe”, 2, 850000, “Trống”, “”),
            (“203”, “Deluxe”, 2, 850000, “Trống”, “”),
            (“204”, “Deluxe”, 2, 850000, “Trống”, “”),
            (“301”, “Superior”, 3, 1000000, “Trống”, “”),
            (“302”, “Superior”, 3, 1000000, “Trống”, “”),
            (“303”, “Superior”, 3, 1000000, “Trống”, “”),
            (“304”, “Superior”, 3, 1000000, “Trống”, “”),
            (“401”, “Suite”, 4, 1500000, “Trống”, “”),
            (“402”, “Suite”, 4, 1500000, “Trống”, “”),
            (“501”, “VIP”, 5, 2500000, “Trống”, “”),
            (“502”, “VIP”, 5, 2500000, “Trống”, “”),
        ]

        Cursor.executemany(“””
            INSERT INTO rooms
            (room_number, room_type, floor, price, status, note)
            VALUES (?, ?, ?, ?, ?, ?)
        “””, rooms)

    Conn.commit()
    Conn.close()


Init_database()


# =========================================================
# HÀM DATABASE
# =========================================================

Def query_df(query, params=()):
    Conn = get_connection()
    Df = pd.read_sql_query(query, conn, params=params)
    Conn.close()
    Return df


Def execute_query(query, params=()):
    Conn = get_connection()
    Cursor = conn.cursor()
    Cursor.execute(query, params)
    Conn.commit()
    Last_id = cursor.lastrowid
    Conn.close()
    Return last_id


Def get_room(room_number):
    Conn = get_connection()
    Cursor = conn.cursor()
    Cursor.execute(
        “SELECT * FROM rooms WHERE room_number = ?”,
        (room_number,)
    )
    Room = cursor.fetchone()
    Conn.close()
    Return room


Def update_room_status(room_number, status):
    Execute_query(
        “UPDATE rooms SET status = ? WHERE room_number = ?”,
        (status, room_number)
    )


Def add_history(room_number, action, guest_name=””, amount=0):
    Execute_query(“””
        INSERT INTO history
        (room_number, action, guest_name, amount, action_time)
        VALUES (?, ?, ?, ?, ?)
    “””, (
        Room_number,
        Action,
        Guest_name,
        Amount,
        Datetime.now().strftime(“%Y-%m-%d %H:%M:%S”)
    ))


# =========================================================
# FORMAT TIỀN
# =========================================================

Def format_money(value):
    Return f”{value:,.0f} VNĐ”


# =========================================================
# SIDEBAR
# =========================================================

St.sidebar.title(“ HOTEL MANAGER”)
St.sidebar.caption(“Hệ thống quản lý phòng khách sạn”)

Menu = st.sidebar.radio(
    “MENU”,
    [
        “ Tổng quan”,
        “️ Quản lý phòng”,
        “ Đặt phòng”,
        “ Check-in”,
        “ Check-out”,
        “ Bảo trì phòng”,
        “ Lịch sử”
    ]
)

St.sidebar.divider()

St.sidebar.info(
    “ Hệ thống sử dụng SQLite nên dữ liệu sẽ được lưu “
    “trong file hotel.db ngay tại thư mục chạy app.”
)


# =========================================================
# CSS
# =========================================================

St.markdown(“””
<style>
    .main-title {
        Font-size: 32px;
        Font-weight: 700;
        Margin-bottom: 5px;
    }

    .sub-title {
        Color: #666;
        Margin-bottom: 25px;
    }

    Div[data-testid=”stMetric”] {
        Border: 1px solid #e5e5e5;
        Border-radius: 12px;
        Padding: 15px;
        Background-color: #fafafa;
    }

    .room-card {
        Border: 1px solid #ddd;
        Border-radius: 12px;
        Padding: 15px;
        Margin-bottom: 10px;
        Background-color: #ffffff;
    }

    .status {
        Font-weight: bold;
    }

    .footer {
        Text-align: center;
        Color: #888;
        Margin-top: 40px;
        Padding: 20px;
    }
</style>
“””, unsafe_allow_html=True)


# =========================================================
# 1. DASHBOARD
# =========================================================

If menu == “ Tổng quan”:

    St.markdown(
        ‘<div class=”main-title”> Tổng quan khách sạn</div>’,
        Unsafe_allow_html=True
    )

    St.markdown(
        ‘<div class=”sub-title”>Theo dõi tình trạng phòng và hoạt động kinh doanh</div>’,
        Unsafe_allow_html=True
    )

    Rooms_df = query_df(“SELECT * FROM rooms”)
    Bookings_df = query_df(“SELECT * FROM bookings”)

    Total_rooms = len(rooms_df)

    Available_rooms = len(
        Rooms_df[rooms_df[“status”] == “Trống”]
    )

    Occupied_rooms = len(
        Rooms_df[rooms_df[“status”] == “Đang ở”]
    )

    Reserved_rooms = len(
        Rooms_df[rooms_df[“status”] == “Đã đặt”]
    )

    Maintenance_rooms = len(
        Rooms_df[rooms_df[“status”] == “Bảo trì”]
    )

    Revenue = bookings_df[
        Bookings_df[“status”] == “Đã trả phòng”
    ][“total_amount”].sum()

    Col1, col2, col3, col4 = st.columns(4)

    Col1.metric(“ Tổng phòng”, total_rooms)
    Col2.metric(“🟢 Phòng trống”, available_rooms)
    Col3.metric(“🔴 Đang có khách”, occupied_rooms)
    Col4.metric(“🟡 Đã đặt”, reserved_rooms)

    St.divider()

    Col1, col2, col3 = st.columns(3)

    Col1.metric(“ Bảo trì”, maintenance_rooms)
    Col2.metric(“ Doanh thu đã thu”, format_money(revenue))
    Col3.metric(
        “ Công suất phòng”,
        F”{(occupied_rooms / total_rooms * 100):.1f}%”
        If total_rooms > 0 else “0%”
    )

    St.divider()

    St.subheader(“️ Tình trạng phòng”)

    Status_count = rooms_df[“status”].value_counts()

    Col1, col2 = st.columns(2)

    With col1:
        St.bar_chart(status_count)

    With col2:
        Status_table = pd.DataFrame({
            “Trạng thái”: status_count.index,
            “Số phòng”: status_count.values
        })

        St.dataframe(
            Status_table,
            Use_container_width=True,
            Hide_index=True
        )

    St.subheader(“ Các booking gần đây”)

    Recent_bookings = query_df(“””
        SELECT
            Id AS ‘Mã’,
            Guest_name AS ‘Khách hàng’,
            Phone AS ‘SĐT’,
            Room_number AS ‘Phòng’,
            Check_in AS ‘Check-in’,
            Check_out AS ‘Check-out’,
            Total_amount AS ‘Tổng tiền’,
            Status AS ‘Trạng thái’
        FROM bookings
        ORDER BY id DESC
        LIMIT 10
    “””)

    If len(recent_bookings) > 0:
        St.dataframe(
            Recent_bookings,
            Use_container_width=True,
            Hide_index=True
        )
    Else:
        St.info(“Chưa có booking nào.”)


# =========================================================
# 2. QUẢN LÝ PHÒNG
# =========================================================

Elif menu == “️ Quản lý phòng”:

    St.markdown(
        ‘<div class=”main-title”>️ Quản lý phòng</div>’,
        Unsafe_allow_html=True
    )

    Rooms_df = query_df(“SELECT * FROM rooms ORDER BY floor, room_number”)

    Col1, col2, col3 = st.columns(3)

    With col1:
        Search = st.text_input(
            “ Tìm phòng”,
            Placeholder=”Nhập số phòng...”
        )

    With col2:
        Status_filter = st.selectbox(
            “Trạng thái”,
            [
                “Tất cả”,
                “Trống”,
                “Đã đặt”,
                “Đang ở”,
                “Bảo trì”,
                “Đang dọn”
            ]
        )

    With col3:
        Type_filter = st.selectbox(
            “Loại phòng”,
            [“Tất cả”] + sorted(rooms_df[“room_type”].unique().tolist())
        )

    Filtered = rooms_df.copy()

    If search:
        Filtered = filtered[
            Filtered[“room_number”]
            .astype(str)
            .str.contains(search, case=False)
        ]

    If status_filter != “Tất cả”:
        Filtered = filtered[
            Filtered[“status”] == status_filter
        ]

    If type_filter != “Tất cả”:
        Filtered = filtered[
            Filtered[“room_type”] == type_filter
        ]

    St.write(f”**Hiển thị {len(filtered)} phòng**”)

    # Hiển thị từng phòng
    For _, room in filtered.iterrows():

        Col1, col2, col3, col4, col5 = st.columns(
            [1, 1.5, 1, 1.5, 2]
        )

        Col1.write(f”### ️ {room[‘room_number’]}”)
        Col2.write(f”**{room[‘room_type’]}**”)
        Col3.write(f”Tầng {room[‘floor’]}”)
        Col4.write(format_money(room[“price”]))

        With col5:

            Status_options = [
                “Trống”,
                “Đã đặt”,
                “Đang ở”,
                “Bảo trì”,
                “Đang dọn”
            ]

            Current_index = (
                Status_options.index(room[“status”])
                If room[“status”] in status_options
                Else 0
            )

            New_status = st.selectbox(
                “Trạng thái”,
                Status_options,
                Index=current_index,
                Key=f”status_{room[‘room_number’]}”
            )

            If new_status != room[“status”]:

                Update_room_status(
                    Room[“room_number”],
                    New_status
                )

                Add_history(
                    Room[“room_number”],
                    F”Cập nhật trạng thái: {room[‘status’]} → {new_status}”
                )

                St.success(
                    F”Phòng {room[‘room_number’]} đã được cập nhật.”
                )

                St.rerun()

        St.divider()

    St.subheader(“➕ Thêm phòng mới”)

    With st.form(“add_room_form”):

        Col1, col2, col3 = st.columns(3)

        With col1:
            Room_number = st.text_input(
                “Số phòng”,
                Placeholder=”Ví dụ: 601”
            )

        With col2:
            Room_type = st.selectbox(
                “Loại phòng”,
                [
                    “Standard”,
                    “Superior”,
                    “Deluxe”,
                    “Suite”,
                    “VIP”
                ]
            )

        With col3:
            Floor = st.number_input(
                “Tầng”,
                Min_value=1,
                Max_value=50,
                Value=1
            )

        Col1, col2 = st.columns(2)

        With col1:
            Price = st.number_input(
                “Giá phòng / đêm”,
                Min_value=0,
                Value=650000,
                Step=50000
            )

        With col2:
            Note = st.text_input(“Ghi chú”)

        Submitted = st.form_submit_button(
            “➕ Thêm phòng”,
            Use_container_width=True
        )

        If submitted:

            If not room_number.strip():
                St.error(“Vui lòng nhập số phòng.”)

            Elif get_room(room_number.strip()):
                St.error(“Số phòng này đã tồn tại.”)

            Else:

                Execute_query(“””
                    INSERT INTO rooms
                    (room_number, room_type, floor, price, status, note)
                    VALUES (?, ?, ?, ?, ?, ?)
                “””, (
                    Room_number.strip(),
                    Room_type,
                    Floor,
                    Price,
                    “Trống”,
                    Note
                ))

                St.success(
                    F”Đã thêm phòng {room_number}.”
                )

                St.rerun()


# =========================================================
# 3. ĐẶT PHÒNG
# =========================================================

Elif menu == “ Đặt phòng”:

    St.markdown(
        ‘<div class=”main-title”> Đặt phòng</div>’,
        Unsafe_allow_html=True
    )

    Rooms_df = query_df(“””
        SELECT *
        FROM rooms
        WHERE status = ‘Trống’
        ORDER BY room_number
    “””)

    If len(rooms_df) == 0:

        St.warning(“Hiện không có phòng trống.”)

    Else:

        With st.form(“booking_form”):

            St.subheader(“ Thông tin khách hàng”)

            Col1, col2 = st.columns(2)

            With col1:
                Guest_name = st.text_input(
                    “Họ và tên khách *”
                )

            With col2:
                Phone = st.text_input(
                    “Số điện thoại”
                )

            Col1, col2 = st.columns(2)

            With col1:
                Room_number = st.selectbox(
                    “Chọn phòng”,
                    Rooms_df[“room_number”].tolist()
                )

            With col2:
                Guests = st.number_input(
                    “Số khách”,
                    Min_value=1,
                    Max_value=20,
                    Value=1
                )

            Col1, col2 = st.columns(2)

            With col1:
                Check_in = st.date_input(
                    “Ngày check-in”,
                    Value=date.today()
                )

            With col2:
                Check_out = st.date_input(
                    “Ngày check-out”,
                    Value=date.today()
                )

            Selected_room = get_room(room_number)

            Price_per_night = selected_room[“price”]

            If check_out > check_in:
                Nights = (check_out – check_in).days
            Else:
                Nights = 0

            Total_amount = price_per_night * nights

            St.info(
                F”Giá phòng: **{format_money(price_per_night)} / đêm**  \n”
                F”Số đêm: **{nights}**  \n”
                F”Tổng tiền dự kiến: **{format_money(total_amount)}**”
            )

            Submitted = st.form_submit_button(
                “ Xác nhận đặt phòng”,
                Use_container_width=True
            )

            If submitted:

                If not guest_name.strip():
                    St.error(“Vui lòng nhập tên khách.”)

                Elif check_out <= check_in:
                    St.error(
                        “Ngày check-out phải sau ngày check-in.”
                    )

                Else:

                    Execute_query(“””
                        INSERT INTO bookings
                        (
                            Guest_name,
                            Phone,
                            Room_number,
                            Room_type,
                            Check_in,
                            Check_out,
                            Guests,
                            Price_per_night,
                            Total_amount,
                            Status,
                            Created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    “””, (
                        Guest_name,
                        Phone,
                        Room_number,
                        Selected_room[“room_type”],
                        Str(check_in),
                        Str(check_out),
                        Guests,
                        Price_per_night,
                        Total_amount,
                        “Đã đặt”,
                        Datetime.now().strftime(“%Y-%m-%d %H:%M:%S”)
                    ))

                    Update_room_status(
                        Room_number,
                        “Đã đặt”
                    )

                    Add_history(
                        Room_number,
                        “Đặt phòng”,
                        Guest_name,
                        Total_amount
                    )

                    St.success(
                        F”Đặt phòng {room_number} thành công!”
                    )

                    St.rerun()

    St.divider()

    St.subheader(“ Danh sách đặt phòng”)

    Bookings = query_df(“””
        SELECT
            Id AS ‘Mã booking’,
            Guest_name AS ‘Khách’,
            Phone AS ‘SĐT’,
            Room_number AS ‘Phòng’,
            Check_in AS ‘Check-in’,
            Check_out AS ‘Check-out’,
            Guests AS ‘Số khách’,
            Total_amount AS ‘Tổng tiền’,
            Status AS ‘Trạng thái’
        FROM bookings
        WHERE status = ‘Đã đặt’
        ORDER BY check_in
    “””)

    If len(bookings) > 0:

        St.dataframe(
            Bookings,
            Use_container_width=True,
            Hide_index=True
        )

    Else:
        St.info(“Chưa có booking sắp tới.”)


# =========================================================
# 4. CHECK-IN
# =========================================================

Elif menu == “ Check-in”:

    St.markdown(
        ‘<div class=”main-title”> Check-in</div>’,
        Unsafe_allow_html=True
    )

    Bookings = query_df(“””
        SELECT *
        FROM bookings
        WHERE status = ‘Đã đặt’
        ORDER BY check_in
    “””)

    If len(bookings) == 0:

        St.info(“Không có booking nào đang chờ check-in.”)

    Else:

        Booking_options = {
            F”#{row[‘id’]} – {row[‘guest_name’]} – Phòng {row[‘room_number’]}”:
            Row[“id”]
            For _, row in bookings.iterrows()
        }

        Selected_label = st.selectbox(
            “Chọn booking”,
            List(booking_options.keys())
        )

        Booking_id = booking_options[selected_label]

        Booking = bookings[
            Bookings[“id”] == booking_id
        ].iloc[0]

        St.divider()

        Col1, col2, col3 = st.columns(3)

        Col1.metric(
            “ Khách”,
            Booking[“guest_name”]
        )

        Col2.metric(
            “️ Phòng”,
            Booking[“room_number”]
        )

        Col3.metric(
            “ Tiền phòng”,
            Format_money(booking[“total_amount”])
        )

        St.write(
            F”**Thời gian:** {booking[‘check_in’]} → “
            F”{booking[‘check_out’]}”
        )

        If st.button(
            “✅ Xác nhận Check-in”,
            Use_container_width=True,
            Type=”primary”
        ):

            Execute_query(“””
                UPDATE bookings
                SET status = ‘Đang ở’
                WHERE id = ?
            “””, (booking_id,))

            Update_room_status(
                Booking[“room_number”],
                “Đang ở”
            )

            Add_history(
                Booking[“room_number”],
                “Check-in”,
                Booking[“guest_name”],
                Booking[“total_amount”]
            )

            St.success(
                F”Check-in thành công cho {booking[‘guest_name’]}.”
            )

            St.rerun()


# =========================================================
# 5. CHECK-OUT
# =========================================================

Elif menu == “ Check-out”:

    St.markdown(
        ‘<div class=”main-title”> Check-out</div>’,
        Unsafe_allow_html=True
    )

    Bookings = query_df(“””
        SELECT *
        FROM bookings
        WHERE status = ‘Đang ở’
        ORDER BY check_out
    “””)

    If len(bookings) == 0:

        St.info(“Hiện không có khách đang lưu trú.”)

    Else:

        Booking_options = {
            F”#{row[‘id’]} – {row[‘guest_name’]} – Phòng {row[‘room_number’]}”:
            Row[“id”]
            For _, row in bookings.iterrows()
        }

        Selected_label = st.selectbox(
            “Chọn khách trả phòng”,
            List(booking_options.keys())
        )

        Booking_id = booking_options[selected_label]

        Booking = bookings[
            Bookings[“id”] == booking_id
        ].iloc[0]

        St.divider()

        Col1, col2, col3 = st.columns(3)

        Col1.metric(
            “ Khách hàng”,
            Booking[“guest_name”]
        )

        Col2.metric(
            “️ Phòng”,
            Booking[“room_number”]
        )

        Col3.metric(
            “ Tiền phòng”,
            Format_money(booking[“total_amount”])
        )

        St.write(
            F”**Check-in:** {booking[‘check_in’]}”
        )

        St.write(
            F”**Check-out dự kiến:** {booking[‘check_out’]}”
        )

        St.divider()

        St.subheader(“ Thanh toán”)

        Col1, col2 = st.columns(2)

        With col1:
            Room_charge = st.number_input(
                “Tiền phòng”,
                Min_value=0,
                Value=int(booking[“total_amount”]),
                Step=50000
            )

        With col2:
            Extra_charge = st.number_input(
                “Phụ thu / dịch vụ”,
                Min_value=0,
                Value=0,
                Step=50000
            )

        Total_payment = room_charge + extra_charge

        St.success(
            F”### Tổng thanh toán: {format_money(total_payment)}”
        )

        If st.button(
            “ Xác nhận Check-out”,
            Use_container_width=True,
            Type=”primary”
        ):

            Execute_query(“””
                UPDATE bookings
                SET
                    Status = ‘Đã trả phòng’,
                    Total_amount = ?
                WHERE id = ?
            “””, (
                Total_payment,
                Booking_id
            ))

            # Sau checkout chuyển sang trạng thái đang dọn
            Update_room_status(
                Booking[“room_number”],
                “Đang dọn”
            )

            Add_history(
                Booking[“room_number”],
                “Check-out”,
                Booking[“guest_name”],
                Total_payment
            )

            St.success(
                F”Check-out thành công. “
                F”Phòng {booking[‘room_number’]} chuyển sang trạng thái Đang dọn.”
            )

            St.rerun()


# =========================================================
# 6. BẢO TRÌ
# =========================================================

Elif menu == “ Bảo trì phòng”:

    St.markdown(
        ‘<div class=”main-title”> Quản lý bảo trì</div>’,
        Unsafe_allow_html=True
    )

    Rooms_df = query_df(“””
        SELECT *
        FROM rooms
        WHERE status = ‘Bảo trì’
        ORDER BY room_number
    “””)

    St.subheader(
        F” Đang bảo trì: {len(rooms_df)} phòng”
    )

    If len(rooms_df) > 0:

        St.dataframe(
            Rooms_df[
                [
                    “room_number”,
                    “room_type”,
                    “floor”,
                    “price”,
                    “status”,
                    “note”
                ]
            ].rename(columns={
                “room_number”: “Phòng”,
                “room_type”: “Loại phòng”,
                “floor”: “Tầng”,
                “price”: “Giá/đêm”,
                “status”: “Trạng thái”,
                “note”: “Ghi chú”
            }),
            Use_container_width=True,
            Hide_index=True
        )

        Room_to_release = st.selectbox(
            “Chọn phòng hoàn tất bảo trì”,
            Rooms_df[“room_number”].tolist()
        )

        If st.button(
            “✅ Hoàn tất bảo trì”,
            Use_container_width=True
        ):

            Update_room_status(
                Room_to_release,
                “Trống”
            )

            Add_history(
                Room_to_release,
                “Hoàn tất bảo trì”
            )

            St.success(
                F”Phòng {room_to_release} đã trở lại trạng thái Trống.”
            )

            St.rerun()

    Else:

        St.success(“ Hiện không có phòng nào đang bảo trì.”)

    St.divider()

    St.subheader(“ Đưa phòng vào bảo trì”)

    Available_rooms = query_df(“””
        SELECT *
        FROM rooms
        WHERE status IN (‘Trống’, ‘Đang dọn’)
        ORDER BY room_number
    “””)

    If len(available_rooms) > 0:

        Room_number = st.selectbox(
            “Chọn phòng”,
            Available_rooms[“room_number”].tolist()
        )

        Maintenance_note = st.text_area(
            “Nội dung bảo trì”,
            Placeholder=”Ví dụ: Máy lạnh không hoạt động...”
        )

        If st.button(
            “ Đưa vào bảo trì”,
            Use_container_width=True
        ):

            Execute_query(“””
                UPDATE rooms
                SET
                    Status = ‘Bảo trì’,
                    Note = ?
                WHERE room_number = ?
            “””, (
                Maintenance_note,
                Room_number
            ))

            Add_history(
                Room_number,
                F”Đưa vào bảo trì: {maintenance_note}”
            )

            St.success(
                F”Phòng {room_number} đã chuyển sang Bảo trì.”
            )

            St.rerun()

    Else:

        St.info(
            “Không có phòng phù hợp để đưa vào bảo trì.”
        )


# =========================================================
# 7. LỊCH SỬ
# =========================================================

Elif menu == “ Lịch sử”:

    St.markdown(
        ‘<div class=”main-title”> Lịch sử hoạt động</div>’,
        Unsafe_allow_html=True
    )

    History_df = query_df(“””
        SELECT
            Id AS ‘Mã’,
            Room_number AS ‘Phòng’,
            Action AS ‘Hoạt động’,
            Guest_name AS ‘Khách hàng’,
            Amount AS ‘Số tiền’,
            Action_time AS ‘Thời gian’
        FROM history
        ORDER BY id DESC
    “””)

    If len(history_df) > 0:

        St.dataframe(
            History_df,
            Use_container_width=True,
            Hide_index=True
        )

        St.divider()

        St.subheader(“ Thống kê hoạt động”)

        Action_count = history_df[“Hoạt động”].value_counts()

        St.bar_chart(action_count)

    Else:

        St.info(“Chưa có lịch sử hoạt động.”)


# =========================================================
# FOOTER
# =========================================================

St.markdown(“””
<div class=”footer”>
     Hotel Room Management System
    <br>
    Web App quản lý phòng khách sạn
    <br>
    Built with Streamlit + SQLite
</div>
“””, unsafe_allow_html=True)
