#!/usr/bin/env python3
"""
students.py
Nhập và quản lý thông tin sinh viên đơn giản trên terminal.
Chức năng:
 - Thêm sinh viên (Mã, Họ tên, Ngày sinh, Lớp, Điểm trung bình)
 - Hiển thị tất cả sinh viên
 - Tìm sinh viên theo mã
 - Sửa / Xóa sinh viên
 - Lưu / Tải dữ liệu ra/vào file CSV
"""

import csv
from datetime import datetime
from typing import List, Dict, Optional

students: List[Dict[str, str]] = []

CSV_FIELDS = ["id", "name", "dob", "class", "gpa"]


def input_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Không được để trống. Hãy thử lại.")


def input_date(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        try:
            # cho phép định dạng ngày: YYYY-MM-DD hoặc DD/MM/YYYY
            if "-" in s:
                d = datetime.strptime(s, "%Y-%m-%d")
            else:
                d = datetime.strptime(s, "%d/%m/%Y")
            return d.strftime("%Y-%m-%d")
        except Exception:
            print("Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD hoặc DD/MM/YYYY.")


def input_gpa(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        try:
            g = float(s)
            if 0 <= g <= 10:  # hỗ trợ thang 10; nếu cần 4.0 hãy chỉnh lại
                return f"{g:.2f}"
            else:
                print("Điểm phải nằm trong khoảng 0 - 10.")
        except Exception:
            print("Hãy nhập số hợp lệ cho điểm trung bình.")


def find_student_index(student_id: str) -> Optional[int]:
    for i, st in enumerate(students):
        if st["id"] == student_id:
            return i
    return None


def add_student():
    print("\n--- Thêm sinh viên mới ---")
    sid = input_nonempty("Mã sinh viên: ")
    if find_student_index(sid) is not None:
        print("Mã này đã tồn tại. Hủy bỏ thao tác.")
        return
    name = input_nonempty("Họ tên: ")
    dob = input_date("Ngày sinh (YYYY-MM-DD hoặc DD/MM/YYYY): ")
    cls = input_nonempty("Lớp: ")
    gpa = input_gpa("Điểm trung bình (0-10): ")
    students.append({"id": sid, "name": name, "dob": dob, "class": cls, "gpa": gpa})
    print("Thêm thành công.")


def show_students():
    print("\n--- Danh sách sinh viên ---")
    if not students:
        print("Chưa có sinh viên nào.")
        return
    # in bảng đơn giản
    print(f"{'ID':<12}{'Họ tên':<30}{'Ngày sinh':<12}{'Lớp':<10}{'GPA':<6}")
    print("-" * 70)
    for st in students:
        print(f"{st['id']:<12}{st['name']:<30}{st['dob']:<12}{st['class']:<10}{st['gpa']:<6}")


def find_student():
    sid = input_nonempty("Nhập mã sinh viên cần tìm: ")
    idx = find_student_index(sid)
    if idx is None:
        print("Không tìm thấy sinh viên.")
    else:
        st = students[idx]
        print("Tìm thấy:")
        for k, v in st.items():
            print(f" - {k}: {v}")


def edit_student():
    sid = input_nonempty("Nhập mã sinh viên cần sửa: ")
    idx = find_student_index(sid)
    if idx is None:
        print("Không tìm thấy sinh viên.")
        return
    st = students[idx]
    print("Để trống và nhấn Enter nếu không muốn thay đổi trường đó.")
    new_name = input(f"Họ tên [{st['name']}]: ").strip()
    new_dob = input(f"Ngày sinh [{st['dob']}]: ").strip()
    new_class = input(f"Lớp [{st['class']}]: ").strip()
    new_gpa = input(f"GPA [{st['gpa']}]: ").strip()
    if new_name:
        st['name'] = new_name
    if new_dob:
        try:
            # chuẩn hoá
            if '-' in new_dob:
                d = datetime.strptime(new_dob, "%Y-%m-%d")
            else:
                d = datetime.strptime(new_dob, "%d/%m/%Y")
            st['dob'] = d.strftime("%Y-%m-%d")
        except Exception:
            print("Ngày nhập không hợp lệ — giữ nguyên ngày cũ.")
    if new_class:
        st['class'] = new_class
    if new_gpa:
        try:
            g = float(new_gpa)
            if 0 <= g <= 10:
                st['gpa'] = f"{g:.2f}"
            else:
                print("GPA không hợp lệ — giữ nguyên.")
        except Exception:
            print("GPA không hợp lệ — giữ nguyên.")
    print("Cập nhật xong.")


def delete_student():
    sid = input_nonempty("Nhập mã sinh viên cần xóa: ")
    idx = find_student_index(sid)
    if idx is None:
        print("Không tìm thấy sinh viên.")
        return
    confirm = input(f"Xác nhận xóa sinh viên {students[idx]['name']}? (y/n): ").strip().lower()
    if confirm == 'y':
        students.pop(idx)
        print("Đã xóa.")
    else:
        print("Hủy xóa.")


def save_csv(filename: str):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for st in students:
                writer.writerow(st)
        print(f"Lưu dữ liệu vào {filename} thành công.")
    except Exception as e:
        print("Lưu thất bại:", e)


def load_csv(filename: str):
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            loaded = list(reader)
            # basic validation
            for row in loaded:
                if all(k in row for k in CSV_FIELDS):
                    students.append({k: row[k] for k in CSV_FIELDS})
        print(f"Đã tải dữ liệu từ {filename}. Tổng sinh viên hiện có: {len(students)}")
    except FileNotFoundError:
        print("Không tìm thấy file.")
    except Exception as e:
        print("Tải thất bại:", e)


def main_menu():
    while True:
        print("\n=== QUẢN LÝ SINH VIÊN ===")
        print("1. Thêm sinh viên")
        print("2. Hiển thị danh sách")
        print("3. Tìm sinh viên")
        print("4. Sửa sinh viên")
        print("5. Xóa sinh viên")
        print("6. Lưu ra CSV")
        print("7. Tải từ CSV")
        print("0. Thoát")
        choice = input("Chọn (0-7): ").strip()
        if choice == '1':
            add_student()
        elif choice == '2':
            show_students()
        elif choice == '3':
            find_student()
        elif choice == '4':
            edit_student()
        elif choice == '5':
            delete_student()
        elif choice == '6':
            fname = input_nonempty("Tên file lưu (ví dụ students.csv): ")
            save_csv(fname)
        elif choice == '7':
            fname = input_nonempty("Tên file tải (ví dụ students.csv): ")
            load_csv(fname)
        elif choice == '0':
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == '__main__':
    main_menu()
