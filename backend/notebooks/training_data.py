# Training dataset — labeled code samples
# Format: (code, label)
# Labels: 0=Brute Force, 1=Sliding Window, 2=Dynamic Programming,
#         3=Greedy, 4=Binary Search, 5=Divide & Conquer

data = [
    # ---- BRUTE FORCE (label 0) ----
    ("""
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""", 0),
    ("""
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                duplicates.append(arr[i])
    return duplicates
""", 0),
    ("""
def max_subarray_brute(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        for j in range(i+1, len(nums)+1):
            curr_sum = sum(nums[i:j])
            max_sum = max(max_sum, curr_sum)
    return max_sum
""", 0),
    ("""
def contains_duplicate(nums):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
""", 0),
    ("""
def string_match(text, pattern):
    n, m = len(text), len(pattern)
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i+j] != pattern[j]:
                match = False
                break
        if match:
            return i
    return -1
""", 0),
    ("""
def three_sum(nums):
    result = []
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            for k in range(j+1, len(nums)):
                if nums[i] + nums[j] + nums[k] == 0:
                    result.append([nums[i], nums[j], nums[k]])
    return result
""", 0),
    ("""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""", 0),
    ("""
def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
""", 0),
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
    ("""
def find_pair_with_sum(arr, target):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] + arr[j] == target:
                return (arr[i], arr[j])
    return None
""", 0),
    ("""
def max_product_pair(nums):
    max_product = float('-inf')
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            max_product = max(max_product, nums[i] * nums[j])
    return max_product
""", 0),
    ("""
def count_pairs_with_diff(arr, k):
    count = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if abs(arr[i] - arr[j]) == k:
                count += 1
    return count
""", 0),
    ("""
def has_pair_with_sum(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i+1, n):
            if nums[i] + nums[j] == target:
                return True
    return False
""", 0),
    ("""
def all_pairs(arr):
    pairs = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            pairs.append((arr[i], arr[j]))
    return pairs
""", 0),
    ("""
def min_pair_sum(nums, target):
    result = float('inf')
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] < target:
                result = min(result, nums[i] + nums[j])
    return result
""", 0),

    # ---- SLIDING WINDOW (label 1) ----
    ("""
def max_sum_subarray(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum
    for i in range(len(arr) - k):
        window_sum = window_sum - arr[i] + arr[i + k]
        max_sum = max(max_sum, window_sum)
    return max_sum
""", 1),
    ("""
def longest_substring_no_repeat(s):
    char_set = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
""", 1),
    ("""
def min_window_substring(s, t):
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = 0
    result = ""
    for right, char in enumerate(s):
        if need[char] > 0:
            missing -= 1
        need[char] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if not result or right - left + 1 < len(result):
                result = s[left:right+1]
            need[s[left]] += 1
            missing += 1
            left += 1
    return result
""", 1),
    ("""
def find_all_anagrams(s, p):
    from collections import Counter
    result = []
    p_count = Counter(p)
    s_count = Counter(s[:len(p)])
    if s_count == p_count:
        result.append(0)
    for i in range(len(p), len(s)):
        s_count[s[i]] += 1
        s_count[s[i - len(p)]] -= 1
        if s_count[s[i - len(p)]] == 0:
            del s_count[s[i - len(p)]]
        if s_count == p_count:
            result.append(i - len(p) + 1)
    return result
""", 1),
    ("""
def longest_ones(nums, k):
    left = 0
    zeros = 0
    max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
""", 1),
    ("""
def max_vowels(s, k):
    vowels = set('aeiou')
    count = sum(1 for c in s[:k] if c in vowels)
    max_count = count
    for i in range(k, len(s)):
        count += (s[i] in vowels) - (s[i-k] in vowels)
        max_count = max(max_count, count)
    return max_count
""", 1),
    ("""
def contains_nearby_duplicate(nums, k):
    window = {}
    for i, num in enumerate(nums):
        if num in window and i - window[num] <= k:
            return True
        window[num] = i
    return False
""", 1),
    ("""
def max_average(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i-k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
""", 1),

    # ---- DYNAMIC PROGRAMMING (label 2) ----
    ("""
def fib(n):
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
""", 2),
    ("""
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for w in range(capacity+1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])
    return dp[n][capacity]
""", 2),
    ("""
def longest_common_subsequence(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
""", 2),
    ("""
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
""", 2),
    ("""
def max_subarray(nums):
    dp = nums[0]
    max_sum = nums[0]
    for num in nums[1:]:
        dp = max(num, dp + num)
        max_sum = max(max_sum, dp)
    return max_sum
""", 2),
    ("""
def climb_stairs(n):
    if n <= 2:
        return n
    dp = [0] * (n+1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n+1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
""", 2),
    ("""
def unique_paths(m, n):
    dp = [[1]*n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]
""", 2),
    ("""
def word_break(s, wordDict):
    dp = [False] * (len(s)+1)
    dp[0] = True
    for i in range(1, len(s)+1):
        for word in wordDict:
            if dp[i-len(word)] and s[i-len(word):i] == word:
                dp[i] = True
    return dp[len(s)]
""", 2),
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

    # ---- GREEDY (label 3) ----
    ("""
def jump_game(nums):
    max_reach = 0
    for i, num in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + num)
    return True
""", 3),
    ("""
def activity_selection(start, end):
    activities = sorted(zip(start, end), key=lambda x: x[1])
    selected = [activities[0]]
    for i in range(1, len(activities)):
        if activities[i][0] >= selected[-1][1]:
            selected.append(activities[i])
    return selected
""", 3),
    ("""
def fractional_knapsack(weights, values, capacity):
    items = sorted(zip(values, weights), key=lambda x: x[0]/x[1], reverse=True)
    total = 0
    for value, weight in items:
        if capacity >= weight:
            total += value
            capacity -= weight
        else:
            total += value * (capacity / weight)
            break
    return total
""", 3),
    ("""
def assign_cookies(children, cookies):
    children.sort()
    cookies.sort()
    child = 0
    for cookie in cookies:
        if child < len(children) and cookie >= children[child]:
            child += 1
    return child
""", 3),
    ("""
def min_platforms(arrivals, departures):
    arrivals.sort()
    departures.sort()
    platforms = 1
    max_platforms = 1
    i, j = 1, 0
    while i < len(arrivals):
        if arrivals[i] <= departures[j]:
            platforms += 1
            i += 1
        else:
            platforms -= 1
            j += 1
        max_platforms = max(max_platforms, platforms)
    return max_platforms
""", 3),
    ("""
def can_complete_circuit(gas, cost):
    total = 0
    tank = 0
    start = 0
    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total += diff
        tank += diff
        if tank < 0:
            start = i + 1
            tank = 0
    return start if total >= 0 else -1
""", 3),
    ("""
def is_valid_parentheses(s):
    count = 0
    for c in s:
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0
""", 3),
    ("""
def partition_labels(s):
    last = {c: i for i, c in enumerate(s)}
    result = []
    start = anchor = 0
    for i, c in enumerate(s):
        anchor = max(anchor, last[c])
        if i == anchor:
            result.append(i - start + 1)
            start = i + 1
    return result
""", 3),

    # ---- BINARY SEARCH (label 4) ----
    ("""
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""", 4),
    ("""
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
""", 4),
    ("""
def find_min_rotated(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]
""", 4),
    ("""
def sqrt_binary(x):
    if x < 2:
        return x
    left, right = 1, x // 2
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    return right
""", 4),
    ("""
def first_bad_version(n, is_bad):
    left, right = 1, n
    while left < right:
        mid = (left + right) // 2
        if is_bad(mid):
            right = mid
        else:
            left = mid + 1
    return left
""", 4),
    ("""
def search_insert(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
""", 4),
    ("""
def find_peak(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[mid+1]:
            right = mid
        else:
            left = mid + 1
    return left
""", 4),
    ("""
def kth_smallest(matrix, k):
    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        count = sum(
            min(k, len([x for x in row if x <= mid]))
            for row in matrix
        )
        if count < k:
            lo = mid + 1
        else:
            hi = mid
    return lo
""", 4),

    # ---- DIVIDE & CONQUER (label 5) ----
    ("""
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
""", 5),
    ("""
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
""", 5),
    ("""
def max_crossing_sum(arr, left, mid, right):
    left_sum = float('-inf')
    total = 0
    for i in range(mid, left-1, -1):
        total += arr[i]
        left_sum = max(left_sum, total)
    right_sum = float('-inf')
    total = 0
    for i in range(mid+1, right+1):
        total += arr[i]
        right_sum = max(right_sum, total)
    return left_sum + right_sum

def max_subarray_dc(arr, left, right):
    if left == right:
        return arr[left]
    mid = (left + right) // 2
    return max(
        max_subarray_dc(arr, left, mid),
        max_subarray_dc(arr, mid+1, right),
        max_crossing_sum(arr, left, mid, right)
    )
""", 5),
    ("""
def power(base, exp):
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    return base * power(base, exp - 1)
""", 5),
    ("""
def closest_pair(points):
    def dist(p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

    if len(points) <= 3:
        min_d = float('inf')
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                min_d = min(min_d, dist(points[i], points[j]))
        return min_d

    mid = len(points) // 2
    left = closest_pair(points[:mid])
    right = closest_pair(points[mid:])
    return min(left, right)
""", 5),
    ("""
def count_inversions(arr):
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, lc = count_inversions(arr[:mid])
    right, rc = count_inversions(arr[mid:])
    merged = []
    count = lc + rc
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            count += len(left) - i
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, count
""", 5),
    ("""
def majority_element(nums):
    if len(nums) == 1:
        return nums[0]
    mid = len(nums) // 2
    left = majority_element(nums[:mid])
    right = majority_element(nums[mid:])
    if left == right:
        return left
    return left if nums.count(left) > nums.count(right) else right
""", 5),
    ("""
def binary_exponentiation(base, exp, mod):
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = binary_exponentiation(base, exp//2, mod)
        return (half * half) % mod
    return (base * binary_exponentiation(base, exp-1, mod)) % mod
""", 5),
]

LABEL_NAMES = {
    0: "Brute Force",
    1: "Sliding Window",
    2: "Dynamic Programming",
    3: "Greedy",
    4: "Binary Search",
    5: "Divide & Conquer"
}