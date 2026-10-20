# VayuTwin: AI-Enabled Real-Time Digital Twin System
**Smart India Hackathon 2026 | Problem Statement ID: SIH26054**  
**Team Name:** StrawHat Devs | **Team ID:** 121090  
**Theme:** Robotics and Drones (Software)

---

## 🔒 Repository Access & Intellectual Property Notice

In accordance with institutional mentorship guidelines and defense software security protocols, the source code, trained machine learning weights, and simulation pipelines for **VayuTwin** are currently maintained in a **private staging environment** to prevent unauthorized public distribution.

**For SIH Evaluators & Jury Members:**
Full repository access, complete source code, and containerized deployment packages will be provided **immediately upon request** during or prior to evaluation rounds. Please reach out to our team lead or use the official hackathon communication channels to request instant collaborator access or a private repository archive.

---

## 🎥 Live Working Proof & Official Submission Links

While the codebase remains restricted on this public branch, the complete working system, live telemetry simulator, architecture breakdown, and real-time fault injection tests can be verified through our official submission links below:

1. **Live Prototype Demonstration Video (Working UI, SPASHT AI & T.A.R.S. Overrides):**  
   https://www.youtube.com/watch?v=8gtB4oF_qm0

2. **SIH 2026 Pitch Presentation & Architecture Deep Dive Video:**  
   https://www.youtube.com/watch?v=8_dZ6AqdoOY

3. **Technical Documentation & Research Paper:**  
   https://docs.google.com/document/d/1NE56zXk8YTGuQzuojAroGmx_NxRrF6Aj/edit?usp=sharing

4. **Official Team Portfolio Website (StrawHat Devs):**  
   https://strawhat-devs-eight.vercel.app/

5. **GitHub Repository:**  
   https://github.com/silentronin456-ui/THE-VAYU-TWIN

---

## ⚙️ System Overview

**VayuTwin** is a 100% indigenous, AI-enabled Digital Twin platform that creates a real-time, physics-based virtual replica of aero piston engines (modeled on the Rotax 915 iS) used in Medium-Altitude Long-Endurance (MALE) UAVs.

### Core Architectural Pillars:
* **Suraksha (Edge Data Ingestion):** Ingests raw ECU/FADEC telemetry at 1 Hz via CAN Bus / SocketCAN protocols, applying real-time data validation and electromagnetic noise filtering.
* **Spasht AI (Predictive Diagnostics):** Built on the proprietary **PIOSSE** (Physics-Informed Operational State & Safety Estimator) framework using XGBoost and ONNX Runtime to evaluate 56 telemetry parameters, diagnose root causes, and compute Remaining Useful Life (RUL).
* **Pratham Module (Intelligent Triage):** Cross-verifies redundant sensor streams to eliminate false alarms and prioritize critical degradation alerts on the operator dashboard.
* **T.A.R.S. (Tactical Autonomous Reflex System):** A zero-latency, deterministic safety watchdog that enforces hardcoded physical engine limits and bypasses AI inference delays during critical failures.
* **Sanjeevani Protocol (Emergency Advisory):** Translates complex failure states into actionable, plain-English directives and triggers emergency Return-To-Base (RTB) procedures.
* **Smriti Sync (Blackout Memory):** Caches high-frequency telemetry locally during communication blackouts and electronic jamming, auto-syncing gapless logs the exact second connection is restored to guarantee zero data loss.
* **Mission Replay & Maintenance Center:** Reconstructs complete historical flights in 3D overlaid with environmental and weather parameters for post-mission debriefs, while maintaining centralized lifecycle logs of faults, inspections, repairs, and automated maintenance checklists for ground crews.

---

## 🛠️ Technology Stack

* **Frontend & 3D Visualization:** React.js, TypeScript, Tailwind CSS, Three.js / React Three Fiber
* **Backend & Telemetry Transport:** Python, FastAPI, Asynchronous WebSockets (WSS)
* **AI & Inference Engine:** XGBoost, PyTorch, Scikit-Learn, ONNX Runtime
* **Database & Time-Series Storage:** PostgreSQL, TimescaleDB

---

## 👥 Team StrawHat Devs

* **Aditya Parab** – Team Lead & Developer
* **Krishav Maurya** – Research Lead & Developer
* **Gehana Manvani** – Team Manager & Designer
* **Atharva Jaiswal** – Developer & Tester
* **Bhupesh Patil** – Developer & Tester
* **Atharva Gaikwad** – Developer

*For immediate source code access or technical inquiries, please contact Team StrawHat Devs at: **strawhat.devs.2026@gmail.com***
