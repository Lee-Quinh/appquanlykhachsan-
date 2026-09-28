import os
from datetime import datetime, date, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
st.image("IMG_20260928_114620.jpg")
# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG WEB STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống Quản Lý Khách Sạn (Hotel PMS)",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_BOOKING = "booking_history.csv"
CSV_ROOMS = "rooms_master.csv"
CSV_GUESTS = "guests_master.csv"
CSV_NOTICES = "internal_notices.csv"

# ---------------------------------------------------------
# 2. KHỞI TẠO DỮ LIỆU BỘ NHỚ (SESSION STATE & CSV)
# ---------------------------------------------------------
def init_data():
    # Danh mục phòng mặc định
    if "df_rooms" not in st.session_state:
        if os.path.exists(CSV_ROOMS):
            st.session_state.df_rooms = pd.read_csv(CSV_ROOMS)
        else:
            default_rooms = [
                {"Phòng": "101", "Hạng": "Đơn Thường", "Giá": 300000, "Trạng thái": "Trống - Sạch", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
                {"Phòng": "102", "Hạng": "Đơn Thường", "Giá": 300000, "Trạng thái": "Trống - Sạch", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
                {"Phòng": "201", "Hạng": "Đôi Thường", "Giá": 450000, "Trạng thái": "Cần dọn (Dirty)", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
                {"Phòng": "202", "Hạng": "Đôi Thường", "Giá": 450000, "Trạng thái": "Đang ở", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
                {"Phòng": "301", "Hạng": "VIP Đơn", "Giá": 600000, "Trạng thái": "Khóa bảo trì", "Bảo trì": True, "Lỗi bảo trì": "Hư hỏng máy lạnh", "Ghi chú": ""},
                {"Phòng": "302", "Hạng": "VIP Đôi", "Giá": 800000, "Trạng thái": "Đã kiểm tra (Inspected)", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
                {"Phòng": "401", "Hạng": "President", "Giá": 1500000, "Trạng thái": "Trống - Sạch", "Bảo trì": False, "Lỗi bảo trì": "", "Ghi chú": ""},
            ]
            st.session_state.df_rooms = pd.DataFrame(default_rooms)

    # Lịch sử đặt phòng & Check-in
    if "df_bookings" not in st.session_state:
        if os.path.exists(CSV_BOOKING):
            st.session_state.df_bookings = pd.read_csv(CSV_BOOKING)
        else:
            default_bookings = [
                {
                    "Mã Đặt": "BK001", "Khách hàng": "Nguyễn Văn Anh", "CCCD/Passport": "0123456789",
                    "SĐT": "0901234567", "Loại khách": "VIP", "Phòng": "202", "Nguồn đặt": "Booking.com",
                    "Ngày Check-in": "2026-09-28", "Ngày Check-out": "2026-09-30", "Số đêm": 2,
                    "Tiền phòng": 900000, "Tiền Dịch vụ": 150000, "Tiền Cọc": 300000, "Tổng cộng": 1050000,
                    "Trạng thái BK": "Đang ở", "PT Thanh toán": "Chuyển khoản", "Ghi chú khách": "Gối lông vũ, tầng cao"
                }
            ]
            st.session_state.df_bookings = pd.DataFrame(default_bookings)

    # Hồ sơ khách hàng
    if "df_guests" not in st.session_state:
        if os.path.exists(CSV_GUESTS):
            st.session_state.df_guests = pd.read_csv(CSV_GUESTS)
        else:
            default_guests = [
                {"CCCD/Passport": "0123456789", "Tên": "Nguyễn Văn Anh", "SĐT": "0901234567", "Loại khách": "VIP", "Sở thích/Yêu cầu": "Gối lông vũ, phòng yên tĩnh", "Số lần lưu trú": 3}
            ]
            st.session_state.df_guests = pd.DataFrame(default_guests)

    # Thông báo nội bộ
    if "df_notices" not in st.session_state:
        if os.path.exists(CSV_NOTICES):
            st.session_state.df_notices = pd.read_csv(CSV_NOTICES)
        else:
            st.session_state.df_notices = pd.DataFrame(columns=["Thời gian", "Từ bộ phận", "Đến bộ phận", "Nội dung", "Đã xử lý"])

init_data()

def save_all_data():
    st.session_state.df_rooms.to_csv(CSV_ROOMS, index=False)
    st.session_state.df_bookings.to_csv(CSV_BOOKING, index=False)
    st.session_state.df_guests.to_csv(CSV_GUESTS, index=False)
    st.session_state.df_notices.to_csv(CSV_NOTICES, index=False)

# ---------------------------------------------------------
# 3. SIDEBAR & ĐĂNG NHẬP PHÂN QUYỀN (ROLES)
# ---------------------------------------------------------
st.sidebar.title("🏨 HOTEL PMS SYSTEM")
role = st.sidebar.selectbox("👤 Vai trò làm việc:", ["Lễ Tân (Front Office)", "Buồng Phòng (Housekeeping)", "Bảo Trì (Engineering)", "Quản Lý (Manager / Admin)"])

page = st.sidebar.radio(
    "📍 Điều hướng chức năng:",
    [
        "1. Sơ Đồ & Quản Lý Phòng",
        "2. Đặt Phòng & OTA",
        "3. Check-in / Check-out & Thanh Toán",
        "4. Quản Lý Khách Hàng",
        "5. Buồng Phòng (Housekeeping)",
        "6. Quản Lý Bảo Trì",
        "7. Báo Cáo & Thống Kê KPI",
        "8. Thông Báo Nội Bộ"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Đang làm việc:** {role}\n\n📅 Ngày hệ thống: {date.today().strftime('%d/%m/%Y')}")

# ---------------------------------------------------------
# MODULE 1: SƠ ĐỒ & QUẢN LÝ PHÒNG
# ---------------------------------------------------------
if page == "1. Sơ Đồ & Quản Lý Phòng":
    st.title("🛏️ Sơ Đồ Phòng Realtime & Quản Lý Trạng Thái")

    df_r = st.session_state.df_rooms

    # Thống kê nhanh trạng thái
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🟢 Trống - Sạch", len(df_r[df_r["Trạng thái"] == "Trống - Sạch"]))
    c2.metric("🔴 Đang có khách", len(df_r[df_r["Trạng thái"] == "Đang ở"]))
    c3.metric("🧹 Cần dọn (Dirty)", len(df_r[df_r["Trạng thái"] == "Cần dọn (Dirty)"]))
    c4.metric("✨ Đã kiểm tra", len(df_r[df_r["Trạng thái"] == "Đã kiểm tra (Inspected)"]))
    c5.metric("🛠️ Khóa bảo trì", len(df_r[df_r["Bảo trì"] == True]))

    st.markdown("---")
    st.subheader("📌 Sơ đồ các phòng khách sạn")

    cols = st.columns(4)
    for idx, row in df_r.iterrows():
        with cols[idx % 4]:
            bg_color = "#d4edda" if row["Trạng thái"] == "Trống - Sạch" else (
                "#f8d7da" if row["Trạng thái"] == "Cần dọn (Dirty)" else (
                    "#cce5ff" if row["Trạng thái"] == "Đang ở" else (
                        "#fff3cd" if row["Trạng thái"] == "Đã kiểm tra (Inspected)" else "#e2e3e5"
                    )
                )
            )
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ccc;">
                <h4>Phòng {row['Phòng']} ({row['Hạng']})</h4>
                <p><b>Trạng thái:</b> {row['Trạng thái']}</p>
                <p><b>Giá:</b> {row['Giá']:,} VNĐ/đêm</p>
                <p><b>Bảo trì:</b> {'🔴 Đang khóa' if row['Bảo trì'] else '🟢 Bình thường'}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔄 Chuyển phòng cho khách")
        room_from = st.selectbox("Từ phòng (đang ở):", df_r[df_r["Trạng thái"] == "Đang ở"]["Phòng"].tolist())
        room_to = st.selectbox("Chuyển sang phòng trống:", df_r[df_r["Trạng thái"] == "Trống - Sạch"]["Phòng"].tolist())
        reason = st.text_input("Lý do chuyển phòng:")

        if st.button("Xác nhận chuyển phòng"):
            if room_from and room_to:
                # Cập nhật trạng thái
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == room_from, "Trạng thái"] = "Cần dọn (Dirty)"
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == room_to, "Trạng thái"] = "Đang ở"

                # Cập nhật lịch sử đặt phòng
                st.session_state.df_bookings.loc[
                    (st.session_state.df_bookings["Phòng"] == room_from) & (st.session_state.df_bookings["Trạng thái BK"] == "Đang ở"), "Phòng"
                ] = room_to

                save_all_data()
                st.success(f"Đã chuyển khách từ phòng {room_from} sang phòng {room_to}!")
                st.rerun()

    with col_right:
        st.subheader("⚙️ Cập nhật thông tin / Giá phòng")
        selected_r = st.selectbox("Chọn phòng điều chỉnh:", df_r["Phòng"].tolist())
        r_info = df_r[df_r["Phòng"] == selected_r].iloc[0]
        new_price = st.number_input("Giá phòng mới (VNĐ):", value=int(r_info["Giá"]), step=50000)
        new_status = st.selectbox("Trạng thái phòng:", ["Trống - Sạch", "Cần dọn (Dirty)", "Đang dọn (Cleaning)", "Đã kiểm tra (Inspected)", "Đang ở"], index=0)

        if st.button("Lưu thay đổi thông tin"):
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == selected_r, "Giá"] = new_price
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == selected_r, "Trạng thái"] = new_status
            save_all_data()
            st.success("Đã cập nhật thông tin phòng thành công!")
            st.rerun()

# ---------------------------------------------------------
# MODULE 2: ĐẶT PHÒNG & QUẢN LÝ OTA
# ---------------------------------------------------------
elif page == "2. Đặt Phòng & OTA":
    st.title("📅 Quản Lý Đặt Phòng & Đồng Bộ OTA")

    tab_create, tab_list = st.tabs(["➕ Tạo Booking Mới / Đồng bộ OTA", "📋 Danh Sách Booking"])

    with tab_create:
        col1, col2 = st.columns(2)
        with col1:
            guest_name = st.text_input("Tên khách hàng:")
            guest_id = st.text_input("Số CCCD / Passport:")
            guest_phone = st.text_input("Số điện thoại:")
            guest_type = st.selectbox("Phân loại khách:", ["Khách lẻ", "Khách quen", "Đoàn", "VIP"])
            source = st.selectbox("Nguồn đặt phòng (Channel):", ["Trực tiếp / Hotline", "Booking.com", "Agoda", "Traveloka", "Expedia"])

        with col2:
            available_rooms = st.session_state.df_rooms[st.session_state.df_rooms["Bảo trì"] == False]["Phòng"].tolist()
            room_sel = st.selectbox("Chọn phòng khả dụng:", available_rooms)
            cin = st.date_input("Ngày Check-in:", date.today())
            cout = st.date_input("Ngày Check-out:", date.today() + timedelta(days=1))
            deposit = st.number_input("Đặt cọc trước (VNĐ):", min_value=0, step=100000)
            notes = st.text_area("Yêu cầu đặc biệt / Ghi chú:")

        if st.button("💾 Xác Nhận Tạo Booking"):
            if guest_name and room_sel:
                num_nights = (cout - cin).days
                if num_nights <= 0:
                    st.error("Ngày check-out phải sau ngày check-in!")
                else:
                    room_price = st.session_state.df_rooms[st.session_state.df_rooms["Phòng"] == room_sel]["Giá"].values[0]
                    room_total = room_price * num_nights
                    bk_code = f"BK{len(st.session_state.df_bookings)+1:03d}"

                    new_bk = {
                        "Mã Đặt": bk_code, "Khách hàng": guest_name, "CCCD/Passport": guest_id,
                        "SĐT": guest_phone, "Loại khách": guest_type, "Phòng": room_sel, "Nguồn đặt": source,
                        "Ngày Check-in": str(cin), "Ngày Check-out": str(cout), "Số đêm": num_nights,
                        "Tiền phòng": room_total, "Tiền Dịch vụ": 0, "Tiền Cọc": deposit, "Tổng cộng": room_total,
                        "Trạng thái BK": "Đã xác nhận", "PT Thanh toán": "Chưa thanh toán", "Ghi chú khách": notes
                    }
                    st.session_state.df_bookings = pd.concat([st.session_state.df_bookings, pd.DataFrame([new_bk])], ignore_index=True)

                    # Lưu hồ sơ khách
                    if guest_id not in st.session_state.df_guests["CCCD/Passport"].values:
                        new_g = {"CCCD/Passport": guest_id, "Tên": guest_name, "SĐT": guest_phone, "Loại khách": guest_type, "Sở thích/Yêu cầu": notes, "Số lần lưu trú": 1}
                        st.session_state.df_guests = pd.concat([st.session_state.df_guests, pd.DataFrame([new_g])], ignore_index=True)

                    save_all_data()
                    st.success(f"Tạo thành công mã đặt phòng {bk_code}!")
                    st.rerun()

    with tab_list:
        st.dataframe(st.session_state.df_bookings, use_container_width=True)

# ---------------------------------------------------------
# MODULE 3: CHECK-IN / CHECK-OUT & THANH TOÁN
# ---------------------------------------------------------
elif page == "3. Check-in / Check-out & Thanh Toán":
    st.title("🗝️ Thủ Tục Check-in / Check-out & Hóa Đơn")

    tab_in, tab_out = st.tabs(["🔑 Check-in (Nhận Phòng)", "💳 Check-out & Thanh Toán"])

    with tab_in:
        st.subheader("Danh sách Booking chờ Check-in hôm nay")
        pending_bk = st.session_state.df_bookings[st.session_state.df_bookings["Trạng thái BK"] == "Đã xác nhận"]

        if not pending_bk.empty:
            st.dataframe(pending_bk[["Mã Đặt", "Khách hàng", "Phòng", "Ngày Check-in", "Nguồn đặt"]], use_container_width=True)
            selected_bk = st.selectbox("Chọn Mã Đặt để Check-in:", pending_bk["Mã Đặt"].tolist())

            if st.button("🚀 Thực Hiện Check-in"):
                bk_row = pending_bk[pending_bk["Mã Đặt"] == selected_bk].iloc[0]
                room_num = bk_row["Phòng"]

                # Kiểm tra phòng có đang bị khóa bảo trì không
                is_maint = st.session_state.df_rooms[st.session_state.df_rooms["Phòng"] == room_num]["Bảo trì"].values[0]
                if is_maint:
                    st.error(f"Phòng {room_num} đang bị KHÓA BẢO TRÌ! Vui lòng đổi phòng cho khách trước khi check-in.")
                else:
                    st.session_state.df_bookings.loc[st.session_state.df_bookings["Mã Đặt"] == selected_bk, "Trạng thái BK"] = "Đang ở"
                    st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == room_num, "Trạng thái"] = "Đang ở"
                    save_all_data()
                    st.success(f"Check-in thành công cho khách {bk_row['Khách hàng']} - Phòng {room_num}!")
                    st.rerun()
        else:
            st.info("Không có booking nào đang chờ check-in.")

    with tab_out:
        st.subheader("Danh sách khách đang lưu trú")
        active_bk = st.session_state.df_bookings[st.session_state.df_bookings["Trạng thái BK"] == "Đang ở"]

        if not active_bk.empty:
            selected_out_bk = st.selectbox("Chọn Booking làm thủ tục Check-out:", active_bk["Mã Đặt"].tolist())
            bk_data = active_bk[active_bk["Mã Đặt"] == selected_out_bk].iloc[0]

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Khách hàng:** {bk_data['Khách hàng']}")
                st.write(f"**Phòng:** {bk_data['Phòng']}")
                st.write(f"**Tiền phòng:** {bk_data['Tiền phòng']:,} VNĐ")
                st.write(f"**Tiền đặt cọc:** {bk_data['Tiền Cọc']:,} VNĐ")

            with col_b:
                st.subheader("Thêm Phụ Phí Dịch Vụ (Minibar, F&B, Spa...)")
                service_fee = st.number_input("Tiền dịch vụ phát sinh (VNĐ):", min_value=0, step=10000, value=int(bk_data['Tiền Dịch vụ']))
                pay_method = st.selectbox("Phương thức thanh toán:", ["Tiền mặt", "Thẻ ngân hàng", "Chuyển khoản QR"])

            # Tính toán tổng thực thanh toán
            total_bill = (bk_data['Tiền phòng'] + service_fee) - bk_data['Tiền Cọc']
            st.markdown(f"### 💰 **CÒN PHẢI THANH TOÁN: {total_bill:,.0f} VNĐ**")

            if st.button("🧾 Hoàn Tất Check-out & In Hóa Đơn"):
                room_num = bk_data["Phòng"]

                # Cập nhật trạng thái
                st.session_state.df_bookings.loc[st.session_state.df_bookings["Mã Đặt"] == selected_out_bk, "Tiền Dịch vụ"] = service_fee
                st.session_state.df_bookings.loc[st.session_state.df_bookings["Mã Đặt"] == selected_out_bk, "Tổng cộng"] = bk_data['Tiền phòng'] + service_fee
                st.session_state.df_bookings.loc[st.session_state.df_bookings["Mã Đặt"] == selected_out_bk, "Trạng thái BK"] = "Đã Check-out"
                st.session_state.df_bookings.loc[st.session_state.df_bookings["Mã Đặt"] == selected_out_bk, "PT Thanh toán"] = pay_method

                # Chuyển trạng thái phòng sang Cần dọn (Dirty) cho Housekeeping
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == room_num, "Trạng thái"] = "Cần dọn (Dirty)"

                save_all_data()
                st.success(f"Đã Check-out thành công cho phòng {room_num}. Phòng đã tự động chuyển sang trạng thái Cần dọn (Dirty)!")
                st.rerun()
        else:
            st.info("Hiện không có phòng nào đang ở cần check-out.")

# ---------------------------------------------------------
# MODULE 4: QUẢN LÝ KHÁCH HÀNG
# ---------------------------------------------------------
elif page == "4. Quản Lý Khách Hàng":
    st.title("👤 Quản Lý Hồ Sơ Khách Hàng & Lịch Sử Lưu Trú")

    df_g = st.session_state.df_guests
    st.dataframe(df_g, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Tra cứu & Cập nhật sở thích khách hàng")
    selected_guest_id = st.selectbox("Chọn khách hàng (theo CCCD/Passport):", df_g["CCCD/Passport"].tolist())

    if selected_guest_id:
        g_data = df_g[df_g["CCCD/Passport"] == selected_guest_id].iloc[0]
        new_pref = st.text_area("Cập nhật Sở thích / Yêu cầu đặc biệt:", value=str(g_data["Sở thích/Yêu cầu"]))
        new_type = st.selectbox("Hạng khách hàng:", ["Khách lẻ", "Khách quen", "Đoàn", "VIP"], index=["Khách lẻ", "Khách quen", "Đoàn", "VIP"].index(g_data["Loại khách"]))

        if st.button("Lưu Hồ Sơ Khách Hàng"):
            st.session_state.df_guests.loc[st.session_state.df_guests["CCCD/Passport"] == selected_guest_id, "Sở thích/Yêu cầu"] = new_pref
            st.session_state.df_guests.loc[st.session_state.df_guests["CCCD/Passport"] == selected_guest_id, "Loại khách"] = new_type
            save_all_data()
            st.success("Đã cập nhật thông tin hồ sơ khách hàng thành công!")
            st.rerun()

# ---------------------------------------------------------
# MODULE 5: BUỒNG PHÒNG (HOUSEKEEPING)
# ---------------------------------------------------------
elif page == "5. Buồng Phòng (Housekeeping)":
    st.title("🧹 Phân Hệ Buồng Phòng (Housekeeping)")

    df_r = st.session_state.df_rooms
    st.subheader("📌 Tình trạng vệ sinh buồng phòng")

    def highlight_clean(val):
        color_map = {
            "Trống - Sạch": "background-color: #d4edda; color: #155724;",
            "Cần dọn (Dirty)": "background-color: #f8d7da; color: #721c24;",
            "Đang dọn (Cleaning)": "background-color: #fff3cd; color: #856404;",
            "Đã kiểm tra (Inspected)": "background-color: #d1ecf1; color: #0c5460;",
            "Đang ở": "background-color: #cce5ff; color: #004085;"
        }
        return color_map.get(val, "")

    st.dataframe(df_r[["Phòng", "Hạng", "Trạng thái", "Bảo trì", "Ghi chú"]].style.map(highlight_clean, subset=["Trạng thái"]), use_container_width=True)

    st.markdown("---")
    st.subheader("🔄 Cập nhật tình trạng dọn phòng (Cập nhật trực tiếp cho FO)")

    col_hk1, col_hk2 = st.columns(2)
    with col_hk1:
        hk_room = st.selectbox("Chọn phòng xử lý:", df_r["Phòng"].tolist())
        hk_status = st.selectbox("Trạng thái vệ sinh mới:", ["Trống - Sạch", "Đang dọn (Cleaning)", "Đã kiểm tra (Inspected)", "Cần dọn (Dirty)"])
        hk_note = st.text_input("Ghi chú vệ sinh / Đồ đạc thất lạc:")

    with col_hk2:
        if st.button("💾 Cập nhật & Báo cho Lễ Tân (FO)"):
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == hk_room, "Trạng thái"] = hk_status
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == hk_room, "Ghi chú"] = hk_note

            # Gửi thông báo nội bộ
            new_not = {
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Từ bộ phận": "Housekeeping", "Đến bộ phận": "Front Office",
                "Nội dung": f"Phòng {hk_room} đã chuyển trạng thái thành: {hk_status}", "Đã xử lý": False
            }
            st.session_state.df_notices = pd.concat([st.session_state.df_notices, pd.DataFrame([new_not])], ignore_index=True)

            save_all_data()
            st.success(f"Đã cập nhật trạng thái phòng {hk_room} và gửi thông báo tới Lễ Tân!")
            st.rerun()

