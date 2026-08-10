import io
import json
from typing import TypedDict


class ResearchSummaryCore(TypedDict):
    research_question: str
    data_source: str
    sample_size: int | None


def validate_summary_core(data: object) -> ResearchSummaryCore:
    if isinstance(data, io.IOBase):
        python_text = json.load(data)
    else:
        python_text = data
    if not isinstance(python_text, dict):
        raise (TypeError)
    if (
        "research_question" not in python_text
        or "data_source" not in python_text
        or "sample_size" not in python_text
    ):
        raise (ValueError)
    if (
        python_text["research_question"].strip() == ""
        or python_text["data_source"].strip() == ""
    ):
        raise (ValueError)
    if (
        python_text["sample_size"] != None
        and not isinstance(python_text["sample_size"], int)
        or isinstance(python_text["sample_size"], bool)
        or isinstance(python_text["sample_size"], int)
        and python_text["sample_size"] <= 0
    ):
        raise (ValueError)
    return ResearchSummaryCore(
        research_question=python_text["research_question"],
        data_source=python_text["data_source"],
        sample_size=python_text["sample_size"],
    )


def main() -> None:
    data = "week02/lesson02_validation/data/data.json"
    with open(data, "r", encoding="utf-8") as f:
        print(validate_summary_core(f))


if __name__ == "__main__":
    main()
