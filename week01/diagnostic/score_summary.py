import csv

def openfile(path):
    df = []

    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            df.append(row)
    return df

def total_students(df):
    return len(df)

def averge_score(df):
    return sum(df)/total_students(df)

def max_score(df):
    return max(df)

def pass_score(df_score):
    pass_students = []
    for i in df_score:
        if i>60:
            pass_students.append(1)
        else:
            pass_students.append(0)
    return sum(pass_students), sum(pass_students)/len(pass_students)


def main():
    df = openfile("week01/diagnostic/data/students.csv")
    print(df)
    total_student = total_students(df)
    df_score = []
    for i in range(0,len(df)):
        df_score.append(int(df[i]["score"]))
    averge = averge_score(df_score)
    max = max_score(df_score)
    pass1,pass_rate = pass_score(df_score)


    print(f"学生人数：{total_student}")
    print(f"平均分：{averge:.2f}")
    print(f"最高分：{max}()")
    print(f"及格人数：{pass1}")
    print(f"及格率：{pass_rate}")

    df_1 = 0
    df_2 = 0
    df_3 = 0
    a = 0
    b = 0
    c = 0

    for i in range(0, len(df)):
        if df[i]["major"] == "应用统计":
            df_1 = df_1 + int(df[i]["score"])
            a = a+1
        if df[i]["major"] == "经济统计":
            df_2 = df_2 + int(df[i]["score"])
            b = b+1
        if df[i]["major"] == "数据科学":
            df_3 = df_3 + int(df[i]["score"])
            c = c+1
    print("各专业平均分")
    print(f"  应用统计：{df_1/a:.2f}")
    print(f"  经济统计：{df_2/b:.2f}")
    print(f"  数据科学：{df_3/c:.2f}")


if __name__ == "__main__":
    main()
