"""Create a user account directly from command line"""
import requests
import json

BASE_URL = "http://localhost:7860"

print("=" * 80)
print("CREATE USER ACCOUNT")
print("=" * 80)
print("\nThis script will create a user account in the database.\n")

# Get user input
email = input("Enter your email: ").strip()
password = input("Enter your password (min 6 chars): ").strip()
name = input("Enter your name (optional): ").strip() or "User"

if len(password) < 6:
    print("\n❌ Password must be at least 6 characters!")
    exit(1)

# Create user via API
register_data = {
    "email": email,
    "password": password,
    "name": name
}

print(f"\nCreating account for {email}...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=register_data
    )
    
    result = response.json()
    
    if response.status_code == 200 and result.get("success"):
        print("\n✅ Account created successfully!")
        print(f"\nLogin credentials:")
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print(f"\nYou can now login at: http://localhost:3000/login")
    else:
        print(f"\n❌ Failed to create account!")
        print(f"Error: {result.get('detail', 'Unknown error')}")
        print(f"Full response: {json.dumps(result, indent=2)}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure the backend server is running on http://localhost:7860")

print("\n" + "=" * 80)
