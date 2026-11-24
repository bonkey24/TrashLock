# 🔐 TrashLock

**TrashLock** is an educational face-recognition login system, presentation attack benchmarking tool, and biometric security prototype built with **Streamlit** and **facenet-pytorch** for the project _"TrashLock: Your Body as a Password"_.

## What it does

| Page | Description |
|---|---|
| **👤 Enrol** | Register participants by capturing 3–5 face photos, computing a 512-d Facenet template, and storing it in SQLite alongside a salted SHA-256 PIN hash. Displays enrolled participants with individual delete actions. |
| **🛡️ Login** | Capture live webcam photos, compare against enrolled templates using cosine distance, and grant/deny access based on the threshold slider. Features 2FA PIN verification and large status badges. |
| **📊 Analysis** | Benchmark False Accept Rate (FAR), False Reject Rate (FRR), and Equal Error Rate (EER) across genuine and impostor face pairs from a public benchmark (LFW). |
| **📋 Test Log** | Record experimental verification scenarios (spoof tests, lighting, accessories, wrong PIN) with Pass/Fail badges, SQLite persistence, and one-click CSV export. |
| **ℹ️ About** | Student-friendly explanations of biometric principles (templates, cosine distance, FAR/FRR/EER trade-offs) and critical risks (spoofing, permanence, demographic bias, and 2FA). |

> **Privacy Guarantee:** Only 512-dimensional numeric embeddings are stored in SQLite — photos are processed in-memory and **never** saved to disk.

---

## Setup (Windows)

### 1. Prerequisites
- **Python 3.10+** (tested on Python 3.12)
- Web camera (for Enrol and Login live capture)

### 2. Create a Virtual Environment

Open PowerShell in the `biometric-prototype` directory:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the Application

```powershell
streamlit run app.py
```

The web application opens automatically at `http://localhost:8501`.

---

## Testing Checklist

Use this checklist to verify every feature and page before presentations:

- [ ] **1. Enrol Page**:
  - [ ] Attempt saving with an empty name $\rightarrow$ verify friendly warning appears.
  - [ ] Capture 3–5 webcam shots (verify photo progress counter increments).
  - [ ] Enter a name (e.g. `Maya Patel`) and 4-digit PIN (e.g. `4829`) $\rightarrow$ click **Save enrolment**.
  - [ ] Check that `Maya Patel` appears in the **Enrolled participants** list.
  - [ ] Attempt enrolling a duplicate name $\rightarrow$ verify duplicate name error prevents overwriting.
  - [ ] Test individual user deletion using the **Delete** button next to an enrolled name.
  - [ ] Test **Delete all users** for quick demo resets.

- [ ] **2. Login Page**:
  - [ ] With no users enrolled $\rightarrow$ verify friendly warning instructs enrolling first.
  - [ ] With an enrolled user, capture your face $\rightarrow$ verify cosine distance, similarity %, and decision rule.
  - [ ] If distance $<$ threshold $\rightarrow$ verify large green **`Access granted`** badge and balloons.
  - [ ] Adjust the sidebar **Match threshold** slider stricter (e.g. `0.20`) or more lenient (e.g. `0.55`) $\rightarrow$ observe instant change in the access decision.
  - [ ] Toggle **Require PIN** in the header $\rightarrow$ verify face match prompts for PIN, and only correct salted hash grants access.

- [ ] **3. Analysis Page**:
  - [ ] Navigate to Analysis before loading data $\rightarrow$ verify informative prompt with no exceptions.
  - [ ] Click **Load LFW sample** $\rightarrow$ watch progress bar extract 512-d embeddings across benchmark faces.
  - [ ] Verify the 3 top summary metric cards (`People`, `Genuine pairs`, `Impostor pairs`).
  - [ ] Check Chart 1: FAR and FRR curves intersecting at the marked **EER point**.
  - [ ] Check Chart 2: Genuine vs. Impostor distance distribution histograms.
  - [ ] Adjust sidebar threshold slider $\rightarrow$ observe vertical dashed line update on both charts in real time.
  - [ ] Review performance table comparing active threshold metrics against optimal EER.

- [ ] **4. Test Log Page**:
  - [ ] Review default experimental scenarios (e.g., front desk lighting, glasses, wrong PIN).
  - [ ] Use **Add row** with dropdown suggestions (e.g. `Phone photo (screen replay)`, `Printed photo`, `Dim light`) $\rightarrow$ verify new row saves into SQLite with colored Pass/Fail badge.
  - [ ] Click **Download CSV** $\rightarrow$ verify CSV export downloads cleanly.
  - [ ] Click **Clear Test Log** $\rightarrow$ verify logs reset.

- [ ] **5. About Page**:
  - [ ] Read through core concepts (Enrolment, Template, Cosine Distance, Threshold, FAR, FRR, EER).
  - [ ] Review presentation attack vulnerabilities, permanence risks, and privacy architecture.

---

## Project Structure

```
biometric-prototype/
├── app.py             # Streamlit app (sidebar routing for Enrol, Login, Analysis, Test Log, About)
├── ui.py              # Stitch design system CSS, card helpers, badges, and figure stylers
├── face_utils.py      # facenet-pytorch (MTCNN + InceptionResnetV1) 512-d embeddings and cosine distance
├── db.py              # SQLite storage for users and test_logs tables
├── requirements.txt   # Pinned dependency versions
├── README.md          # Setup, test checklist, and presentation guide
├── lfw_data/          # Local LFW benchmark dataset
└── users.db           # SQLite database (created automatically)
```

---

## Tech Stack

| Component | Role |
|---|---|
| **Streamlit** | Interactive wide web UI, webcam input, and data caching (`@st.cache_data`) |
| **facenet-pytorch (InceptionResnetV1)** | 512-dimensional facial feature representation (pretrained on VGGFace2) |
| **MTCNN** | Deep learning face detection and alignment |
| **NumPy & SciPy** | Cosine distance, error curves, and distribution metrics |
| **scikit-learn** | LFW benchmark dataset loader (`fetch_lfw_people`) |
| **Matplotlib** | Styled FAR/FRR tradeoff curves and distance distribution histograms |
| **SQLite (sqlite3)** | Local database for users and test_logs |
| **hashlib (SHA-256)** | Salted cryptographic hashing for user PINs |
