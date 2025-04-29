import numpy as np

# ... existing code ...

# 生成 4x4 的顺时针螺旋矩阵
n = 6
matrix = np.zeros((n, n), dtype=int)
num = 1
left, right, top, bottom = 0, n - 1, 0, n - 1

while left <= right and top <= bottom:
    # 从左到右填充顶部行
    for col in range(left, right + 1):
        matrix[top][col] = num
        num += 1
    top += 1

    # 从上到下填充右侧列
    for row in range(top, bottom + 1):
        matrix[row][right] = num
        num += 1
    right -= 1

    if top <= bottom:
        # 从右到左填充底部行
        for col in range(right, left - 1, -1):
            matrix[bottom][col] = num
            num += 1
        bottom -= 1

    if left <= right:
        # 从下到上填充左侧列
        for row in range(bottom, top - 1, -1):
            matrix[row][left] = num
            num += 1
        left += 1

print("4x4 顺时针螺旋矩阵：\n", matrix)

# ... existing code ...