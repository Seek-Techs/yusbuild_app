# 🤝 Contributing to YusBuild

Thank you for your interest in contributing to YusBuild 🚀  
This project aims to transform pile engineering workflows from manual Excel processes into a structured, automated system.

---

## 🧠 Project Philosophy

YusBuild is built on three core principles:

- **Clarity over complexity** → Code must be easy to understand
- **Single source of truth** → No duplicated models or logic
- **Separation of concerns** → UI, logic, and data must remain independent

---

## 🏗️ Project Structure
yusbuild/
├── piling/ # UI + form workflow (Django templates)
├── piles/ # Calculation engine + business logic
│ └── services/
│ └── calculations.py


### Responsibilities

| Component | Responsibility |
|----------|----------------|
| `piling` | Handles forms, templates, and user interaction |
| `piles`  | Handles engineering calculations and logic |

---

## 📌 Contribution Areas

We welcome contributions in the following areas:

### 🔧 Backend (Django)
- Improve model structure
- API development (Django REST Framework)
- Data validation and workflow optimization

### 🧮 Engineering Logic
- Reinforcement calculations (A/B/C/D bars)
- Lap length and stock handling
- Helix and stiffener computation
- BOQ (Bill of Quantities) generation

### 🎨 Frontend
- UI/UX improvements
- React dashboard (future phase)

### 📄 Documentation
- Improve README
- Add technical guides
- Write usage examples

---

## ⚠️ Contribution Rules (IMPORTANT)

### 1. Do NOT duplicate models
There must only be **one Pile model** in the system.

### 2. Keep calculations centralized
All engineering logic must go here:
piles/services/calculations.py

Do NOT put calculations in:
- views
- forms
- templates

---

### 3. Keep code clean and readable
- Use meaningful variable names
- Avoid unnecessary complexity
- Add comments where needed

---

### 4. Maintain consistency with existing logic
Before adding new logic:
- Understand current flow
- Avoid breaking existing features

---

## 🔄 Development Workflow

### 1. Fork the repository

### 2. Create a feature branch
git checkout -b feature/your-feature-name


---

### 3. Make your changes

Keep commits small and focused.

---

### 4. Commit using proper format

type(scope): message

#### Examples:
feat(engine): implement reinforcement bar calculation logic

fix(piling): resolve form validation error

refactor(models): unify pile model usage across apps

docs(readme): improve project documentation


---

### 5. Push and create a Pull Request

Explain:
- What you did
- Why you did it
- What problem it solves

---

## 🧪 Testing Guidelines

Before submitting:

- Run the server and test your changes
- Ensure no existing functionality is broken
- Validate calculations with sample data

---

## 🎯 Current Priority Tasks

We are actively looking for help in:

- Full reinforcement logic implementation
- Lap and stock length handling
- Helix + stiffener calculations
- BOQ generation system
- API standardization (DRF)

---

## 💬 Communication

Be clear and direct when:
- Asking questions
- Reviewing code
- Suggesting improvements

---

## 🚀 Final Note

This project is not just a coding exercise.  
It is an attempt to build a **real engineering tool**.

Contribute with that mindset.

---

Thanks for building with us 💪