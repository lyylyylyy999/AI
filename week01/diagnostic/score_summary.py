import csv
from pathlib import Path

def read_students(path):
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        students = list(reader)
    return students

def total_students(students):
    return len(students)

def average_score(students_score):
    return sum(students_score)/total_students(students_score)

def max_score(students, students_score):
    max_sc = max(students_score)
    for i in range(0, len(students)):
        if int(students[i]["score"]) == max_sc:
            name = students[i]["name"]
    return max_sc, name

def pass_score(students_score):
    pass_students = []
    for i in students_score:
        if i>=60:
            pass_students.append(1)
        else:
            pass_students.append(0)
    return sum(pass_students), sum(pass_students)/len(pass_students)

def average_major(students):
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

# def average_major(students):
#     score = []
#     index = []
#     major = []
#     result = []
#     for i in range(0, len(students)):
#         major.append(students[i]["major"])
#     major = list(dict.fromkeys(major))
#     for i in range(0, len(major)):
#         score.append(0)
#         index.append(0)
#     for i in range(0, len(students)):
#         for j in range(0, len(major)):
#             if students[i]["major"] == major[j]:
#                 score[j] = score[j] + int(students[i]["score"])
#                 index[j] = index[j] + 1
#     for i in range(0, len(score)):
#         result.append(score[i]/index[i])
#     return major, result


def main():
    path = Path(__file__).resolve().parent / "data" / "students.csv"
    students = read_students(path)
    total_student = total_students(students)
    students_score = []
    for i in range(0,len(students)):
        students_score.append(int(students[i]["score"]))
    average = average_score(students_score)
    max_sc, name = max_score(students, students_score)
    pass1,pass_rate = pass_score(students_score)
    major_average = average_major(students)


    print(f"学生人数：{total_student}")
    print(f"平均分：{average:.2f}")
    print(f"最高分：{max_sc:.1f} ({name})")
    print(f"及格人数：{pass1}")
    print(f"及格率：{pass_rate:.2%}")
    print("各专业平均分：")
    for major, score in major_average.items():
        print(f"  {major}: {score:.2f}")


if __name__ == "__main__":
    main()
