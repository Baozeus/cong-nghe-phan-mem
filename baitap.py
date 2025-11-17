import json
import os
from typing import Dict, Any, Optional

DATA_FILE = "data.json"

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "courses": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def existing_student_numbers(data: Dict[str, Any]) -> set:
    nums = set()
    for u in data.get("users", {}).values():
        if u.get("role") == "student":
            sid = u.get("id")
            if isinstance(sid, str) and sid.startswith("S"):
                try:
                    nums.add(int(sid[1:]))
                except ValueError:
                    pass
    return nums

def get_next_student_id(data: Dict[str, Any]) -> str:
    nums = existing_student_numbers(data)
    n = 1
    while n in nums:
        n += 1
    return f"S{n:03d}"

def ensure_student_ids(data: Dict[str, Any]) -> None:
    nums = existing_student_numbers(data)
    max_n = max(nums) if nums else 0
    for uname, info in data.get("users", {}).items():
        if info.get("role") == "student" and "id" not in info:
            max_n += 1
            info["id"] = f"S{max_n:03d}"
            data["users"][uname] = info

def authenticate(data: Dict[str, Any], username: str, password: str) -> Optional[Dict[str, Any]]:
    u = data["users"].get(username)
    if not u:
        return None
    if u["password"] == password:
        return {"username": username, **u}
    return None

def student_menu(data: Dict[str, Any], username: str):
    while True:
        print("\n--- Student Menu ---")
        print("1. View course grades")
        print("2. Update personal information")
        print("0. Log out")
        choice = input("Choose: ").strip()
        if choice == "1":
            view_student_grades(data, username)
        elif choice == "2":
            update_personal_info(data, username)
            save_data(data)
        elif choice == "0":
            break
        else:
            print("Invalid selection.")

def view_student_grades(data: Dict[str, Any], username: str):
    student = data["users"].get(username, {})
    sid = student.get("id", "")
    print(f"\nGrades of {username} {f'({sid})' if sid else ''}:")
    found = False
    for cid, c in data["courses"].items():
        if username in c.get("students", []):
            found = True
            grade = c.get("grades", {}).get(username, "Not yet")
            print(f"- {cid} : {c['name']} -> grade: {grade}")
    if not found:
        print("You are not enrolled in any courses.")

def update_personal_info(data: Dict[str, Any], username: str):
    info = data["users"][username].get("info", {})
    print("\nUpdate personal information:")
    name = input(f"Name [{info.get('name','')}]: ").strip()
    email = input(f"Email [{info.get('email','')}]: ").strip()
    if name:
        info["name"] = name
    if email:
        info["email"] = email
    data["users"][username]["info"] = info
    print("Updated successfully.")

def instructor_menu(data: Dict[str, Any], username: str):
    while True:
        print("\n--- Instructor Menu ---")
        print("1. View assigned courses")
        print("2. Edit grades for students")
        print("0. Log out")
        choice = input("Choose: ").strip()
        if choice == "1":
            view_instructor_courses(data, username)
        elif choice == "2":
            enter_grades(data, username)
            save_data(data)
        elif choice == "0":
            break
        else:
            print("Invalid selection.")

def view_instructor_courses(data: Dict[str, Any], username: str):
    print(f"\nCourses assigned to {username}:")
    any_course = False
    for cid, c in data["courses"].items():
        if c.get("instructor") == username:
            any_course = True
            students = c.get("students", [])
            print(f"- {cid}: {c['name']} (students: {len(students)})")
    if not any_course:
        print("You are not assigned to any courses.")

def enter_grades(data: Dict[str, Any], username: str):
    courses = {cid: c for cid, c in data["courses"].items() if c.get("instructor") == username}
    if not courses:
        print("You have no courses to grade.")
        return
    print("Choose a course to enter grades:")
    for cid, c in courses.items():
        print(f"- {cid}: {c['name']}")
    cid = input("Course ID: ").strip()
    if cid not in courses:
        print("Invalid course ID.")
        return
    course = data["courses"][cid]
    if not course.get("students"):
        print("No students enrolled in this course.")
        return
    print(f"Students in {cid}:")
    for i, s in enumerate(course["students"], 1):
        current = course.get("grades", {}).get(s, "None")
        info = data["users"].get(s, {}).get("info", {})
        sid = data["users"].get(s, {}).get("id", "")
        print(f"{i}. {s} {f'({sid})' if sid else ''} ({info.get('name','-')}) -> Current grade: {current}")
    while True:
        target = input("Enter student username to grade (or 'q' to quit): ").strip()
        if target.lower() == 'q':
            break
        if target not in course["students"]:
            print("Student not in this class.")
            continue
        raw = input("Enter grade: ").strip()
        try:
            grade = float(raw)
            course.setdefault("grades", {})[target] = grade
            data["courses"][cid] = course
            print("Grade saved.")
        except ValueError:
            print("Invalid grade.")

