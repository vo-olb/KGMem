# Memory Management Assistant Based on Knowledge Graph

This project is a **Memory Management Assistant** designed to help researchers and professionals organize, retrieve, and visualize complex information efficiently. The project leverages **Microsoft’s GraphRAG** to extract entities and relationships for constructing a knowledge graph and querying stored knowledge.

## Features

### Core Functionalities
- **Add Knowledge**:
  - Add knowledge through manual input, file upload (TXT/PDF), or raw material processing.
  - Microsoft’s [GraphRAG](https://github.com/microsoft/graphrag) is used to extract entities and their relationships to construct a knowledge graph.
- **Query Knowledge**:
  - Query stored knowledge using Microsoft’s GraphRAG’s functionality, along with contextual LLM reasoning and optional internet-based queries.
- **Visualize Knowledge**:
  - Visualize knowledge graphs using [GraphRAG Visualizer](https://github.com/noworneverev/graphrag-visualizer).
  - Explore relationships and gain insights through an intuitive interface.
- **Manage Memory**:
  - Create, delete, rename, and edit memory files with full user control.
  - Data is stored in GraphRAG-compatible formats for structured knowledge management.

### Frontend:
- An intuitive, responsive interface built with React allows users to add, query, and visualize knowledge seamlessly.

### Backend
- Built with Flask to handle requests, manage data, and integrate with GraphRAG. Supports LLM-based summarization and processing using OpenAI GPT.

## Setup

### Prerequisites
- Python (tested on 3.12)
- Node.js and npm
- Git

### Installation
1. Clone the repository or spin it in GitHub Codespaces:
   ```bash
   git clone https://github.com/vo-olb/KGMem.git
   cd KGMem-main
   ```
2. Ensure the parent folder of this project is accessible (this is where the `graphrag-visualizer` folder will be cloned and built).
3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Start the server:
   ```
   python server.py
   ```
   - This command will prepare the project, including running ``npm install``, ``npm run build``, and other necessary setup steps.

### Access
Once the server is running, open your browser and navigate to:
```
http://127.0.0.1:5000
```
The homepage includes instructions for using the assistant.

## Future Improvements

### Cloud Deployment:
- Use Docker for containerized deployment.
- Implement user login and authentication.
- Enhance multi-user support with Redis for caching and task queues.

### Optimization:
- Optimize GraphRAG calling parameters for quicker responses.
- Support asynchronous task handling with tools like Celery and Redis.

## Contributions
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the [MIT License](https://mit-license.org/).