import csv

def read_students(path):
    df = []

    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            df.append(row)
    return df

def total_students(df):
    return len(df)

def average_score(df_score):
    return sum(df_score)/total_students(df_score)

def max_score(df, df_score):
    max_sc = max(df_score)
    for i in range(0, len(df)):
        if int(df[i]["score"]) == max_sc:
            name = df[i]["name"]
    return max_sc, name

def pass_score(df_score):
    pass_students = []
    for i in df_score:
        if i>=60:
            pass_students.append(1)
        else:
            pass_students.append(0)
    return sum(pass_students), sum(pass_students)/len(pass_students)

def average_major(df):
    score = []
    index = []
    major = []
    result = []
    for i in range(0, len(df)):
        major.append(df[i]["major"])
    major = list(dict.fromkeys(major))
    for i in range(0, len(major)):
        score.append(0)
        index.append(0)
    for i in range(0, len(df)):
        for j in range(0, len(major)):
            if df[i]["major"] == major[j]:
                score[j] = score[j] + int(df[i]["score"])
                index[j] = index[j] + 1
    for i in range(0, len(score)):
        result.append(score[i]/index[i])
    return major, result


def main():
    df = read_students("week01/diagnostic/data/students.csv")
    total_student = total_students(df)
    df_score = []
    for i in range(0,len(df)):
        df_score.append(int(df[i]["score"]))
    averge = average_score(df_score)
    max_sc, name = max_score(df, df_score)
    pass1,pass_rate = pass_score(df_score)
    major, average_majors = average_major(df)


    print(f"学生人数：{total_student}")
    print(f"平均分：{averge:.2f}")
    print(f"最高分：{max_sc:.1f} ({name})")
    print(f"及格人数：{pass1}")
    print(f"及格率：{pass_rate:.2%}")
    print("各专业平均分：")
    for i in range(0, len(major)):
        print(f"  {major[i]}：{average_majors[i]:.2f}")


if __name__ == "__main__":
    main()