# ---------------------------------------------------------
# MODULE 6: QUẢN LÝ BẢO TRÌ (ENGINEERING)
# ---------------------------------------------------------
elif page == "6. Quản Lý Bảo Trì":
    st.title("🛠️ Quản Lý Bảo Trì & Sự Cố Phòng (Out of Order)")

    df_r = st.session_state.df_rooms

    col_maint1, col_maint2 = st.columns(2)

    with col_maint1:
        st.subheader("🚨 Báo sự cố & Khóa phòng khỏi hệ thống bán")
        maint_room = st.selectbox("Chọn phòng sự cố:", df_r["Phòng"].tolist())
        error_desc = st.selectbox("Thiết bị sự cố:", ["Hư hỏng máy lạnh", "Lỗi TV/Wifi", "Hệ thống nước nóng", "Điện/Bóng đèn", "Khác"])
        error_detail = st.text_area("Chi tiết lỗi hư hỏng:")

        if st.button("🔒 Khóa Phòng & Báo Bảo Trì"):
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == maint_room, "Bảo trì"] = True
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == maint_room, "Trạng thái"] = "Khóa bảo trì"
            st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == maint_room, "Lỗi bảo trì"] = f"{error_desc}: {error_detail}"

            save_all_data()
            st.warning(f"Đã KHÓA phòng {maint_room} thành công! Lễ tân sẽ không thể gắn phòng này cho khách.")
            st.rerun()

    with col_maint2:
        st.subheader("✅ Mở khóa phòng (Đã sửa chữa xong)")
        locked_rooms = df_r[df_r["Bảo trì"] == True]["Phòng"].tolist()

        if locked_rooms:
            unlock_room = st.selectbox("Chọn phòng đã sửa xong:", locked_rooms)
            if st.button("🔓 Sửa xong & Mở bán lại phòng"):
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == unlock_room, "Bảo trì"] = False
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == unlock_room, "Trạng thái"] = "Cần dọn (Dirty)"
                st.session_state.df_rooms.loc[st.session_state.df_rooms["Phòng"] == unlock_room, "Lỗi bảo trì"] = ""

                save_all_data()
                st.success(f"Đã mở khóa phòng {unlock_room}! Phòng chuyển sang trạng thái Cần dọn để HK kiểm tra.")
                st.rerun()
        else:
            st.info("Hiện không có phòng nào bị khóa bảo trì.")

