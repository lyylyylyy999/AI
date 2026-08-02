"""学生成绩摘要：诊断题参考实现。"""

import argparse
import csv
import sys
from pathlib import Path


Student = dict[str, str]
DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"


def build_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="读取学生成绩 CSV 并输出统计摘要",
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DATA_FILE,
        help="CSV 文件路径；省略时使用内置样例数据",
    )
    return parser


def read_students(path: Path) -> list[Student]:
    """从 CSV 文件读取学生记录。"""
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def average_score(students: list[Student]) -> float:
    """计算所有学生的平均分。"""
    if not students:
        raise ValueError("无法计算空数据的平均分")

    total = sum(int(student["score"]) for student in students)
    return total / len(students)


def highest_scoring_student(students: list[Student]) -> Student:
    """返回分数最高的学生记录。"""
    if not students:
        raise ValueError("无法从空数据中查找最高分")

    return max(students, key=lambda student: int(student["score"]))


def pass_statistics(
    students: list[Student], passing_score: int = 60
) -> tuple[int, float]:
    """返回及格人数和及格率。"""
    if not students:
        return 0, 0.0

    passed_count = sum(
        int(student["score"]) >= passing_score for student in students
    )
    return passed_count, passed_count / len(students)


def average_scores_by_major(students: list[Student]) -> dict[str, float]:
    """计算每个专业的平均分。"""
    major_stats: dict[str, dict[str, int]] = {}

    for student in students:
        major = student["major"]
        score = int(student["score"])

        if major not in major_stats:
            major_stats[major] = {"total": 0, "count": 0}

        major_stats[major]["total"] += score
        major_stats[major]["count"] += 1

    return {
        major: stats["total"] / stats["count"]
        for major, stats in major_stats.items()
    }


def print_summary(students: list[Student]) -> None:
    """计算并打印学生成绩摘要。"""
    overall_average = average_score(students)
    top_student = highest_scoring_student(students)
    passed_count, passed_rate = pass_statistics(students)
    major_averages = average_scores_by_major(students)

    print(f"学生人数: {len(students)}")
    print(f"平均分: {overall_average:.2f}")
    print(f"最高分: {float(top_student['score']):.1f} ({top_student['name']})")
    print(f"及格人数: {passed_count}")
    print(f"及格率: {passed_rate:.2%}")
    print("各专业平均分:")

    for major, average in major_averages.items():
        print(f"  {major}: {average:.2f}")


def main(argv: list[str] | None = None) -> int:
    """运行命令行应用并返回进程退出码。"""
    args = build_parser().parse_args(argv)

    try:
        students = read_students(args.csv_path)
        print_summary(students)
    except FileNotFoundError:
        print(f"错误：文件不存在：{args.csv_path}", file=sys.stderr)
        return 1
    except (KeyError, ValueError) as error:
        print(f"错误：数据格式不正确：{error}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
