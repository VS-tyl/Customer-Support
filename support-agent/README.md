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

## Installation
1. Clone the repository:
   ````
   git clone <repository-url>
   cd <repository-directory>
   ````

2. Install dependencies:

   ```
   uv install
   ```
3. Set up API keys in `.env` file:


## Usage

Run the agent interactively:

```
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

