# README

1. Ensure `uv` is installed ([UV Installation](https://docs.astral.sh/uv/getting-started/installation/))
2. Clone the `ai-agent-from-scratch` repo
    ```shell
    git clone https://github.com/dartcrossett/ai-agent-from-scratch.git
    ```
3. Navigate into `ai-agent-from-scratch`
4. Update `DARTMOUTH_CHAT_API_KEY` in the `.env` file with your Dartmouth Chat API key.
5. Run the agent
    ```shell
    uv run -p 3.13 -w httpx,python-dotenv agent.py
    ```
