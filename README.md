# YusBuild Construction Management Backend

This is the backend API for **YusBuild** — a construction site management platform for Nigerian construction teams. Built with:

- Django REST Framework (DRF)
- Token-based Authentication
- Role-based Access
- Task & Report Management
- Project-based filtering

## 🚀 Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/yusbuild-backend.git
cd yusbuild-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver
