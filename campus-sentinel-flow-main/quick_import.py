import requests
import json

# Import student data from CSV
def import_student_data():
    try:
        response = requests.post('http://localhost:5000/api/import_csv')
        result = response.json()
        
        if response.ok:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Importing student data from CSV...")
    import_student_data()