
---

# 🚀 AI-Assisted Document Authoring & Generation Platform

An end-to-end full-stack platform built with **FastAPI**, **React (Vite)**, and **MySQL**, designed for generating, refining, editing, and exporting structured documents using AI (Gemini API).

Users can:
✔ Register / Login
✔ Create projects
✔ Add sections/slides
✔ Auto-generate content using LLM
✔ Refine sections with prompts
✔ Add feedback & comments
✔ Export DOCX / PPTX

Fully deployed using:

* **Backend:** FastAPI on Render
* **Frontend:** React (Vercel)
* **Database:** MySQL (Railway)
* **AI Engine:** Gemini 1.5 Flash API

---

## 🌐 Live Links

### 🔹 Frontend (Vercel)

👉 **[https://ai-doc-2kvz.vercel.app/](https://ai-doc-2kvz.vercel.app/)**

### 🔹 Backend (Render)

👉 **[https://ai-doc-ss1m.onrender.com](https://ai-doc-ss1m.onrender.com)**

### 🔹 API Docs (Swagger UI)

👉 **[https://ai-doc-ss1m.onrender.com/docs](https://ai-doc-ss1m.onrender.com/docs)**

---

## 🏗️ Tech Stack

### **Frontend**

* React + Vite
* Fetch / Axios for API calls
* Environment variables through `VITE_API_URL`

### **Backend**

* FastAPI
* SQLAlchemy ORM
* JWT Authentication
* LLM integration (Gemini API)
* DOCX generation (python-docx)
* PPTX generation (python-pptx)

### **Database**

* MySQL (Railway Cloud)

### **Deployment**

* Render (Backend)
* Vercel (Frontend)

---

## 📁 Project Structure

```
ai-doc-platform/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── llm.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── docx_export.py
│   │   └── pptx_export.py
│   ├── requirements.txt
│   └── .env (NOT committed)
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── styles
    ├── vite.config.js
    ├── package.json
    └── .env
```

---

## 🔑 Environment Variables

### **Backend (.env)**

```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

DATABASE_URL=mysql+mysqlconnector://root:password@host:port/railway

LLM_API_KEY=your_gemini_api_key
LLM_API_URL=https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent
```

### **Frontend (.env)**

```
VITE_API_URL=https://ai-doc-ss1m.onrender.com
```

---

## 🚀 Deployment Instructions

### **Backend (Render)**

1. Push backend to GitHub
2. Create a Render Web Service
3. Root directory: `backend`
4. Build command:

```
pip install -r requirements.txt
```

5. Start command:

```
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

6. Add environment variables
7. Deploy

---

### **Frontend (Vercel)**

1. Push frontend to GitHub
2. Import project into Vercel
3. Root directory: `frontend`
4. Build command:

```
npm run build
```

5. Output directory:

```
dist
```

6. Add env variable:

```
VITE_API_URL=https://ai-doc-ss1m.onrender.com
```

---

## 🧠 Features Overview

### ✔ User Authentication

JWT-based authentication and session persistence.

### ✔ Project Management

Create, view, delete, and open document projects.

### ✔ AI Content Generation

Automatic content generation for each section using Gemini LLM.

### ✔ Section Refinement

Improve sections using custom user prompts.

### ✔ Feedback & Commenting

Save likes/dislikes and comments per section.

### ✔ Export Options

Download final document as:

* `.docx` (Word)
* `.pptx` (PowerPoint)

---

## 💻 Run Locally

### **Backend**

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### **Frontend**

```
cd frontend
npm install
npm run dev
```

---

## 🛠️ Future Improvements

* Real-time collaboration
* PDF export
* Spell checking
* GPT-style chat refinement
* Templates for different document types

---

## 📝 License

This project is for educational and development purposes.

---

<img width="1459" height="606" alt="image" src="https://github.com/user-attachments/assets/eae73e6a-1cdb-4baa-8709-1a8ce03b916f" />
<img width="1204" height="854" alt="image" src="https://github.com/user-attachments/assets/e3c2d016-4257-4981-a5c5-8edd071fed27" />




> ⚠️ **Important:** Do **NOT** put your real password/host/port in the public README. Use placeholders like `<RAILWAY_HOST>` etc. Your `.env` file should keep the real secrets.

---

## 🔌 Connecting to Railway MySQL with MySQL Workbench

You can inspect and manage the production database (hosted on Railway) using **MySQL Workbench**.

### 1. Prerequisites

* MySQL Workbench installed

  * Download from the official MySQL site.
* Railway MySQL service already created.
* Database credentials from Railway:

  * **Host**
  * **Port**
  * **Username**
  * **Password**
  * **Database name** (e.g. `railway`)

> You can find these in Railway → your MySQL service → **Connect** / **Variables** section.

---

### 2. Create a new connection in MySQL Workbench

1. Open **MySQL Workbench**.

2. On the home screen, under **MySQL Connections**, click the **`+`** icon to add a new connection.

3. Fill in the connection details:

   * **Connection Name:**
     `Railway MySQL` (or any name you like)
   * **Connection Method:**
     `Standard (TCP/IP)`
   * **Hostname:**
     `<RAILWAY_HOST>`
     (example: `yamabiko.proxy.rlwy.net`)
   * **Port:**
     `<RAILWAY_PORT>`
     (example: `34087`)
   * **Username:**
     `<RAILWAY_USER>`
     (often `root` by default)
   * Click **Store in Vault…** next to *Password* and enter your Railway DB password.
   * (Optional) **Default Schema:**
     `<RAILWAY_DATABASE_NAME>`
     (example: `railway`)

4. Click **Test Connection**:

   * If prompted about SSL, click **OK/Continue**.
   * You should see a “Successfully made the MySQL connection” message.

5. Click **OK** to save the connection.

---

### 3. Open the connection and select the database

1. On the MySQL Workbench home screen, **double-click** the connection you just created (`Railway MySQL`).
2. After it opens:

   * On the **left sidebar (SCHEMAS panel)**, find your database (e.g. `railway`).
   * Right-click it and choose **Set as Default Schema**.

---

### 4. Running SQL queries (example: view & delete users)

1. Click the **“SQL +”** button (or `File → New Query Tab`) to open a new SQL editor tab.

2. Make sure your default schema is selected (shown above the editor, or in the SCHEMAS panel).

3. Now you can run queries like:

   ```sql
   -- See all tables
   SHOW TABLES;

   -- Select all users
   SELECT * FROM users;

   -- Delete a specific user (example: id = 3)
   DELETE FROM users
   WHERE id = 3;
   ```

4. Highlight the query (or keep cursor inside it) and click the **lightning bolt ▶️** button to execute.

> ⚠️ `DELETE` is permanent. Double-check the `WHERE` condition before running.

---

### 5. Mapping to backend configuration

In your backend, the database connection is configured via `DATABASE_URL` in `.env`, for example:

```env
DATABASE_URL=mysql+mysqlconnector://<RAILWAY_USER>:<RAILWAY_PASSWORD>@<RAILWAY_HOST>:<RAILWAY_PORT>/<RAILWAY_DATABASE_NAME>
```

This should match the same host, port, user, password, and database name you used in MySQL Workbench.

---


