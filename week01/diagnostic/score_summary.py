import argparse
import csv
import sys
from pathlib import Path

Student = dict[str, str]
DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="读取学生成绩 CSV 并输出统计摘要",
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="CSV 文件路径；省略时使用内置样例数据",
    )
    parser.add_argument(
        "--passing-score",
        type=int,
        default=60,
        help="及格分数线（默认：60）",
    )
    return parser


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


def pass_score(scores: list[int], passed_score: int = 60) -> tuple[int, float]:
    if not scores:
        return 0, 0.0
    passed_count = sum(score >= passed_score for score in scores)
    return passed_count, passed_count / len(scores)


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
        average[major] = stats["total"] / stats["count"]
    return average


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        students = read_students(args.csv_path)
        total_student = total_students(students)
        scores = [int(student["score"]) for student in students]
        average = average_score(scores)
        max_sc, max_name = max_score(students)
        passed_count, pass_rate = pass_score(scores, args.passing_score)
        major_average = average_major(students)

        print(f"学生人数：{total_student}")
        print(f"平均分：{average:.2f}")
        print(f"最高分：{max_sc:.1f} ({max_name})")
        print(f"及格人数：{passed_count}")
        print(f"及格率：{pass_rate:.2%}")
        print("各专业平均分：")
        for major, score in major_average.items():
            print(f"  {major}: {score:.2f}")
    except FileNotFoundError:
        print(f"错误：文件不存在：{args.csv_path}", file=sys.stderr)
        return 1
    except (KeyError, ValueError) as error:
        print(f"错误：数据格式不正确：{error}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
