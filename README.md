# Intelligent Chatbot Project

## Environment Setup

1. Make the setup script executable:

   ```bash
   chmod +x setup_venv.sh
   ```

2. Run the setup script:

   ```bash
   ./setup_venv.sh
   ```

3. This will:

   - Create a virtual environment named "venv"
   - Generate a requirements.txt file based on project imports
   - Install all required packages in the virtual environment

4. To activate the virtual environment manually:

   ```bash
   source venv/bin/activate
   ```

5. To deactivate when done:
   ```bash
   deactivate
   ```

## Running the Chatbot

Always make sure your virtual environment is activated before running:

```bash
conda activate $ENV_NAME
python chainlit run app.py
```
