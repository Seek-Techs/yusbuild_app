# YusBuild – Pile Engineering System

## 🚀 Overview
YusBuild is a construction-focused software platform designed to automate pile design, reinforcement detailing, and BOQ generation.

This module focuses on:
- Pile data capture (site workflow)
- Reinforcement calculation engine
- Future integration with BOQ and project dashboard

---

## 🧠 Problem Statement
Current pile design workflows rely heavily on Excel, leading to:
- Manual errors
- Inconsistent calculations
- Poor traceability

YusBuild aims to:
- Standardize calculations
- Automate reinforcement logic
- Provide real-time engineering outputs

---

## 🏗️ Architecture

Django Apps:

- `piling` → UI + data capture (forms, templates)
- `piles` → calculation engine (business logic)

Flow:

User Input → piling app → calculation engine → stored results

---

## ⚙️ Current Features

- Multi-step pile data capture
- Initial calculation engine (zoned vs full cage)
- Database persistence

---

## ⚠️ Current Limitations

- Reinforcement logic is simplified (placeholder)
- No BOQ yet
- No frontend (React) yet

---

## 🎯 Roadmap

- [ ] Full reinforcement logic (A/B/C/D bars)
- [ ] Lap + stock length handling
- [ ] Helix + stiffener calculation
- [ ] BOQ generation
- [ ] API exposure (DRF)
- [ ] React frontend integration

---

## 🛠️ Setup Instructions

```bash
git clone <repo>
cd yusbuild
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver