# 🏠 EstateMind — AI-Powered Real Estate Assistant

EstateMind is an **AI-powered conversational real estate assistant** designed to help users search and interact with real estate data using natural language.

The system combines **LangGraph, LangChain, FastAPI, and Model Context Protocol (MCP)** to create a modular agentic workflow capable of understanding user intent, retrieving real estate data, handling greetings, and requesting human input when required.

---

## 🚀 Features

* 🤖 **AI-powered conversational real estate assistant**
* 🧠 **LangGraph-based agentic workflow**
* 🔀 **Intent classification and intelligent routing**
* 🔌 **MCP-based real estate tools**
* 🔍 **Natural-language property search**
* 💬 **Conversation history support**
* 👋 **Greeting handling**
* 🙋 **Human-in-the-loop (HITL) workflow**
* ⚡ **FastAPI backend**
* 🔗 **LangChain agent integration**
* 🌐 **OpenRouter-compatible LLM integration**
* 🧩 Modular node and tool architecture

---

## 🏗️ Architecture

EstateMind uses LangGraph to orchestrate different nodes based on the user's intent.

```text
                 +-----------+
                 | __start__ |
                 +-----------+
                        *
                        *
                        *
                +------------+
                | classifier |
                +------------+.
              ...       .      ...
           ...          .         ...
         ..             .            ..
+----------+        +-------+        +------+
| get_data |        | greet |        | hitl |
+----------+**      +-------+     ***+------+
              ***       *      ***
                 ***    *   ***
                    **  * **
                  +---------+
                  | __end__ |
                  +---------+
```

### Workflow

1. **User Request**

   * User sends a natural-language real estate query.

2. **Classifier**

   * Determines the intent of the request.
   * Routes the request to the appropriate node.

3. **Get Data**

   * Handles real estate-related queries.
   * Uses MCP tools to retrieve relevant property information.

4. **Greet**

   * Handles greetings and casual conversational requests.

5. **HITL**

   * Handles situations where human input or clarification is required.

6. **End**

   * Returns the final response to the user.

---

## 🧠 Agent Workflow

The overall architecture can be represented as:

```text
User
 │
 ▼
FastAPI
 │
 ▼
LangGraph
 │
 ▼
Classifier
 │
 ├──────────────► Greet
 │
 ├──────────────► Get Data
 │                    │
 │                    ▼
 │                  MCP
 │                    │
 │                    ▼
 │             Real Estate Data
 │
 └──────────────► HITL
                      │
                      ▼
                Human Input
                      │
                      ▼
                    End
```

---

## 🔌 MCP Integration

EstateMind uses the **Model Context Protocol (MCP)** to expose real estate functionality as tools that can be consumed by the AI agent.

This provides a separation between:

```text
AI Agent
   │
   ▼
MCP Client
   │
   ▼
MCP Server
   │
   ▼
Real Estate Tools / Data
```

This architecture makes the real estate tools modular and allows the agent to select the appropriate functionality based on the user's request.

---

## 💬 Conversational Context

EstateMind maintains conversation history so that users can ask follow-up questions naturally.

### Example

```text
User:
Show me properties in Gachibowli.

Assistant:
I found several properties in Gachibowli.

User:
Under 80 lakhs.

Assistant:
The request is interpreted using the previous context
as properties in Gachibowli under ₹80 lakhs.
```

Conversation history is maintained as structured data:

```json
[
  {
    "role": "user",
    "content": "Show me properties in Gachibowli"
  },
  {
    "role": "assistant",
    "content": "I found several properties in Gachibowli."
  },
  {
    "role": "user",
    "content": "Under 80 lakhs"
  }
]
```

This allows the agent to understand contextual follow-up questions without requiring users to repeat the entire query.

---

## 🛠️ Tech Stack

| Technology                | Purpose                            |
| ------------------------- | ---------------------------------- |
| **Python**                | Core programming language          |
| **FastAPI**               | Backend API                        |
| **LangChain**             | LLM and agent framework            |
| **LangGraph**             | Agent workflow orchestration       |
| **MCP**                   | Tool integration and communication |
| **OpenRouter**            | LLM API gateway                    |
| **PostgreSQL / Database** | Real estate data                   |
| **Pydantic**              | Data validation                    |
| **Uvicorn**               | ASGI server                        |
| **python-dotenv**         | Environment configuration          |

---

## 📁 Project Structure

```text
EstateMind/
│
├── Nodes/
│   ├── graph.py
│   ├── graph_state.py
│   ├── classifier.py
│   ├── router.py
│   ├── greet.py
│   ├── hitl.py
│   ├── query_data.py
│   ├── cond_edge.py
│   └── llm_.py
│
├── Tools/
│   ├── flask_api.py
│   └── tools.py
│
├── main.py
├── Readme.md
├── requirements.txt
├── .gitignore
└── .env
```

> `.env` should remain local and must never be committed to the repository.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nagesh2809/EstateMind.git
```

```bash
cd EstateMind
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
MCP_SERVER_URL=your_mcp_server_url
```

If your application requires additional credentials, add them to `.env`.

**Never commit API keys, database passwords, or other secrets to GitHub.**

---

## ▶️ Running the Application

Start the FastAPI application using:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

---

## 🔄 Example Interaction

### User

```text
Show me 2 BHK apartments in Gachibowli under 1 crore.
```

### EstateMind

The request is classified as a real estate data query and routed through the `get_data` workflow.

```text
User Query
    ↓
Classifier
    ↓
Get Data
    ↓
MCP Tool
    ↓
Real Estate Data
    ↓
LLM
    ↓
Natural Language Response
```

---

## 🎯 Use Cases

EstateMind can be used for queries related to:

* Property availability
* Location-based property search
* Budget-based property search
* BHK filtering
* Property type
* Locality
* Pincode
* Metro proximity
* Project information
* Property prices
* Market value
* RERA information
* Nearby properties
* Conversational follow-up queries

---

## 🧩 Why LangGraph?

LangGraph allows EstateMind to represent the application as a structured stateful workflow.

Instead of a simple:

```text
User → LLM → Response
```

EstateMind uses:

```text
User
 ↓
Classifier
 ↓
Intent-based routing
 ↓
Specialized node
 ↓
Tools / MCP
 ↓
LLM
 ↓
Response
```

This makes the system easier to extend with additional agents, tools, validation steps, and human-in-the-loop workflows.

---

## 🔮 Future Improvements

Potential improvements include:

* [ ] Advanced property recommendation system
* [ ] RAG-based property document search
* [ ] User authentication and authorization
* [ ] Persistent conversation memory
* [ ] Property comparison
* [ ] Personalized property recommendations
* [ ] Location-aware property search
* [ ] Improved HITL workflows
* [ ] Docker deployment
* [ ] Kubernetes deployment
* [ ] Redis-based session management
* [ ] Observability and LLM tracing
* [ ] Automated testing and CI/CD

---

## 👨‍💻 Author

**Nagesh Kure**

AI/ML Engineer focused on:

* Agentic AI
* Generative AI
* LLM Applications
* RAG
* LangChain
* LangGraph
* MCP
* FastAPI
* Backend Systems

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

**EstateMind — Making real estate search conversational with Agentic AI.**


