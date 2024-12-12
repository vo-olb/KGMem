# Memory Management Assistant Based on Knowledge Graph

This project is a **Memory Management Assistant** designed to help researchers and professionals organize, retrieve, and visualize complex information efficiently. The project leverages Microsoft’s **GraphRAG** to extract entities and relationships for constructing a knowledge graph and querying stored knowledge. For video introduction, please refer to [this YouTube link](https://youtu.be/bEEVs-A-M48).

## Features

### Core Functionalities
- **Add Knowledge**:
  - Add knowledge through manual input, text or pdf file upload.
  - Microsoft’s [GraphRAG](https://github.com/microsoft/graphrag) is used to extract entities and their relationships to construct a knowledge graph. The focus of entity type or knowledge type can be chosen by user.
- **Query Knowledge**:
  - Query stored knowledge using Microsoft’s GraphRAG’s global/drift search methods, along with LLM's own knowledge base querying.
- **Visualize Knowledge**:
  - Visualize knowledge graphs using [GraphRAG Visualizer](https://github.com/noworneverev/graphrag-visualizer) to explore relationships and gain insights through an intuitive interface.
- **Manage Memory**:
  - Create and delete separately managed memory data by user. Memory data is stored in GraphRAG-compatible formats (parquet) for structured knowledge management.

### Frontend Summary
- An intuitive, responsive interface built with React allows users to add, query, and visualize knowledge.

### Backend Summary
- Built with Flask to handle requests, manage data, and integrate with GraphRAG. Supports LLM-based processing for GraphRAG inputs/results using OpenAI GPT.

## Setup

### Prerequisites
- Python (tested on 3.12)
- Node.js and npm
- Git

### Installation and Setup
1. Clone the repository to local:
   ```bash
   git clone https://github.com/vo-olb/KGMem.git
   cd KGMem-main
   ```
   or spin it in GitHub Codespaces.
2. Ensure the parent folder of this project is accessible (this is where the `graphrag-visualizer` folder will be cloned and built).
3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the folder of the project, and add [OpenAI API Key](https://platform.openai.com/api-keys) into it:
   ```
   OPENAI_API_KEY="..."
   ```
5. Start the server:
   ```
   python server.py
   ```
   - This command will prepare the project, including running ``npm install``, ``npm run build``, and other necessary preparation steps.

### Access
Once the server is running, open your browser and navigate to:
```
http://127.0.0.1:5000
```
if you are running it at local. The homepage includes instructions for using the assistant.

## Future Improvements

### Cloud Deployment:
- Use Docker for containerized deployment.
- Implement user login and authentication.
- Enhance multi-user support with Redis for caching and task queues.

### Optimization:
- Optimize GraphRAG calling parameters for quicker responses and more reasonable graph construction (e.g., avoid separate entities for synonyms).
- Support asynchronous task handling with tools like Celery and Redis.

## Contributions
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the [MIT License](https://mit-license.org/).

## Acknowledgement
My deepest gratitude to my friend, teammate, mentor, and emotional supporter - **ChatGPT 4o**!  
A special thanks to **John Williams** and **Abel Sanchez** for offering the incredible course MIT 1.125, which provided the foundation for this project.  
And ackowledgement for all the tools and open-source projects that expedite realization of this project.