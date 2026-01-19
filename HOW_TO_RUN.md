# How to Run C-AIRA - Simple Guide

## 🚀 Three Ways to Run

### Option 1: Use the Setup Script (Easiest)

1. **Double-click `setup.bat`** in the project folder
   - This will install everything automatically
   - Wait for it to complete

2. **Configure your Azure credentials:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your Azure OpenAI details

3. **Double-click `run.bat`**
   - This will build the index and start the app
   - Your browser will open automatically

---

### Option 2: Manual Setup (Step by Step)

#### Step 1: Open PowerShell in the project folder

Right-click in the folder → "Open in Terminal" or navigate:
```powershell
cd c:\Users\rsury\.gemini\antigravity\playground\photonic-pioneer
```

#### Step 2: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install dependencies (first time only)
```powershell
pip install -r requirements.txt
```

#### Step 4: Configure Azure OpenAI

Create `.env` file from the example:
```powershell
copy .env.example .env
```

Edit `.env` and add your credentials:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - Your API key
- `AZURE_OPENAI_LLM_DEPLOYMENT` - Your GPT-4 deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Your embedding deployment name

#### Step 5: Build the index (first time only)
```powershell
python scripts/build_index.py
```

This will:
- Load sample documents
- Create embeddings
- Build searchable index
- Takes 2-5 minutes

#### Step 6: Run the application
```powershell
streamlit run src/app/streamlit_app.py
```

Your browser will open to `http://localhost:8501`

---

### Option 3: Quick Commands (After Initial Setup)

Once you've done the setup once, you just need:

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run app
streamlit run src/app/streamlit_app.py
```

Or just double-click `run.bat`!

---

## 📝 What You Need

### Azure OpenAI Requirements

You need an Azure OpenAI resource with these models deployed:

1. **GPT-4 or GPT-3.5-Turbo** (for generating responses)
   - Deployment name: e.g., "gpt-4"

2. **text-embedding-ada-002** (for embeddings)
   - Deployment name: e.g., "text-embedding-ada-002"

### Where to Get Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. **Endpoint**: Overview → Endpoint URL
4. **API Key**: Keys and Endpoint → Key 1
5. **Deployment Names**: Model deployments → Your deployment names

---

## 🎯 Using the Application

Once the app is running:

1. **Enter your incident description** in the text box:
   ```
   Example: "Database connection timeout errors in production"
   ```

2. **Click "Get Resolution"**

3. **Review the response:**
   - Step-by-step resolution guidance
   - Source documents referenced
   - Retrieved context chunks

4. **Adjust settings** in the sidebar:
   - Number of sources (1-10)
   - Response creativity (0.0-1.0)

---

## 🔧 Common Issues

### "Configuration validation failed"
- Check that `.env` file exists
- Verify Azure credentials are correct
- Make sure deployment names match your Azure resources

### "Index file not found"
- Run `python scripts/build_index.py` first
- Check that `vector_store/` folder was created

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Port already in use
- Stop other Streamlit apps
- Or use different port: `streamlit run src/app/streamlit_app.py --server.port 8502`

---

## 📂 Project Structure

```
photonic-pioneer/
├── setup.bat              ← Run this first (one-time setup)
├── run.bat                ← Run this to start the app
├── .env.example           ← Copy to .env and configure
├── requirements.txt       ← Python dependencies
├── data/                  ← Sample documents (already included)
│   ├── incidents/
│   ├── runbooks/
│   └── logs/
├── scripts/
│   └── build_index.py     ← Builds the searchable index
└── src/
    └── app/
        └── streamlit_app.py  ← Main application
```

---

## 🎓 Quick Test

After setup, try these example queries:

1. "Database connection timeout errors"
2. "Users unable to log in with 401 errors"
3. "Server disk space full, deployment failing"
4. "JWT token validation failing"

The system will retrieve relevant documents and provide step-by-step resolution guidance!

---

## 📞 Need Help?

1. Check `QUICKSTART.md` for detailed instructions
2. Review `README.md` for full documentation
3. Check logs in `logs/` folder for errors
4. Verify Azure OpenAI credentials are correct

---

**That's it! You're ready to use C-AIRA! 🎉**
