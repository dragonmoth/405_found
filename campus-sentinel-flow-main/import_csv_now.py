import requests

# Force import CSV data with the correct path
csv_data = """
[
    {
        "student_id": "23102824",
        "name": "Ankit Ayaan Patel",
        "license_plate": "KAF 9279"
    },
    {
        "student_id": "23107924", 
        "name": "Avni Divya Mehta",
        "license_plate": "MH71HQ6925"
    },
    {
        "student_id": "23104150",
        "name": "Vivaan Shah", 
        "license_plate": "LVE 6820"
    },
    {
        "student_id": "23108573",
        "name": "Avni Rao",
        "license_plate": ""
    },
    {
        "student_id": "23101916",
        "name": "Nikhil Shaurya Jain",
        "license_plate": ""
    }
]
"""

def manual_import():
    import sqlite3
    import json
    
    try:
        # Manual database import
        conn = sqlite3.connect('backend/campus_sentinel.db')
        cursor = conn.cursor()
        
        # Sample data from CSV
        students_data = [
            ("23102824", "Ankit Ayaan Patel", "KAF 9279"),
            ("23107924", "Avni Divya Mehta", "MH71HQ6925"),
            ("23104150", "Vivaan Shah", "LVE 6820"),
            ("23108573", "Avni Rao", ""),
            ("23101916", "Nikhil Shaurya Jain", ""),
            ("23107537", "Riya Mishra", "KA10SB2104"),
            ("23104872", "Kabir Yadav", "MH20EF1958"),
            ("23109883", "Ankit Verma", "MH75PQ7868")
        ]
        
        imported = 0
        for student_id, name, plate in students_data:
            # Check if exists
            cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student_id,))
            if not cursor.fetchone():
                # Insert student
                email = f"{name.lower().replace(' ', '.')}@college.edu"
                cursor.execute('''
                    INSERT INTO students (student_id, name, email, active)
                    VALUES (?, ?, ?, 1)
                ''', (student_id, name, email))
                imported += 1
                
                # Insert license plate if exists
                if plate:
                    cursor.execute('''
                        INSERT INTO license_plates (student_id, plate_number, active)
                        VALUES (?, ?, 1)
                    ''', (student_id, plate))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Manually imported {imported} students")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    manual_import()