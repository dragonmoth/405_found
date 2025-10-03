"""
Import student data from CSV and setup authorized students
"""

import sqlite3
import csv
import os

def import_students_from_csv():
    """Import all students from CSV but only authorize Mihika and Vinayak for face recognition"""
    
    csv_path = "Untitled - Sheet1.csv"
    db_path = "backend/campus_sentinel.db"
    
    # Target students for face recognition
    AUTHORIZED_STUDENTS = {
        "23102069": {"name": "Mihika Patil", "face_trained": True},
        "23101188": {"name": "Vinayak Kundar", "face_trained": True}
    }
    
    print("📊 Importing student data from CSV...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM license_plates")
        cursor.execute("DELETE FROM access_logs")
        
        imported_count = 0
        authorized_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Skip header rows
                if row.get('student_id') == 'student_id' or row.get('student_id') == 'Student_Data_Generation':
                    continue
                    
                student_id = str(row.get('student_id', '')).strip()
                name = row.get('name', '').strip()
                year = row.get('year', '').strip()
                division = row.get('division', '').strip()
                roll_number = row.get('roll_number', '').strip()
                license_plate = row.get('license_plate', '').strip()
                
                # Skip empty rows
                if not student_id or not name:
                    continue
                
                # Create email from name
                email = f"{name.lower().replace(' ', '.')}@college.edu"
                
                # Check if this student is authorized for face recognition
                is_authorized = student_id in AUTHORIZED_STUDENTS
                face_trained = AUTHORIZED_STUDENTS.get(student_id, {}).get('face_trained', False)
                
                # Insert student
                cursor.execute('''
                    INSERT INTO students (student_id, name, email, face_trained, active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (student_id, name, email, face_trained))
                
                imported_count += 1
                
                if is_authorized:
                    authorized_count += 1
                    print(f"✅ Authorized student: {name} (ID: {student_id})")
                
                # Handle license plate if provided
                if license_plate:
                    cursor.execute('''
                        INSERT INTO license_plates (student_id, plate_number, active)
                        VALUES (?, ?, 1)
                    ''', (student_id, license_plate))
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 Import Summary:")
        print(f"   Total students imported: {imported_count}")
        print(f"   Authorized for face recognition: {authorized_count}")
        print(f"   Face recognition enabled for:")
        for student_id, info in AUTHORIZED_STUDENTS.items():
            print(f"     - {info['name']} ({student_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing CSV data: {e}")
        return False

def verify_database():
    """Verify the database setup"""
    print("\n🔍 Verifying database setup...")
    
    try:
        conn = sqlite3.connect("backend/campus_sentinel.db")
        cursor = conn.cursor()
        
        # Check total students
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        # Check authorized students
        cursor.execute("SELECT student_id, name FROM students WHERE face_trained = 1")
        authorized = cursor.fetchall()
        
        # Check license plates
        cursor.execute("SELECT COUNT(*) FROM license_plates")
        total_plates = cursor.fetchone()[0]
        
        print(f"✅ Total students in database: {total_students}")
        print(f"✅ Students authorized for face recognition: {len(authorized)}")
        print(f"✅ License plates registered: {total_plates}")
        
        print(f"\n👤 Authorized students:")
        for student_id, name in authorized:
            print(f"   - {name} ({student_id})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False

def main():
    print("=" * 60)
    print("  Campus Sentinel - Student Data Import")
    print("=" * 60)
    
    # Import CSV data
    if import_students_from_csv():
        # Verify setup
        verify_database()
        
        print("\n" + "=" * 60)
        print("  Import Complete!")
        print("=" * 60)
        print("Next steps:")
        print("1. Place mihika.jpg and vinayak.jpeg in current directory")
        print("2. Run: python setup_face_recognition.py")
        print("3. Start the backend: cd backend && python app.py")
        print("4. Test the system with live camera")
        print("\nOnly Mihika Patil and Vinayak Kundar will have face recognition access!")
    
    else:
        print("❌ Failed to import student data")

if __name__ == "__main__":
    main()