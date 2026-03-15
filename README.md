# 🎓 Student Result Portal — Docker Containerization Project

## 📁 Project Structure
```
student_result_portal/
├── app.py                  ← Flask backend (main server)
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Docker build instructions
├── docker-compose.yml      ← App + MySQL multi-container setup
└── templates/
    ├── login.html          ← Student login page
    ├── admin_login.html    ← Admin/faculty login page
    ├── change_password.html← First login password update page
    ├── index.html          ← Student dashboard
    ├── result.html         ← Student result page
    └── admin_dashboard.html← Admin credential management page
```

---

## 🖥️ WINDOWS — Step-by-Step Guide

### Step 1: Install Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Install it (enable WSL 2 when asked) → Restart your PC
4. Open Docker Desktop and wait until it says **"Engine Running"**

### Step 2: Open Terminal in Your Project Folder
1. Copy your `student_result_portal` folder to Desktop
2. Open **Command Prompt** or **PowerShell**
3. Navigate to the folder:
```cmd
cd Desktop\student_result_portal
```
> TIP: Type `cd ` then drag the folder into CMD — it auto-fills the path!

### Step 3: Start App + MySQL with Docker Compose
```cmd
docker compose up --build -d
```
> This starts both containers: Flask app and MySQL database.

### Step 5: Open in Browser
Open Chrome/Edge → go to: **http://localhost:5000**

You should see the Student Login page first.

Student initial login credentials:
- Roll Number: `S2401` to `S2450`
- Initial password format: `<roll number in lowercase>@vu2026`
- Example: Roll `S2401` -> Password `s2401@vu2026`

After first login, each student is forced to set a private password.

Admin login:
- URL: `http://localhost:5000/admin/login`
- Default username: `admin`
- Default password: `Admin@12345`

After login, student can open only their own result dashboard. Admin can search all students and reset student passwords.

### Step 6: Useful Commands
```cmd
docker ps                          ← Check if container is running
docker stats student_result_portal student_result_mysql     ← Live CPU/RAM usage
docker logs student_result_portal  ← See app logs
docker logs student_result_mysql   ← See database logs
docker compose down                ← Stop all services
docker compose up -d               ← Start all services again
```

---

## 🐧 LINUX — Step-by-Step Guide

### Method A: Transfer via .tar file (USB / Google Drive)

**On Windows — Export the image:**
```cmd
docker save -o result_portal.tar result-portal-image
```
This creates a file `result_portal.tar` in your folder. Transfer it to Linux.

**On Linux — Load and Run:**
```bash
sudo docker load -i result_portal.tar
sudo docker compose up --build -d
```
Open browser → **http://localhost:5000**

### Method B: Copy files and rebuild on Linux (Recommended)

**On Linux — Install Docker:**
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
```

**Navigate to project folder and build:**
```bash
cd student_result_portal
sudo docker compose up --build -d
```

---

## 🔢 Demo Roll Numbers
| Roll Number | Student Name       | Branch           |
|-------------|--------------------|------------------|
| S2401       | Aarav Sharma       | Computer Science |
| S2402       | Priya Patel        | Computer Science |
| S2403       | Rohit Verma        | Information Tech |
| S2404       | Sneha Joshi (Topper) | Computer Science |
| S2405       | Karan Mehta        | Electronics      |
| S2406       | Anjali Singh       | Information Tech |
| S2407       | Vikram Nair        | Computer Science |
| S2408       | Divya Reddy        | Computer Science |

---

## 📊 For PPT — Show docker stats Live
While presenting, open a new terminal and run:
```cmd
docker stats student_result_portal student_result_mysql
```
This shows **live memory & CPU usage** — very impressive to show professors!

---

## 🔐 Security Logic (How Credentials Stay Private)
1. Every student has an individual credential row in MySQL (`student_credentials` table) identified by roll number.
2. Passwords are never saved as plain text; they are stored as one-way hashes (`generate_password_hash`).
3. During login, the app compares entered password with hash using `check_password_hash`.
4. Student sessions are role-based (`auth_role=student`) and tied to a single roll number, so student can only open own result.
5. Admin sessions are separate (`auth_role=admin`) and can access only admin routes.
6. Admin can reset a student password, but still cannot recover the old plain-text password from hash.
7. On first login/reset, `must_change_password=true` forces student to set a secret password known only to that student.

---

## 🛑 Cleanup Commands
```cmd
docker compose down -v             ← Stop containers and remove DB volume
```
