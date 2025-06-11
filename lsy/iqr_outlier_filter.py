def remove_outliers(data):
    data.sort()
    q1 = data[len(data)//4]
    q3 = data[(len(data)*3)//4]
    iqr = q3 - q1
    return [x for x in data if q1 - 1.5*iqr <= x <= q3 + 1.5*iqr]

nums = list(map(int, input("숫자 목록 입력 (띄어쓰기): ").split()))
filtered = remove_outliers(nums)
print("이상치 제거 후 평균:", sum(filtered)/len(filtered))
