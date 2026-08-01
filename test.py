import csv

path = "week01/diagnostic/data/students.csv"

with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        reader = list(reader)

print(reader["major"])