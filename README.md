# Prerequisites: 
1. Docker and Docker Compose installed on your system
2. Git for cloning the repo


# Setup Instructions:
1. Clone the repo: 
    ```bash
    git clone https://github.com/cf-stormtroopers/week2-imgGallery.git
    cd week2-imgGallery
    ```

2. Create a .env file as in the example:
    ```bash
    cp .env.example .env
    ```

3. Build and run the containers:
    ```bash
    docker compose up -d
    ```

🌩️ SnapStorm

Team Stormtrooper presents SnapStorm – a modernized photo gallery powered by AI search and sleek UI.

✨ Features

📸 Photo Uploads

Add photos with title, caption, alt text, license, attribution, and privacy settings.

Drag & drop or click-to-upload.

🖼️ Albums & Collections

Organize photos into albums and collections.

🔍 AI-powered Search

Vector-based AI search bar to quickly find photos.

🔦 Lightbox Viewer

View photos in full with navigation (Next / Previous) and a Download option.

⚙️ User & Site Settings

Manage site name and global settings.

User roles: Admin (full control) and Editor (limited).

Add, edit, or delete users.

🔑 Authentication

Login and profile management.

🛠️ Tech Stack

Frontend: React + TypeScript + Vite

Styling: TailwindCSS

API Handling: Axios + OpenAPI (Orval)

Vector Search: AI similarity search

State Management: React state

Containerization: Docker

Linting: ESLint + Prettier

📂 Project Structure
frontend/
 ├── public/                # Static assets
 ├── src/
 │   ├── api/               # API calls (axios + generated client)
 │   ├── assets/            # Static icons (e.g., react.svg)
 │   ├── components/        # Reusable UI components
 │   ├── pages/             # Main pages (Home, Albums, Lightbox, Profile, etc.)
 │   ├── state/             # State management
 │   ├── App.tsx            # Root component
 │   └── main.tsx           # Entry point
 ├── index.html             # Base HTML
 ├── vite.config.ts         # Vite config
 ├── tailwind.config.js     # Tailwind setup
 └── Dockerfile             # Container setup

🚀 Getting Started
1. Clone the repo
git clone https://github.com/<your-org>/snapstorm.git
cd snapstorm/frontend

2. Install dependencies
npm install

3. Start development server
npm run dev

Visit http://localhost:5173/

🐳 Run with Docker
docker build -t snapstorm .
docker run -p 3000:3000 snapstorm

📌 Roadmap
 Drag & drop photo reordering in albums
 AI-based photo search
 Create and view Albums

👥 Team Stormtrooper
Ranjith R Dixit
Anvitha Bhat A
Gauri Girish Dhanakshirur
Vishruth A