def admin_menu(data: Dict[str, Any], username: str):
    while True:
        print("\n--- Admin Menu ---")
        print("1. Create new account")
        print("2. Manage students (add/edit/delete)")
        print("3. Manage courses (create/edit/delete/assign instructor/add/remove student)")
        print("4. List all users")
        print("0. Log out")
        choice = input("Choose: ").strip()
        if choice == "1":
            create_account(data)
            save_data(data)
        elif choice == "2":
            manage_students(data)
            save_data(data)
        elif choice == "3":
            manage_courses(data)
            save_data(data)
        elif choice == "4":
            list_users(data)
        elif choice == "0":
            break
        else:
            print("Invalid selection.")

def create_account(data: Dict[str, Any]):
    print("\nCreate new account")
    uname = input("Username: ").strip()
    if not uname:
        print("Username cannot be empty.")
        return
    if uname in data["users"]:
        print("Username already exists.")
        return
    role = input("Role (student/instructor/admin): ").strip().lower()
    if role not in ("student", "instructor", "admin"):
        print("Invalid role.")
        return
    pw = input("Password: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    user_obj = {
        "role": role,
        "password": pw,
        "info": {"name": name, "email": email}
    }
    if role == "student":
        user_obj["id"] = get_next_student_id(data)
    data["users"][uname] = user_obj
    print("Account created successfully.")

def manage_students(data: Dict[str, Any]):
    while True:
        print("\n--- Manage Students ---")
        print("1. Add student")
        print("2. Edit student")
        print("3. Delete student")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            create_account_for_role(data, "student")
        elif c == "2":
            edit_student(data)
        elif c == "3":
            delete_student(data)
        elif c == "0":
            break
        else:
            print("Invalid choice.")

def create_account_for_role(data: Dict[str, Any], role: str):
    print(f"\nCreate {role} account")
    uname = input("Username: ").strip()
    if not uname or uname in data["users"]:
        print("Invalid or existing username.")
        return
    pw = input("Password: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    user_obj = {
        "role": role,
        "password": pw,
        "info": {"name": name, "email": email}
    }
    if role == "student":
        user_obj["id"] = get_next_student_id(data)
    data["users"][uname] = user_obj
    print("Created successfully.")

def edit_student(data: Dict[str, Any]):
    uname = input("Student username to edit: ").strip()
    u = data["users"].get(uname)
    if not u or u.get("role") != "student":
        print("Student not found.")
        return
    print("Leave blank to keep unchanged.")
    name = input(f"Name [{u.get('info',{}).get('name','')}]: ").strip()
    email = input(f"Email [{u.get('info',{}).get('email','')}]: ").strip()
    pw = input("New password (leave blank to keep): ").strip()
    change_id = input(f"Student ID [{u.get('id','')}], leave blank to keep or type new ID: ").strip()
    if name:
        u["info"]["name"] = name
    if email:
        u["info"]["email"] = email
    if pw:
        u["password"] = pw
    if change_id:
        u["id"] = change_id
    data["users"][uname] = u
    print("Student updated successfully.")

def delete_student(data: Dict[str, Any]):
    uname = input("Student username to delete: ").strip()
    u = data["users"].get(uname)
    if not u or u.get("role") != "student":
        print("Student not found.")
        return
    for cid, c in data["courses"].items():
        if uname in c.get("students", []):
            c["students"].remove(uname)
            if "grades" in c and uname in c["grades"]:
                del c["grades"][uname]
    del data["users"][uname]
    print("Student deleted successfully.")