# ---------------------------------------------------------
# MODULE 7: BÁO CÁO & THỐNG KÊ KPI
# ---------------------------------------------------------
elif page == "7. Báo Cáo & Thống Kê KPI":
    st.title("📊 Báo Cáo Doanh Thu & Thống Kê Chỉ Số KPI Khách Sạn")

    if role != "Quản Lý (Manager / Admin)":
        st.warning("⚠️ Chỉ tài khoản Quản Lý (Manager / Admin) mới có quyền truy cập báo cáo doanh thu chi tiết.")
    else:
        df_bk = st.session_state.df_bookings
        df_r = st.session_state.df_rooms

        # Tính toán các chỉ số KPI chuẩn quản lý khách sạn
        total_rooms = len(df_r)
        occupied_rooms = len(df_r[df_r["Trạng thái"] == "Đang ở"])
        occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0

        completed_bk = df_bk[df_bk["Trạng thái BK"] != "Đã hủy"]
        total_revenue = completed_bk["Tổng cộng"].sum() if not completed_bk.empty else 0
        total_nights = completed_bk["Số đêm"].sum() if not completed_bk.empty else 0

        adr = (total_revenue / total_nights) if total_nights > 0 else 0
        revpar = (total_revenue / total_rooms) if total_rooms > 0 else 0

        # Hiển thị Metric KPI
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Công suất phòng (Occupancy)", f"{occupancy_rate:.1f}%")
        kpi2.metric("Tổng doanh thu", f"{total_revenue:,.0f} VNĐ")
        kpi3.metric("ADR (Giá TB / Đêm)", f"{adr:,.0f} VNĐ")
        kpi4.metric("RevPAR (Doanh thu / Phòng sẵn có)", f"{revpar:,.0f} VNĐ")

        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("📈 Doanh thu theo nguồn đặt (Channel)")
            if not completed_bk.empty:
                fig_source = px.pie(completed_bk, names="Nguồn đặt", values="Tổng cộng", hole=0.4, title="Tỷ trọng doanh thu theo OTA")
                st.plotly_chart(fig_source, use_container_width=True)

        with col_chart2:
            st.subheader("📊 Tỷ lệ trạng thái phòng hiện tại")
            fig_status = px.bar(df_r, x="Phòng", y="Giá", color="Trạng thái", title="Giá & Trạng thái từng phòng")
            st.plotly_chart(fig_status, use_container_width=True)

# ---------------------------------------------------------
# MODULE 8: THÔNG BÁO NỘI BỘ
# ---------------------------------------------------------
elif page == "8. Thông Báo Nội Bộ":
    st.title("📢 Phối Hợp & Thông Báo Nội Bộ")

    col_n1, col_n2 = st.columns([1, 1.5])

    with col_n1:
        st.subheader("✉️ Gửi thông báo mới")
        to_dept = st.selectbox("Gửi tới bộ phận:", ["Front Office", "Housekeeping", "Engineering", "Toàn bộ"])
        not_content = st.text_area("Nội dung ghi chú / Yêu cầu:")

        if st.button("Gửi Thông Báo"):
            new_note = {
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Từ bộ phận": role,
                "Đến bộ phận": to_dept,
                "Nội dung": not_content,
                "Đã xử lý": False
            }
            st.session_state.df_notices = pd.concat([st.session_state.df_notices, pd.DataFrame([new_note])], ignore_index=True)
            save_all_data()
            st.success("Đã gửi thông báo nội bộ!")
            st.rerun()

    with col_n2:
        st.subheader("📋 Nhật ký thông báo nội bộ")
        st.dataframe(st.session_state.df_notices, use_container_width=True)
