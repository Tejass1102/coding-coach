# backend/data/curated_problems.py

# A curated list of high-quality, canonical LeetCode problems mapped to our core ML classifier approaches.
# These will be used to recommend targeted questions to the user based on their weak algorithmic areas.

CURATED_PROBLEMS = {
    "Two Pointers": [
        {"title": "Valid Palindrome", "slug": "valid-palindrome", "difficulty": "Easy"},
        {"title": "Two Sum II - Input Array Is Sorted", "slug": "two-sum-ii-input-array-is-sorted", "difficulty": "Medium"},
        {"title": "3Sum", "slug": "3sum", "difficulty": "Medium"},
        {"title": "Container With Most Water", "slug": "container-with-most-water", "difficulty": "Medium"},
        {"title": "Trapping Rain Water", "slug": "trapping-rain-water", "difficulty": "Hard"}
    ],
    "Sliding Window": [
        {"title": "Best Time to Buy and Sell Stock", "slug": "best-time-to-buy-and-sell-stock", "difficulty": "Easy"},
        {"title": "Longest Substring Without Repeating Characters", "slug": "longest-substring-without-repeating-characters", "difficulty": "Medium"},
        {"title": "Longest Repeating Character Replacement", "slug": "longest-repeating-character-replacement", "difficulty": "Medium"},
        {"title": "Permutation in String", "slug": "permutation-in-string", "difficulty": "Medium"},
        {"title": "Minimum Window Substring", "slug": "minimum-window-substring", "difficulty": "Hard"}
    ],
    "Dynamic Programming": [
        {"title": "Climbing Stairs", "slug": "climbing-stairs", "difficulty": "Easy"},
        {"title": "House Robber", "slug": "house-robber", "difficulty": "Medium"},
        {"title": "Coin Change", "slug": "coin-change", "difficulty": "Medium"},
        {"title": "Longest Increasing Subsequence", "slug": "longest-increasing-subsequence", "difficulty": "Medium"},
        {"title": "Regular Expression Matching", "slug": "regular-expression-matching", "difficulty": "Hard"}
    ],
    "Greedy": [
        {"title": "Maximum Subarray", "slug": "maximum-subarray", "difficulty": "Medium"},
        {"title": "Jump Game", "slug": "jump-game", "difficulty": "Medium"},
        {"title": "Merge Intervals", "slug": "merge-intervals", "difficulty": "Medium"},
        {"title": "Gas Station", "slug": "gas-station", "difficulty": "Medium"},
        {"title": "Candy", "slug": "candy", "difficulty": "Hard"}
    ],
    "Binary Search": [
        {"title": "Binary Search", "slug": "binary-search", "difficulty": "Easy"},
        {"title": "Search a 2D Matrix", "slug": "search-a-2d-matrix", "difficulty": "Medium"},
        {"title": "Find Minimum in Rotated Sorted Array", "slug": "find-minimum-in-rotated-sorted-array", "difficulty": "Medium"},
        {"title": "Koko Eating Bananas", "slug": "koko-eating-bananas", "difficulty": "Medium"},
        {"title": "Median of Two Sorted Arrays", "slug": "median-of-two-sorted-arrays", "difficulty": "Hard"}
    ],
    "Divide & Conquer": [
        {"title": "Merge k Sorted Lists", "slug": "merge-k-sorted-lists", "difficulty": "Hard"},
        {"title": "Sort an Array", "slug": "sort-an-array", "difficulty": "Medium"},
        {"title": "Construct Binary Tree from Preorder and Inorder Traversal", "slug": "construct-binary-tree-from-preorder-and-inorder-traversal", "difficulty": "Medium"}
    ],
    "Hash Map": [
        {"title": "Two Sum", "slug": "two-sum", "difficulty": "Easy"},
        {"title": "Valid Anagram", "slug": "valid-anagram", "difficulty": "Easy"},
        {"title": "Group Anagrams", "slug": "group-anagrams", "difficulty": "Medium"},
        {"title": "Top K Frequent Elements", "slug": "top-k-frequent-elements", "difficulty": "Medium"},
        {"title": "Longest Consecutive Sequence", "slug": "longest-consecutive-sequence", "difficulty": "Medium"}
    ],
    "Brute Force": [
        # It's rare you *want* to practice brute force, but these are array-heavy problems that usually start with Brute Force.
        {"title": "Contains Duplicate", "slug": "contains-duplicate", "difficulty": "Easy"},
        {"title": "Missing Number", "slug": "missing-number", "difficulty": "Easy"},
        {"title": "Find All Numbers Disappeared in an Array", "slug": "find-all-numbers-disappeared-in-an-array", "difficulty": "Easy"}
    ],
}
