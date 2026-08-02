import pytest

from score_summary import (
    average_major,
    average_score,
    max_score,
    pass_score,
)


def test_average_score_with_typical_scores() -> None:
    scores = [78, 65, 88]

    result = average_score(scores)

    assert result == 77.0

def test_max_score() -> None:
    students = [{"name": "张三", "score": 92}, {"name": "李四", "score": 95}, {"name": "王五", "score": 100}]

    result_score, result_name = max_score(students)

    assert result_score ==100
    assert result_name == "王五" 

def test_pass_score() -> None:
    score = [59, 60, 100]

    result_pass_students, result_pass_rate = pass_score(score)

    assert result_pass_students == 2
    assert result_pass_rate == pytest.approx(2/3)

def test_average_major() -> None:
    students = [{"name": "张三", "major":"应用统计", "score": 92}, 
                {"name": "李四", "major":"数学", "score": 95}, 
                {"name": "王五", "major":"应用统计", "score": 100}]

    result = average_major(students)
    assert len(result.keys()) >= 2
    assert result["应用统计"] == 96
    assert result["数学"] == 95

def test_average_score_with_empty() -> None:
    with pytest.raises(ValueError):
        average_score([])

def test_max_score_with_empty() -> None:
    with pytest.raises(ValueError):
        max_score([])

def test_pass_score_with_empty() -> None:
    assert pass_score([]) == (0, 0.0)

