import requests

# Check if students are in database
def check_students():
    try:
        response = requests.get('http://localhost:5000/api/students')
        if response.ok:
            students = response.json()
            print(f"Found {len(students)} students in database:")
            for i, student in enumerate(students[:5]):  # Show first 5
                print(f"  {i+1}. ID: {student['student_id']}, Name: {student['name']}")
            if len(students) > 5:
                print(f"  ... and {len(students) - 5} more")
        else:
            print("Failed to get students")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_students()