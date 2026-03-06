from flask import Flask, render_template, request, jsonify
import socket
import datetime
import random

app = Flask(__name__)

# Simulated student database
students_db = {
    "S2401": {"name": "Aarav Sharma",     "roll": "S2401", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 88, "Probablity and Statistics": 91, "Design and Analysis of Algorithms": 85, "Machine Learning": 79, "Design Thinking": 92, "Database Management System": 87}},
    "S2402": {"name": "Priya Patel",      "roll": "S2402", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 76, "Probablity and Statistics": 83, "Design and Analysis of Algorithms": 90, "Machine Learning": 88, "Design Thinking": 74, "Database Management System": 81}},
    "S2403": {"name": "Rohit Verma",      "roll": "S2403", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 62, "Probablity and Statistics": 70, "Design and Analysis of Algorithms": 68, "Machine Learning": 75, "Design Thinking": 80, "Database Management System": 65}},
    "S2404": {"name": "Sneha Joshi",      "roll": "S2404", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 95, "Probablity and Statistics": 98, "Design and Analysis of Algorithms": 92, "Machine Learning": 94, "Design Thinking": 96, "Database Management System": 91}},
    "S2405": {"name": "Karan Mehta",      "roll": "S2405", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 71, "Probablity and Statistics": 68, "Design and Analysis of Algorithms": 74, "Machine Learning": 80, "Design Thinking": 66, "Database Management System": 72}},
    "S2406": {"name": "Anjali Singh",     "roll": "S2406", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 84, "Probablity and Statistics": 79, "Design and Analysis of Algorithms": 88, "Machine Learning": 82, "Design Thinking": 77, "Database Management System": 83}},
    "S2407": {"name": "Vikram Nair",      "roll": "S2407", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 55, "Probablity and Statistics": 61, "Design and Analysis of Algorithms": 58, "Machine Learning": 63, "Design Thinking": 70, "Database Management System": 60}},
    "S2408": {"name": "Divya Reddy",      "roll": "S2408", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 90, "Probablity and Statistics": 87, "Design and Analysis of Algorithms": 93, "Machine Learning": 85, "Design Thinking": 89, "Database Management System": 94}},
    "S2409": {"name": "Arjun Kulkarni",   "roll": "S2409", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 74, "Probablity and Statistics": 69, "Design and Analysis of Algorithms": 77, "Machine Learning": 72, "Design Thinking": 81, "Database Management System": 68}},
    "S2410": {"name": "Nisha Desai",      "roll": "S2410", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 83, "Probablity and Statistics": 76, "Design and Analysis of Algorithms": 80, "Machine Learning": 91, "Design Thinking": 85, "Database Management System": 78}},
    "S2411": {"name": "Rajan Iyer",       "roll": "S2411", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 59, "Probablity and Statistics": 64, "Design and Analysis of Algorithms": 61, "Machine Learning": 57, "Design Thinking": 66, "Database Management System": 62}},
    "S2412": {"name": "Pooja Mishra",     "roll": "S2412", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 91, "Probablity and Statistics": 86, "Design and Analysis of Algorithms": 94, "Machine Learning": 89, "Design Thinking": 93, "Database Management System": 88}},
    "S2413": {"name": "Sameer Khan",      "roll": "S2413", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 67, "Probablity and Statistics": 72, "Design and Analysis of Algorithms": 65, "Machine Learning": 70, "Design Thinking": 74, "Database Management System": 69}},
    "S2414": {"name": "Tanvi Bhatt",      "roll": "S2414", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 78, "Probablity and Statistics": 82, "Design and Analysis of Algorithms": 75, "Machine Learning": 84, "Design Thinking": 79, "Database Management System": 86}},
    "S2415": {"name": "Harsh Tiwari",     "roll": "S2415", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 53, "Probablity and Statistics": 58, "Design and Analysis of Algorithms": 47, "Machine Learning": 55, "Design Thinking": 61, "Database Management System": 50}},
    "S2416": {"name": "Meera Pillai",     "roll": "S2416", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 86, "Probablity and Statistics": 90, "Design and Analysis of Algorithms": 83, "Machine Learning": 87, "Design Thinking": 91, "Database Management System": 85}},
    "S2417": {"name": "Nikhil Rao",       "roll": "S2417", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 70, "Probablity and Statistics": 65, "Design and Analysis of Algorithms": 73, "Machine Learning": 68, "Design Thinking": 76, "Database Management System": 71}},
    "S2418": {"name": "Kavya Menon",      "roll": "S2418", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 92, "Probablity and Statistics": 88, "Design and Analysis of Algorithms": 96, "Machine Learning": 90, "Design Thinking": 87, "Database Management System": 93}},
    "S2419": {"name": "Aditya Jain",      "roll": "S2419", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 64, "Probablity and Statistics": 71, "Design and Analysis of Algorithms": 67, "Machine Learning": 73, "Design Thinking": 69, "Database Management System": 66}},
    "S2420": {"name": "Shruti Gupta",     "roll": "S2420", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 80, "Probablity and Statistics": 77, "Design and Analysis of Algorithms": 84, "Machine Learning": 78, "Design Thinking": 82, "Database Management System": 79}},
    "S2421": {"name": "Vivek Chandra",    "roll": "S2421", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 57, "Probablity and Statistics": 62, "Design and Analysis of Algorithms": 54, "Machine Learning": 60, "Design Thinking": 58, "Database Management System": 63}},
    "S2422": {"name": "Isha Saxena",      "roll": "S2422", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 89, "Probablity and Statistics": 84, "Design and Analysis of Algorithms": 87, "Machine Learning": 92, "Design Thinking": 86, "Database Management System": 90}},
    "S2423": {"name": "Manish Dubey",     "roll": "S2423", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 66, "Probablity and Statistics": 60, "Design and Analysis of Algorithms": 69, "Machine Learning": 64, "Design Thinking": 72, "Database Management System": 67}},
    "S2424": {"name": "Ritika Bose",      "roll": "S2424", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 77, "Probablity and Statistics": 81, "Design and Analysis of Algorithms": 79, "Machine Learning": 75, "Design Thinking": 83, "Database Management System": 76}},
    "S2425": {"name": "Suresh Nambiar",   "roll": "S2425", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 48, "Probablity and Statistics": 53, "Design and Analysis of Algorithms": 45, "Machine Learning": 51, "Design Thinking": 56, "Database Management System": 49}},
    "S2426": {"name": "Deepa Krishnan",   "roll": "S2426", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 93, "Probablity and Statistics": 89, "Design and Analysis of Algorithms": 91, "Machine Learning": 95, "Design Thinking": 88, "Database Management System": 92}},
    "S2427": {"name": "Gaurav Shukla",    "roll": "S2427", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 72, "Probablity and Statistics": 67, "Design and Analysis of Algorithms": 76, "Machine Learning": 70, "Design Thinking": 65, "Database Management System": 73}},
    "S2428": {"name": "Poonam Thakur",    "roll": "S2428", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 85, "Probablity and Statistics": 78, "Design and Analysis of Algorithms": 82, "Machine Learning": 86, "Design Thinking": 80, "Database Management System": 84}},
    "S2429": {"name": "Rahul Pandey",     "roll": "S2429", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 61, "Probablity and Statistics": 66, "Design and Analysis of Algorithms": 63, "Machine Learning": 58, "Design Thinking": 67, "Database Management System": 64}},
    "S2430": {"name": "Swati Malhotra",   "roll": "S2430", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 87, "Probablity and Statistics": 92, "Design and Analysis of Algorithms": 85, "Machine Learning": 88, "Design Thinking": 94, "Database Management System": 89}},
    "S2431": {"name": "Abhishek Das",     "roll": "S2431", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 69, "Probablity and Statistics": 74, "Design and Analysis of Algorithms": 71, "Machine Learning": 77, "Design Thinking": 63, "Database Management System": 70}},
    "S2432": {"name": "Neha Agarwal",     "roll": "S2432", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 82, "Probablity and Statistics": 85, "Design and Analysis of Algorithms": 88, "Machine Learning": 81, "Design Thinking": 84, "Database Management System": 87}},
    "S2433": {"name": "Siddharth Roy",    "roll": "S2433", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 56, "Probablity and Statistics": 50, "Design and Analysis of Algorithms": 59, "Machine Learning": 54, "Design Thinking": 62, "Database Management System": 57}},
    "S2434": {"name": "Ananya Chatterjee","roll": "S2434", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 94, "Probablity and Statistics": 91, "Design and Analysis of Algorithms": 97, "Machine Learning": 93, "Design Thinking": 90, "Database Management System": 95}},
    "S2435": {"name": "Pranav Hegde",     "roll": "S2435", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 75, "Probablity and Statistics": 69, "Design and Analysis of Algorithms": 72, "Machine Learning": 78, "Design Thinking": 68, "Database Management System": 74}},
    "S2436": {"name": "Simran Kaur",      "roll": "S2436", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 81, "Probablity and Statistics": 86, "Design and Analysis of Algorithms": 78, "Machine Learning": 83, "Design Thinking": 88, "Database Management System": 80}},
    "S2437": {"name": "Tarun Bajaj",      "roll": "S2437", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 63, "Probablity and Statistics": 68, "Design and Analysis of Algorithms": 60, "Machine Learning": 66, "Design Thinking": 71, "Database Management System": 65}},
    "S2438": {"name": "Varsha Nair",      "roll": "S2438", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 88, "Probablity and Statistics": 83, "Design and Analysis of Algorithms": 91, "Machine Learning": 86, "Design Thinking": 85, "Database Management System": 89}},
    "S2439": {"name": "Yash Patil",       "roll": "S2439", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 52, "Probablity and Statistics": 57, "Design and Analysis of Algorithms": 49, "Machine Learning": 55, "Design Thinking": 60, "Database Management System": 53}},
    "S2440": {"name": "Zara Sheikh",      "roll": "S2440", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 79, "Probablity and Statistics": 84, "Design and Analysis of Algorithms": 76, "Machine Learning": 81, "Design Thinking": 87, "Database Management System": 82}},
    "S2441": {"name": "Akash Tripathi",   "roll": "S2441", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 68, "Probablity and Statistics": 63, "Design and Analysis of Algorithms": 71, "Machine Learning": 67, "Design Thinking": 75, "Database Management System": 69}},
    "S2442": {"name": "Bhavna Joshi",     "roll": "S2442", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 96, "Probablity and Statistics": 93, "Design and Analysis of Algorithms": 89, "Machine Learning": 97, "Design Thinking": 92, "Database Management System": 94}},
    "S2443": {"name": "Chirag Vora",      "roll": "S2443", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 73, "Probablity and Statistics": 78, "Design and Analysis of Algorithms": 70, "Machine Learning": 76, "Design Thinking": 64, "Database Management System": 75}},
    "S2444": {"name": "Disha Kapoor",     "roll": "S2444", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 84, "Probablity and Statistics": 80, "Design and Analysis of Algorithms": 87, "Machine Learning": 83, "Design Thinking": 89, "Database Management System": 86}},
    "S2445": {"name": "Ekta Srivastava",  "roll": "S2445", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 58, "Probablity and Statistics": 54, "Design and Analysis of Algorithms": 62, "Machine Learning": 59, "Design Thinking": 65, "Database Management System": 61}},
    "S2446": {"name": "Farhan Ansari",    "roll": "S2446", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 77, "Probablity and Statistics": 73, "Design and Analysis of Algorithms": 80, "Machine Learning": 74, "Design Thinking": 78, "Database Management System": 76}},
    "S2447": {"name": "Gargi Banerjee",   "roll": "S2447", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 65, "Probablity and Statistics": 70, "Design and Analysis of Algorithms": 67, "Machine Learning": 72, "Design Thinking": 61, "Database Management System": 68}},
    "S2448": {"name": "Hemant Solanki",   "roll": "S2448", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 90, "Probablity and Statistics": 87, "Design and Analysis of Algorithms": 84, "Machine Learning": 91, "Design Thinking": 88, "Database Management System": 92}},
    "S2449": {"name": "Ishita Mathur",    "roll": "S2449", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 71, "Probablity and Statistics": 76, "Design and Analysis of Algorithms": 74, "Machine Learning": 69, "Design Thinking": 79, "Database Management System": 73}},
    "S2450": {"name": "Jayesh Pawar",     "roll": "S2450", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 83, "Probablity and Statistics": 88, "Design and Analysis of Algorithms": 81, "Machine Learning": 85, "Design Thinking": 90, "Database Management System": 84}},
}

