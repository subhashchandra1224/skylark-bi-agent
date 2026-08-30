<div align="center">
  <h1>🦅 Skylark BI Agent</h1>
  <p><strong>A deterministic, real-time AI Business Intelligence agent over live Monday.com operational data.</strong></p>

  <p>
    <a href="https://frontend-3o06y1dnq-subhash45.vercel.app"><img src="https://img.shields.io/badge/Live_Demo-frontend--3o06y1dnq--subhash45.vercel.app-10b981?style=for-the-badge&logo=vercel" alt="Live Demo" /></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  </p>
</div>

<hr />

## 🌟 Overview
Executive teams require immediate, cross-functional visibility into live operational metrics (Sales Deals and Engineering Work Orders). Traditional BI dashboards are static, and raw LLMs frequently hallucinate financial arithmetic.

**The Skylark BI Agent** bridges this gap by offering a natural language conversational interface that guarantees **100% deterministic mathematical accuracy**. It uses Google Gemini strictly for semantic intent parsing and executive interpretation, while relying entirely on Python and Pandas to execute authoritative calculations against live Monday.com GraphQL data.

---

## 🏗️ Architecture & Core Systems

```mermaid
graph TD
    A[User Question] --> B[React Frontend]
    B --> C[FastAPI Backend]
    C --> D[Gemini Intent Parsing]
    D --> E[Structured JSON Plan]
    E --> F[Monday.com GraphQL]
    F --> G[Data Normalization]
    G --> H[Pandas BI Engine]
    H --> I[Verified Metrics]
    I --> J[Gemini Executive Summary]
    J --> B
```

### 🔹 Deterministic BI Engine
**Gemini is blocked from doing math.** All aggregations, counts, groupings, and date-range filtering are deterministically calculated via `pandas` in Python. This ensures **0% hallucination** on financial metrics.

### 🔹 Dynamic Column Discovery
Rather than hardcoding fragile column IDs, the agent fetches board metadata to dynamically map normalized text titles (e.g., `"probable start date"`) to their live Monday.com internal hashes.

### 🔹 Robust Normalization & Date Parsing
Monday.com returns highly variable data types (strings, JSON, empty arrays) and non-standard timezone notations (e.g., `(Coordinated Universal Time)`). A strict normalization engine converts financial figures and strips breaking timezone strings to allow flawless timestamp casting.

### 🔹 Data Quality Transparency
Missing data is not silently ignored. If deals lack financial values, the agent flags this (e.g., *"Pipeline totals exclude 184 deals with missing values"*), maintaining absolute trust in the generated reports.

### 🔹 Cross-Board Analytics
Queries like *"Give me a leadership update"* automatically span multiple boards, pulling and analyzing live data from both the **Deals** pipeline and **Work Orders** execution tracking.

---

## 🚀 Live Demo
You can test the application live directly at the Vercel URL below:

👉 **[Live Frontend Application](https://frontend-3o06y1dnq-subhash45.vercel.app)**

### Example Questions to Try:
- *"How many deals do we have?"*
- *"What is our open pipeline value?"*
- *"Which work orders are starting soon?"*
- *"Give me a leadership update."*

---

## ⚙️ Local Setup & Execution

### 1️⃣ Environment Variables
Create a `.env` file in the `backend/` directory with the following keys:
```env
MONDAY_API_TOKEN=your_monday_token
MONDAY_DEALS_BOARD_ID=5030975323
MONDAY_WORK_ORDERS_BOARD_ID=5030975433
GEMINI_API_KEY=your_gemini_key
FRONTEND_URL=http://localhost:5173
```

### 2️⃣ Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3️⃣ Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

---

## 🚢 Deployment Details
The application is fully containerized and deployed across two platforms:

- **Backend (Render)**: 
  - **Root**: `backend`
  - **Build**: `pip install -r requirements.txt`
  - **Start**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- **Frontend (Vercel)**:
  - **Framework**: Vite (`npm run build`)
  - **Variables**: `VITE_API_URL` securely links to the Render instance.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
