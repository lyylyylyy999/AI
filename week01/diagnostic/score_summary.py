import csv
from pathlib import Path

Student = dict[str, str]

def read_students(path: Path) -> list[Student]:
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        students = list(reader)
    return students

def total_students(students: list[Student]) -> int:
    return len(students)

def average_score(students_score: list[int]) -> float:
    if not students_score:
        raise ValueError("无法计算空列表的平均分")

    return sum(students_score) / len(students_score)

def max_score(students: list[Student]) -> tuple[float, str]:
    if not students:
        raise ValueError("无法从空列表中查找最高分")

    top_student = max(
        students,
        key=lambda student: float(student["score"]),
    )

    return float(top_student["score"]), top_student["name"]

def pass_score(students_score: list[int]) -> tuple[int, float]:
    pass_students = []
    for i in students_score:
        if i>=60:
            pass_students.append(1)
        else:
            pass_students.append(0)
    return sum(pass_students), sum(pass_students)/len(pass_students)

def average_major(students: list[Student]) -> dict[str, float]:
    major_stats = {}
    average = {}
    for student in students:
        major = student["major"]
        score = int(student["score"])

        if major not in major_stats:
            major_stats[major] = {"total": 0, "count": 0}

        major_stats[major]["total"] += score
        major_stats[major]["count"] += 1
    for major, stats in major_stats.items():
        average[major] = (stats["total"] / stats["count"])
    return average

def main() -> None:
    path = Path(__file__).resolve().parent / "data" / "students.csv"
    students = read_students(path)
    print(students)
    total_student = total_students(students)
    students_score = []
    for i in range(0,len(students)):
        students_score.append(int(students[i]["score"]))
    average = average_score(students_score)
    max_sc, max_name = max_score(students)
    pass1,pass_rate = pass_score(students_score)
    major_average = average_major(students)


    print(f"学生人数：{total_student}")
    print(f"平均分：{average:.2f}")
    print(f"最高分：{max_sc:.1f} ({max_name})")
    print(f"及格人数：{pass1}")
    print(f"及格率：{pass_rate:.2%}")
    print("各专业平均分：")
    for major, score in major_average.items():
        print(f"  {major}: {score:.2f}")


if __name__ == "__main__":
    main()
