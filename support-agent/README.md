# Customer Support Agent

## Overview
This project implements a customer support assistant powered by a large language model (LLM) and integrated with tools for managing support tickets in Airtable. The assistant can answer customer queries using a knowledge base, create support tickets, and check ticket status.

The agent combines LLM capabilities with structured tool interactions to provide reliable and accurate responses, ensuring that no information is made up or guessed.

## Features
- Answer customer questions based on a knowledge base.
- Search for users in the Airtable database.
- Create support tickets for users facing issues.
- Check the status of existing tickets.
- Handles multiple tickets and returns concise responses.

## Requirements
- Python 3.9+
- Dependencies listed in `requirements.txt`:
  ````
  dotenv>=0.9.9
  langchain>=0.3.27
  langchain-community>=0.3.31
  langchain-google-genai>=2.1.12
  langchain-groq>=0.3.8
  pendulum>=3.1.0
  supabase>=2.22.0
  ````
## Installation
1. Clone the repository:
   ````
   git clone <repository-url>
   cd <repository-directory>
   ````

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```
3. Set up the LLM if using GROQ API:

   ```bash
   export GROQ_API_KEY=<your_api_key>
   ```

## Usage

Run the agent interactively:

```bash
python main.py
```

* Type your queries and follow the prompts.
* To exit the program, type `exit` or `quit`.

### Example Interactions

* **Create a ticket**: The agent will first verify the user exists and then create a ticket.
* **Check ticket status**: The agent will ask for `user_id` and provide ticket status in the form:

  ```
  Reason: <reason>, Status: <status>
  ```

## License

This project is licensed under the MIT License.
