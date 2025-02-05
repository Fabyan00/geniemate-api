# GenieMate API

## Getting Started
1. Clone the repository
```zsh
git clone https://github.com/Fabyan00/geniemate-api.git
cd geniemate-api
```
2. Set up a virtual environment
```zsh
python3 -m venv .venv
source .venv/bin/activate (Linux/Mac)
.venv\Scripts\activate (Windows)
```
3. Install dependencies
```zsh
pip install -r requirements.txt
```
4. Set OpenAI Key in a .env file
```zsh
OPENAI_API_KEY = "YOUR API KEY"
```
5. Run the application
```zsh
uvicorn app.main:app
```
Open [http://localhost:8000](http://localhost:8000) with your browser and see the result.

Open API docs [http://localhost:8000/docs](http://localhost:8000/docs)

API routes can be accessed on [http://localhost:8000/api/resume](http://localhost:8000/api/resume). This endpoint returns text resumes.