def manage_courses(data: Dict[str, Any]):
    while True:
        print("\n--- Manage Courses ---")
        print("1. Create course")
        print("2. Edit course")
        print("3. Delete course")
        print("4. Assign instructor to course")
        print("5. Add student to course")
        print("6. Remove student from course")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            create_course(data)
        elif c == "2":
            edit_course(data)
        elif c == "3":
            delete_course(data)
        elif c == "4":
            assign_instructor_to_course(data)
        elif c == "5":
            add_student_to_course(data)
        elif c == "6":
            remove_student_from_course(data)
        elif c == "0":
            break
        else:
            print("Invalid selection.")

def create_course(data: Dict[str, Any]):
    cid = input("Course ID (e.g. IT101): ").strip()
    if not cid or cid in data["courses"]:
        print("Invalid or existing course ID.")
        return
    name = input("Course name: ").strip()
    instr = input("Instructor username (leave blank if none): ").strip()
    if instr and (instr not in data["users"] or data["users"][instr]["role"] != "instructor"):
        print("Instructor not valid. Skipping assignment.")
        instr = ""
    data["courses"][cid] = {
        "name": name,
        "instructor": instr,
        "students": [],
        "grades": {}
    }
    print("Course created successfully.")

def edit_course(data: Dict[str, Any]):
    cid = input("Course ID to edit: ").strip()
    course = data["courses"].get(cid)
    if not course:
        print("Course not found.")
        return
    name = input(f"Name [{course['name']}]: ").strip()
    instr = input(f"Instructor [{course.get('instructor','')}]: ").strip()
    if name:
        course["name"] = name
    if instr:
        if instr in data["users"] and data["users"][instr]["role"] == "instructor":
            course["instructor"] = instr
        else:
            print("Invalid instructor, keeping current.")
    data["courses"][cid] = course
    print("Course updated successfully.")

def delete_course(data: Dict[str, Any]):
    cid = input("Course ID to delete: ").strip()
    if cid not in data["courses"]:
        print("Course not found.")
        return
    del data["courses"][cid]
    print("Course deleted successfully.")

def assign_instructor_to_course(data: Dict[str, Any]):
    cid = input("Course ID: ").strip()
    if cid not in data["courses"]:
        print("Course not found.")
        return
    instr = input("Instructor username: ").strip()
    if instr not in data["users"] or data["users"][instr]["role"] != "instructor":
        print("Invalid instructor.")
        return
    data["courses"][cid]["instructor"] = instr
    print("Instructor assigned successfully.")

def add_student_to_course(data: Dict[str, Any]):
    cid = input("Course ID: ").strip()
    if cid not in data["courses"]:
        print("Course not found.")
        return
    uname = input("Student username to add: ").strip()
    if uname not in data["users"] or data["users"][uname]["role"] != "student":
        print("Invalid student.")
        return
    course = data["courses"][cid]
    if uname in course.get("students", []):
        print("Student already in class.")
        return
    course.setdefault("students", []).append(uname)
    print("Student added successfully.")

def remove_student_from_course(data: Dict[str, Any]):
    cid = input("Course ID: ").strip()
    if cid not in data["courses"]:
        print("Course not found.")
        return
    uname = input("Student username to remove: ").strip()
    course = data["courses"][cid]
    if uname not in course.get("students", []):
        print("Student not in this course.")
        return
    course["students"].remove(uname)
    if "grades" in course and uname in course["grades"]:
        del course["grades"][uname]
    print("Student removed successfully.")

def list_users(data: Dict[str, Any]):
    print("\nUsers list:")
    for uname, u in data["users"].items():
        role = u.get("role", "")
        name = u.get("info", {}).get("name", "")
        sid = u.get("id", "")
        print(f"- {uname} ({role}) - {name}{f' - {sid}' if sid else ''}")

def main():
    data = load_data()
    ensure_student_ids(data)
    save_data(data)

    print("=== Student Management System ===")
    while True:
        print("\n1. Log in")
        print("2. Exit")
        c = input("Choose: ").strip()
        if c == "1":
            uname = input("Username: ").strip()
            pw = input("Password: ").strip()
            user = authenticate(data, uname, pw)
            if not user:
                print("Invalid username or password.")
                continue
            role = user["role"]
            print(f"Logged in as: {role}")
            if role == "student":
                student_menu(data, uname)
            elif role == "instructor":
                instructor_menu(data, uname)
            elif role == "admin":
                admin_menu(data, uname)
            else:
                print("Invalid role.")
            save_data(data)
        elif c == "2":
            print("Goodbye.")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
