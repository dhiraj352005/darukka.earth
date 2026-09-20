"""
Test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n2. Testing User Registration...")
    data = {
        "email": "testadmin@test.com",
        "username": "testadmin",
        "password": "Test123!",
        "full_name": "Test Admin",
        "is_admin": True
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"   ✓ User registered successfully")
        return True
    elif response.status_code == 400:
        print(f"   ℹ User already exists (that's OK)")
        return True
    else:
        print(f"   ✗ Error: {response.json()}")
        return False

def test_login():
    """Test user login and get token"""
    print("\n3. Testing User Login...")
    data = {
        "email": "testadmin@test.com",
        "password": "Test123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        token = result.get("access_token")
        print(f"   ✓ Login successful")
        print(f"   Token: {token[:50]}...")
        return token
    else:
        print(f"   ✗ Error: {response.json()}")
        return None

def test_create_project(token):
    """Test project creation"""
    print("\n4. Testing Project Creation...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Project",
        "description": "Test project for site creation",
        "status": "active"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✓ Project created: ID = {result.get('id')}")
        return result.get('id')
    else:
        print(f"   ✗ Error: {response.json()}")
        return None

def test_get_projects(token):
    """Test getting all projects"""
    print("\n5. Testing Get Projects...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"   ✓ Found {len(projects)} project(s)")
        if projects:
            print(f"   First project ID: {projects[0].get('id')}")
            return projects[0].get('id')
        return None
    else:
        print(f"   ✗ Error: {response.json()}")
        return None

def test_create_site(token, project_id):
    """Test site creation"""
    print("\n6. Testing Site Creation...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Site Alpha",
        "description": "Test site for polygon",
        "project_id": project_id,
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [77.5946, 12.9716],
                [77.5956, 12.9716],
                [77.5956, 12.9726],
                [77.5946, 12.9726],
                [77.5946, 12.9716]
            ]]
        },
        "area_hectares": 50,
        "location_info": "Test location"
    }
    response = requests.post(f"{BASE_URL}/sites/", json=data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✓ Site created successfully!")
        print(f"   Site ID: {result.get('id')}")
        return True
    else:
        print(f"   ✗ Error: {response.text}")
        return False

def main():
    print("="*60)
    print("Darukaa.Earth API Testing")
    print("="*60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the backend running?")
        return
    
    # Test 2: Register user
    test_register()
    
    # Test 3: Login
    token = test_login()
    if not token:
        print("\n❌ Login failed. Cannot continue.")
        return
    
    # Test 4 & 5: Get or create project
    project_id = test_get_projects(token)
    if not project_id:
        project_id = test_create_project(token)
    
    if not project_id:
        print("\n❌ No project available. Cannot create site.")
        return
    
    # Test 6: Create site
    if test_create_site(token, project_id):
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n🎉 Your API is working correctly!")
        print(f"   • Backend is running")
        print(f"   • Authentication works")
        print(f"   • Project ID {project_id} exists")
        print(f"   • Site creation works")
        print(f"\n📝 Use project ID {project_id} when creating sites in the frontend")
    else:
        print("\n" + "="*60)
        print("⚠️ SITE CREATION FAILED")
        print("="*60)
        print("\nDebugging needed. Check the error message above.")

if __name__ == "__main__":
    main()
