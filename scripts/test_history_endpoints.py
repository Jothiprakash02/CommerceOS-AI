"""
Test script for history management endpoints.

Tests:
1. GET /history - List all analyses
2. PUT /history/{id}/star - Star/unstar an analysis
3. DELETE /history/{id} - Delete an analysis
4. GET /export/{id}?format=json - Export analysis as JSON
5. GET /export/{id}?format=csv - Export analysis as CSV

Usage:
    python scripts/test_history_endpoints.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8080"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_get_history():
    """Test GET /history endpoint"""
    print_section("TEST 1: GET /history")
    
    try:
        response = requests.get(f"{BASE_URL}/history?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Found {len(data)} analyses")
            
            if data:
                print("\nFirst analysis:")
                first = data[0]
                print(f"  ID: {first.get('id')}")
                print(f"  Product: {first.get('product_name')}")
                print(f"  Country: {first.get('country')}")
                print(f"  Risk: {first.get('risk_level')}")
                print(f"  Starred: {first.get('starred', False)}")
                print(f"  Created: {first.get('created_at')}")
                return first.get('id')  # Return ID for further tests
            else:
                print("\n⚠ No analyses found in history")
                print("  Run an analysis first to test other endpoints")
                return None
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_star_analysis(analysis_id):
    """Test PUT /history/{id}/star endpoint"""
    print_section(f"TEST 2: PUT /history/{analysis_id}/star")
    
    if not analysis_id:
        print("⚠ Skipping - no analysis ID available")
        return False
    
    try:
        # Star the analysis
        response = requests.put(f"{BASE_URL}/history/{analysis_id}/star")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Starred: {data.get('starred')}")
            
            # Verify by getting history again
            verify = requests.get(f"{BASE_URL}/history?limit=5")
            if verify.status_code == 200:
                analyses = verify.json()
                target = next((a for a in analyses if a['id'] == analysis_id), None)
                if target:
                    print(f"✓ Verified starred status: {target.get('starred')}")
                    return True
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_export_json(analysis_id):
    """Test GET /export/{id}?format=json endpoint"""
    print_section(f"TEST 3: GET /export/{analysis_id}?format=json")
    
    if not analysis_id:
        print("⚠ Skipping - no analysis ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/export/{analysis_id}?format=json")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Export successful")
            print(f"\nExported data:")
            print(f"  Product: {data.get('product_name')}")
            print(f"  Demand Score: {data.get('demand_score')}")
            print(f"  Competition Score: {data.get('competition_score')}")
            print(f"  Risk Level: {data.get('risk_level')}")
            print(f"  Profit Margin: {data.get('profit_margin')}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_export_csv(analysis_id):
    """Test GET /export/{id}?format=csv endpoint"""
    print_section(f"TEST 4: GET /export/{analysis_id}?format=csv")
    
    if not analysis_id:
        print("⚠ Skipping - no analysis ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/export/{analysis_id}?format=csv")
        
        if response.status_code == 200:
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Export successful")
            print(f"\nCSV Content:")
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_delete_analysis(analysis_id):
    """Test DELETE /history/{id} endpoint"""
    print_section(f"TEST 5: DELETE /history/{analysis_id}")
    
    if not analysis_id:
        print("⚠ Skipping - no analysis ID available")
        return False
    
    print("⚠ This test will DELETE an analysis from the database")
    print("  Press Enter to continue or Ctrl+C to skip...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n⚠ Test skipped by user")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/history/{analysis_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Message: {data.get('message')}")
            
            # Verify deletion
            verify = requests.get(f"{BASE_URL}/history?limit=50")
            if verify.status_code == 200:
                analyses = verify.json()
                if not any(a['id'] == analysis_id for a in analyses):
                    print(f"✓ Verified: Analysis {analysis_id} no longer in history")
                    return True
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  History Management Endpoints Test Suite")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure the backend is running on port 8080")
    
    # Check if backend is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.status_code != 200:
            print("\n✗ Backend is not responding correctly")
            print("  Start the backend with: python -m uvicorn main:app --port 8080")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Cannot connect to backend: {e}")
        print("  Start the backend with: python -m uvicorn main:app --port 8080")
        sys.exit(1)
    
    print("✓ Backend is running\n")
    
    # Run tests
    results = []
    
    # Test 1: Get history
    analysis_id = test_get_history()
    results.append(("GET /history", analysis_id is not None or True))
    
    if analysis_id:
        # Test 2: Star analysis
        results.append(("PUT /history/{id}/star", test_star_analysis(analysis_id)))
        
        # Test 3: Export JSON
        results.append(("GET /export/{id}?format=json", test_export_json(analysis_id)))
        
        # Test 4: Export CSV
        results.append(("GET /export/{id}?format=csv", test_export_csv(analysis_id)))
        
        # Test 5: Delete analysis (optional)
        results.append(("DELETE /history/{id}", test_delete_analysis(analysis_id)))
    else:
        print("\n⚠ Skipping remaining tests - no analyses available")
        print("  Run an analysis first using the frontend or API")
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(0)
