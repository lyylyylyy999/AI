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

def average_score(scores: list[int]) -> float:
    if not scores:
        raise ValueError("无法计算空列表的平均分")

    return sum(scores) / len(scores)

def max_score(students: list[Student]) -> tuple[float, str]:
    if not students:
        raise ValueError("无法从空列表中查找最高分")

    top_student = max(
        students,
        key=lambda student: float(student["score"]),
    )

    return float(top_student["score"]), top_student["name"]

def pass_score(scores: list[int]) -> tuple[int, float]:
    if not scores:
        return 0, 0.0
    result = sum(score >=60 for score in scores)
    return result, result/len(scores)

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
    scores = []
    for i in range(0,len(students)):
        scores.append(int(students[i]["score"]))
    average = average_score(scores)
    max_sc, max_name = max_score(students)
    passed_count, pass_rate = pass_score(scores)
    major_average = average_major(students)


    print(f"学生人数：{total_student}")
    print(f"平均分：{average:.2f}")
    print(f"最高分：{max_sc:.1f} ({max_name})")
    print(f"及格人数：{passed_count}")
    print(f"及格率：{pass_rate:.2%}")
    print("各专业平均分：")
    for major, score in major_average.items():
        print(f"  {major}: {score:.2f}")


if __name__ == "__main__":
    main()
