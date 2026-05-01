# Railway LCCA — Life Cycle Cost Analysis Tool

A premium Flask-based **Life Cycle Cost Analysis (LCCA)** engine designed for railway infrastructure evaluation. Originally developed for the **Karachi Circular Railway (KCR)** 44km track expansion, it now supports multiple infrastructure scenarios.

## 🚀 Key Features

- **Multi-Scenario Support**: 
  - **Scenario 1**: Concrete vs. Wooden Sleepers
  - **Scenario 2**: Weld vs. Fish Plate Joints
  - **Scenario 3**: Ballasted vs. Slab Track Systems
- **Interactive Dashboard**: Premium dark-themed UI with an animated, toggleable sidebar.
- **Dynamic LCCA Engine**: Supports both Legacy Scenario logic and Standard Analytical Engineering formulas.
- **Visual Analytics**: Real-time charts including Economic Comparison (Bar) and Annual Maintenance Flow (Line).
- **Financial Auditing**: Step-by-step breakdown of Initial Cost (IC), NPV Maintenance, and Replacement costs.
- **Responsive Design**: Optimized for desktop and tablets with horizontal scrolling for large data tables.

## 📁 Project Structure

```bash
railway_lcca/
├── app.py               # Flask entry point & routing
├── lcca_model.py        # Generic LCCA calculation engine
├── requirements.txt     # Project dependencies
├── static/
│   └── style.css        # Premium UI design system
└── templates/
    ├── landing.html     # Welcome landing page
    ├── index.html       # Scenario configuration form
    └── results.html     # Financial audit & visualization
```

## 🛠️ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/alayr78-oss/LCCA.git
cd LCCA/railway_lcca

# 2. Setup Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run Development Server
flask --app app run --debug
```

## 📈 Methodology

The tool uses standard financial engineering formulas to calculate the Net Present Value (NPV) of repeating maintenance and capital replacement cycles:

| Factor | Formula |
| :--- | :--- |
| **NPV (Annuity)** | $A \times \frac{1 - (1+r)^{-n}}{r}$ |
| **Replacement PV** | $\frac{RC}{(1+r)^t}$ |
| **Total LCC** | $IC + \text{NPV}_{\text{maint}} + \text{NPV}_{\text{repl}}$ |

---
*Built for Karachi Circular Railway Project Analytics.*
