# Compliance Check

## 1. Overview and Research Context
The Compliance Check is a Python-based Command-Line Interface (CLI) application developed as a Proof of Concept (PoC) for automating security and privacy compliance within a DevSecOps pipeline. 

By analyzing software requirements and Azure DevOps User Stories *before* development begins, this tool embodies the "shift-left" security paradigm. It evaluates raw text against major frameworks—including the OWASP Top 10, STRIDE threat modeling, GDPR, NIS2, and the European Health Data Space (EHDS) regulations. The objective is to determine the feasibility of utilizing localized Large Language Models (LLMs) to identify compliance gaps without transmitting proprietary requirements to third-party cloud providers, thereby maintaining strict data sovereignty.

## 2. Architecture and Class Relationships
The application follows a modular, object-oriented architecture leveraging Dependency Injection (DI) to adhere to the Open-Closed Principle and ensure robust testability. 

- **`main.py` (Composition Root):** Acts as the entry point. It loads environment variables, instantiates all necessary components (Client -> Service -> CLI), and starts the interactive Read-Eval-Print Loop (REPL).
- **`cli.compliance_cli.ComplianceCLI`:** Inherits from Python's built-in `cmd.Cmd`. It handles user interactions, parses input, and implements robust exception handling to ensure continuous execution (e.g., catching `KeyboardInterrupt` signals gracefully). It delegates analysis tasks to the `AnalysisService`.
- **`services.analysis_service.AnalysisService`:** Encapsulates the core business logic and prompt engineering. It receives User Story IDs or raw text, constructs the zero-shot prompt with strict JSON schema enforcement, and delegates the API call. 
- **`clients.analysis_client.AnalysisClient`:** Solely responsible for HTTP communication with the LLM inference engine. It constructs the payload, handles authentication, verifies HTTP status codes, and parses the JSON response. Network failures or malformed outputs raise a custom `ModelAPIError`. By abstracting this client, future researchers can seamlessly swap the localized Ollama client for a cloud-based client (e.g., Azure OpenAI) to conduct comparative performance studies without modifying the core service logic.
- **`helpers.report_handler.ReportHandler`:** A static utility class responsible for formatting the JSON output for the console and persisting the compliance reports to timestamped text files for auditing purposes in the `reports/` directory.

## 3. Usage & Interactive CLI Commands

Once started via `python main.py` or within Docker, the interactive terminal opens up a REPL interface indicating `(compliance) `. Available commands:

- **`help`** or **`?`**: List all available commands and get help for each.
- **`story <user_story_id>`**: Analyze an Azure DevOps User Story by ID. Example: `story 1234`
- **`text <raw_text>`**: Analyze raw text requirements directly. Example: `text The system shall allow users to upload profile pictures.`
- **`exit`**, **`quit`**, **`q`**, or **`EOF` (Ctrl+D)**: Gracefully terminate and exit the CLI.

## 4. Reproducibility and Deployment
To ensure both software and scientific reproducibility across developer environments and Azure DevOps CI/CD pipelines, the project utilizes comprehensive containerization and environment management.

### 4.1 Software Reproducibility
- **Environment Configuration (`.env`):** All environment-specific variables (model names, endpoint URLs, credentials) are abstracted using `python-dotenv`. A `.env.example` file is provided for straightforward initial setup.
- **Backend Infrastructure (`docker-compose.yml`):** Initializes and provisions the localized LLM inference engine (Ollama) and a reverse proxy (Nginx). The default model evaluated is `llama3.2:3b`.
- **CLI Containerization (`Dockerfile`):** The Python CLI is packaged into a lightweight `python:3.12-slim` container, leveraging Docker layer caching for `requirements.txt`. This guarantees the CLI executes in an identical environment regardless of the host operating system.
- **Automated Testing:** The codebase is rigorously evaluated using a deterministic testing suite built upon the `pytest` and `pytest-mock` frameworks, currently achieving a 100% passing rate across dedicated unit tests. The testing architecture is compartmentalized within the `tests/` directory, strategically organized to mirror the application's modular logic (categorized into `cli/`, `clients/`, `helpers/`, and `services/`). To ensure strict environmental independence and eliminate reliance on external infrastructure—such as running Docker containers or an active Ollama inference engine—all network communications and file system I/O operations are comprehensively mocked. 

  To locally execute the test suite and empirically validate component integrity, run the following command from the root of the project:
  ```bash
  python3 -m pytest tests/ -v
  ```
- **Code Quality:** The codebase strictly adheres to PEP 8 standards, enforced via the `black` formatter.

### 4.2 Scientific Reproducibility
- **LLM Parameters:** The inference engine is configured to execute prompts deterministically by requesting structured `json` format. (Future work may involve exposing and documenting specific hyperparameters like `temperature` and `top_p` via the Ollama API to further control hallucination rates).
- **Prompt Engineering:** The core scientific instrument is a zero-shot prompt embedded within `AnalysisService.__prepare_prompt()`. It explicitly commands the LLM to adopt a compliance persona, evaluate the text against the specified frameworks, and return a binary `is_compliant` boolean alongside an array of identified risks and mitigations.
- **Pipeline Integration:** The CLI is designed to be executed as a headless task within an Azure DevOps YAML pipeline. By piping requirements directly into the containerized CLI, non-compliant JSON outputs can be configured to trigger a non-zero exit code, thereby failing the build and preventing non-compliant user stories from entering the sprint backlog.

## 5. Setup & Containerization Guide

This section outlines the steps to configure, containerize, and run the compliance check environment securely using Docker and Nginx.

### 5.1 Environment Configuration
1. Clone the repository and navigate to the component directory.
2. Copy the `.env.example` file to create your active `.env` configuration:
   ```bash
   cp .env.example .env
   ```
3. Update the variables in `.env` (e.g., set `ENVIRONMENT=docker`, `OLLAMA_MODEL=llama3.2:3b`).

### 5.2 Authentication Setup (`htpasswd`)
The localized LLM (Ollama) is protected behind an Nginx reverse proxy that enforces Basic Authentication. To configure this:
1. Ensure you have the `htpasswd` utility installed (typically part of the `apache2-utils` or `httpd-tools` package).
2. Generate the `htpasswd` file in the root of the project directory:
   ```bash
   htpasswd -c htpasswd <your_username>
   ```
3. You will be prompted to enter and confirm a password. Make sure the chosen username and password match the `OLLAMA_USER` and `OLLAMA_PASSWORD` values in your `.env` file.

### 5.3 Starting the Infrastructure
The application's backend infrastructure is fully containerized using Docker Compose. It provisions both the Nginx proxy and the Ollama inference engine.
1. Build and start the containers in detached mode:
   ```bash
   docker-compose up -d
   ```
2. The Ollama engine will automatically pull the configured models (e.g., `llama3.2:3b`) on startup. Wait a few moments for the health checks to pass.

### 5.4 Running the CLI
You can execute the Compliance Check CLI either locally or via a Docker container:
- **Local Execution:** Ensure you have Python 3.12 installed. Install dependencies via `pip install -r requirements.txt` and run `python main.py`.
- **Containerized Execution:** The project provides a `Dockerfile` to package the CLI into a lightweight Python container.
  ```bash
  docker build -t compliance-cli .
  docker run -it --env-file .env --network host compliance-cli
  ```