def get_grade(marks):
    if marks >= 90: return "O", "Outstanding"
    elif marks >= 80: return "A+", "Excellent"
    elif marks >= 70: return "A", "Very Good"
    elif marks >= 60: return "B+", "Good"
    elif marks >= 50: return "B", "Average"
    else: return "F", "Fail"

def get_result_summary(subjects):
    total = sum(subjects.values())
    avg = total / len(subjects)
    passed = all(m >= 40 for m in subjects.values())
    grade, _ = get_grade(avg)
    return {
        "total": total,
        "avg": round(avg, 2),
        "passed": passed,
        "grade": grade,
        "percentage": round(avg, 2)
    }

@app.route('/')
def index():
    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template('index.html', container_id=container_id, timestamp=now)

@app.route('/result', methods=['POST'])
def get_result():
    roll = request.form.get('roll_number', '').strip().upper()
    student = students_db.get(roll)
    if not student:
        return render_template('index.html', 
                               error="No student found with Roll Number: " + roll,
                               container_id=socket.gethostname(),
                               timestamp=datetime.datetime.now().strftime("%d %B %Y, %I:%M %p"))
    
    subjects_with_grades = {}
    for sub, marks in student['subjects'].items():
        grade, label = get_grade(marks)
        subjects_with_grades[sub] = {"marks": marks, "grade": grade, "label": label}
    
    summary = get_result_summary(student['subjects'])
    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    
    return render_template('result.html', 
                           student=student, 
                           subjects=subjects_with_grades,
                           summary=summary,
                           container_id=container_id,
                           timestamp=now)

@app.route('/api/stats')
def stats():
    return jsonify({
        "container_id": socket.gethostname(),
        "uptime": "Running",
        "active_requests": random.randint(1, 50),
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
