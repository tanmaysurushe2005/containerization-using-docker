# 🎓 Student Result Portal — Docker Containerization Project

## 📁 Project Structure
```
student_result_portal/
├── app.py                  ← Flask backend (main server)
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Docker build instructions
├── docker-compose.yml      ← Easy one-command run
└── templates/
    ├── index.html          ← Homepage (search page)
    └── result.html         ← Result display page
```

---

## 🪟 WINDOWS — Step-by-Step Guide

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

### Step 3: Build the Docker Image
```cmd
docker build -t result-portal-image .
```
> Wait for it to finish (first time takes 1-2 minutes as it downloads Python)

### Step 4: Run the Container
```cmd
docker run -d -p 5000:5000 --name student_container result-portal-image
```

### Step 5: Open in Browser
Open Chrome/Edge → go to: **http://localhost:5000**

You should see the Student Result Portal! Try roll numbers: `S2401` to `S2408`

### Step 6: Useful Commands
```cmd
docker ps                          ← Check if container is running
docker stats student_container     ← Live CPU/RAM usage (great for PPT!)
docker logs student_container      ← See server activity
docker stop student_container      ← Stop the website
docker start student_container     ← Start it again
```

---

## 🐧 LINUX VM — Step-by-Step Guide

### Method A: Transfer via .tar file (USB / Google Drive)

**On Windows — Export the image:**
```cmd
docker save -o result_portal.tar result-portal-image
```
This creates a file `result_portal.tar` in your folder. Transfer it to Linux.

**On Linux — Load and Run:**
```bash
sudo docker load -i result_portal.tar
sudo docker run -d -p 8080:5000 --name student_portal result-portal-image
```
Open browser → **http://localhost:8080**

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
sudo docker build -t result-portal-image .
sudo docker run -d -p 5000:5000 --name student_container result-portal-image
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
docker stats student_container
```
This shows **live memory & CPU usage** — very impressive to show professors!

---

## 🛑 Cleanup Commands
```cmd
docker stop student_container      ← Stop container
docker rm student_container        ← Remove container
docker rmi result-portal-image     ← Remove image
```
