# LLM Code Architecture Visualizer

This project provides a web application that allows users to input a GitHub repository link and automatically generates architecture diagrams for the code project. Users can then continue chatting and asking questions about the codebase.

## Project Structure

The project consists of two main components:
- **llm-backend**: The backend implementation of the project (Python/FastAPI)
- **llm-frontend**: The frontend implementation of the project (Next.js)

## Screenshots

### Application Interface
![image](images/interface.png)
### Enter Github Link
![image](images/input.png)
### Architecture Diagram Example
![image](images/diagram.png)

## Setup and Installation

### Backend Setup (llm-backend)

1. Navigate to the backend directory:
   ```
   cd llm-backend
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

   Required packages:
   - fastapi
   - uvicorn
   - anthropic
   - python-dotenv
   - graphviz
   - requests
   - pydantic
   - gitpython

3. Configure your environment variables:
   - Add your API key to the `.env` file:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```

4. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup (llm-frontend)

1. Navigate to the frontend directory:
   ```
   cd llm-frontend
   ```

2. Install required dependencies:
   ```
   npm install
   ```

   Key dependencies:
   - next
   - react
   - react-dom
   - uuid
   - tailwindcss

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000` (or the port shown in your terminal)

## Usage

1. Enter a GitHub repository URL in the input field
2. The application will generate an architecture diagram for the repository
3. You can then ask questions about the codebase through the chat interface

