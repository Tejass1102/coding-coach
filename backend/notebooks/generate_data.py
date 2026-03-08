# Additional high quality brute force examples
# that are clearly distinct from DP

extra_brute_force = [
    # Pattern: two nested loops, index-based
    ("""
def pair_sum_exists(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False
""", 0),
    ("""
def get_all_subarrays(arr):
    result = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr) + 1):
            result.append(arr[i:j])
    return result
""", 0),
    ("""
def intersection_brute(a, b):
    result = []
    for x in a:
        for y in b:
            if x == y and x not in result:
                result.append(x)
    return result
""", 0),
    ("""
def common_elements(arr1, arr2):
    common = []
    for i in arr1:
        for j in arr2:
            if i == j:
                common.append(i)
    return common
""", 0),
    ("""
def brute_max_subarray(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        current = 0
        for j in range(i, len(nums)):
            current += nums[j]
            max_sum = max(max_sum, current)
    return max_sum
""", 0),
    ("""
def is_unique_brute(s):
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if s[i] == s[j]:
                return False
    return True
""", 0),
    ("""
def find_zero_sum_triplet(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            for k in range(j+1, len(arr)):
                if arr[i] + arr[j] + arr[k] == 0:
                    return [arr[i], arr[j], arr[k]]
    return []
""", 0),
    ("""
def count_inversions_brute(arr):
    count = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                count += 1
    return count
""", 0),
]

# Extra DP examples that are CLEARLY dp
# (using dp array, memoization, subproblems)
extra_dp = [
    ("""
def min_cost_climbing(cost):
    n = len(cost)
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
    return dp[n]
""", 2),
    ("""
def decode_ways(s):
    dp = [0] * (len(s) + 1)
    dp[0] = 1
    dp[1] = 0 if s[0] == '0' else 1
    for i in range(2, len(s) + 1):
        if s[i-1] != '0':
            dp[i] += dp[i-1]
        two = int(s[i-2:i])
        if 10 <= two <= 26:
            dp[i] += dp[i-2]
    return dp[len(s)]
""", 2),
    ("""
def longest_increasing_subsequence(nums):
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
""", 2),
    ("""
def egg_drop(n, k):
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = 0
        dp[i][1] = i
    for j in range(1, k + 1):
        dp[1][j] = 1
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            dp[i][j] = float('inf')
            for x in range(1, i + 1):
                worst = 1 + max(dp[x-1][j-1], dp[i-x][j])
                dp[i][j] = min(dp[i][j], worst)
    return dp[n][k]
""", 2),
    ("""
def palindrome_partitioning(s):
    n = len(s)
    dp = [float('inf')] * n
    for i in range(n):
        if s[:i+1] == s[:i+1][::-1]:
            dp[i] = 0
        else:
            for j in range(i):
                if s[j+1:i+1] == s[j+1:i+1][::-1]:
                    dp[i] = min(dp[i], dp[j] + 1)
    return dp[n-1]
""", 2),
    ("""
def matrix_chain(dims):
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1]
                dp[i][j] = min(dp[i][j], cost)
    return dp[0][n-1]
""", 2),
    ("""
def subset_sum(nums, target):
    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for j in range(target, num - 1, -1):
            dp[j] = dp[j] or dp[j - num]
    return dp[target]
""", 2),
    ("""
def house_robber(nums):
    if not nums:
        return 0
    dp = [0] * len(nums)
    dp[0] = nums[0]
    if len(nums) > 1:
        dp[1] = max(nums[0], nums[1])
    for i in range(2, len(nums)):
        dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    return dp[-1]
""", 2),
]

# Print counts
print(f"Extra Brute Force samples: {len(extra_brute_force)}")
print(f"Extra DP samples: {len(extra_dp)}")
print(f"Total new samples: {len(extra_brute_force) + len(extra_dp)}")