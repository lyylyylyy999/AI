# 命令行应用：参数、错误流与退出码

## 本课目标

- 使用 `argparse` 接收 CSV 文件路径。
- 保留默认样例文件，兼容不传参数的运行方式。
- 区分正常输出 `stdout` 和错误输出 `stderr`。
- 使用退出码表示成功、文件错误和数据错误。
- 使用 pytest 的 `tmp_path` 测试真实临时文件。

## 目标用法

不传路径时读取默认样例：

```powershell
python week01\diagnostic\score_summary.py
```

传入其他 CSV：

```powershell
python week01\diagnostic\score_summary.py C:\data\scores.csv
```

查看帮助：

```powershell
python week01\diagnostic\score_summary.py --help
```

## 第一步：参数解析器

新增导入：

```python
import argparse
import sys
```

把默认文件路径放到模块级常量中：

```python
DEFAULT_DATA_FILE = (
    Path(__file__).resolve().parent / "data" / "students.csv"
)
```

创建参数解析器：

```python
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
    return parser
```

这里的 `nargs="?"` 表示位置参数可以出现零次或一次。

## 第二步：让 main 可测试

把函数签名改成：

```python
def main(argv: list[str] | None = None) -> int:
```

解析参数：

```python
args = build_parser().parse_args(argv)
```

- 命令行直接运行时，`argv=None`，argparse 会读取真实命令行参数。
- 测试时传入 `main([])`，表示没有额外参数。
- 测试时传入 `main([str(csv_path)])`，表示用户输入了文件路径。

## 第三步：错误与退出码

本课采用以下契约：

| 退出码 | 含义 |
|---:|---|
| 0 | 成功 |
| 1 | 文件不存在 |
| 2 | CSV 数据内容不合法 |

在 `main()` 中用 `try/except` 包围读取和计算流程：

```python
try:
    # 读取、转换、计算和打印
except FileNotFoundError:
    print(f"错误：文件不存在：{args.csv_path}", file=sys.stderr)
    return 1
except (KeyError, ValueError) as error:
    print(f"错误：数据格式不正确：{error}", file=sys.stderr)
    return 2

return 0
```

程序入口改成：

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

`SystemExit` 会把 `main()` 返回的整数交给操作系统作为进程退出码。

## 第四步：清理输出

删除 `print(students)`。正常输出只保留统计摘要，错误只写入 `stderr`。

## 第五步：集成测试

### 更新默认路径测试

原来的集成测试调用改为：

```python
exit_code = main([])
assert exit_code == 0
```

### 自定义 CSV

新增测试，使用 pytest 内置的 `tmp_path`：

```python
def test_main_accepts_custom_csv(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_path = tmp_path / "custom.csv"
    csv_path.write_text(
        "name,major,score\n甲,统计,60\n乙,统计,100\n",
        encoding="utf-8",
    )

    exit_code = main([str(csv_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "学生人数：2" in output
    assert "平均分：80.00" in output
```

测试文件需要导入：

```python
from pathlib import Path
```

### 文件不存在

独立编写测试并验证：

- 调用 `main([str(tmp_path / "missing.csv")])`。
- 返回值为 `1`。
- 使用 `capsys.readouterr().err` 获取错误流。
- 错误流包含 `文件不存在`。

### 非法分数

独立编写测试，临时 CSV 中将一个分数写成 `abc`，验证：

- 返回值为 `2`。
- `stderr` 包含 `数据格式不正确`。
- 程序不向调用者抛出未处理异常。

## 验收要求

- 原有 13 条用例继续通过。
- 新增 3 条 CLI 集成测试。
- 总计应为 16 条测试。
- 默认路径、自定义路径、缺失文件和非法分数均有明确行为。
- 不修改参考答案文件。

完成后运行：

```powershell
.\.venv\Scripts\python.exe -m pytest week01\diagnostic\test_score_summary.py -v
```

再手动运行帮助：

```powershell
.\.venv\Scripts\python.exe week01\diagnostic\score_summary.py --help
```

回复：

```text
CLI 第一版完成
测试数量：
默认运行退出码：
缺失文件退出码：
非法数据退出码：
stdout 和 stderr 的区别：
argv=None 的作用：
```

