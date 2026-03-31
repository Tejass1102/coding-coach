"""
Test API endpoints - Run this AFTER starting backend with: python backend/main.py
Usage: python test_api.py
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("🧪 Testing Coding Coach API")
print("=" * 70)

# Test 1: Health check
print("\n[1/3] Testing health endpoint...")
try:
    response = requests.get(f"{API_URL}/")
    if response.status_code == 200:
        print(f"  ✅ Health check passed")
        print(f"  Response: {response.json()}")
    else:
        print(f"  ❌ Health check failed - Status: {response.status_code}")
        print("  Make sure backend is running: python backend/main.py")
        exit(1)
except requests.exceptions.ConnectionError:
    print(f"  ❌ Cannot connect to {API_URL}")
    print("  Make sure backend is running: python backend/main.py")
    exit(1)

# Test 2: Analyze endpoint with HashMap example
print("\n[2/3] Testing /api/analyze endpoint with HashMap example...")

# Sample Java code - HashMap approach (Two Sum)
sample_code = '''
public class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] {map.get(complement), i};
            }
            map.put(nums[i], i);
        }
        return new int[] {0, 0};
    }
}
'''

payload = {
    "code": sample_code,
    "language": "java",
    "problem_name": "Two Sum"
}

try:
    response = requests.post(
        f"{API_URL}/api/analyze",
        json=payload,
        timeout=30
    )
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("  ✅ Analyze endpoint works!")
        
        print("\n  📊 Response Summary:")
        print(f"    - Problem: {result.get('problem_name')}")
        print(f"    - Approach: {result.get('approach_detection', {}).get('predicted_approach')}")
        print(f"    - Confidence: {result.get('approach_detection', {}).get('confidence')}%")
        print(f"    - Time Complexity: {result.get('analysis', {}).get('time_complexity')}")
        print(f"    - Space Complexity: {result.get('analysis', {}).get('space_complexity')}")
        
        print("\n  Full Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"  ❌ Request failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("  ❌ Request timed out (>30s)")
    print("  This might be the first request (model loading takes time)")
    print("  Try again - it should be faster on second request")
except Exception as e:
    print(f"  ❌ Error: {str(e)}")

# Test 3: History endpoint
print("\n[3/3] Testing /api/history endpoint...")
try:
    response = requests.get(f"{API_URL}/api/history", timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ History endpoint works!")
        print(f"    - Total submissions: {result.get('total')}")
        
        if result.get('submissions'):
            print(f"    - Latest submission: {result['submissions'][0].get('problem_name')}")
    else:
        print(f"  ⚠️  Status {response.status_code}")
        
except Exception as e:
    print(f"  ⚠️  Error accessing history: {str(e)}")

print("\n" + "=" * 70)
print("✅ API TESTING COMPLETE")
print("=" * 70)
print("\nIf all tests passed:")
print("  1. Load the Chrome extension (chrome://extensions/)")
print("  2. Go to https://leetcode.com/problems/two-sum/")
print("  3. Write some code and click the ⚡ Coding Coach button")
print("=" * 70)
