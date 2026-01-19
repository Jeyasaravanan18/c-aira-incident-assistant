# C-AIRA: Context-Aware Incident Response Assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900.svg)](https://aws.amazon.com/bedrock/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg)](https://streamlit.io/)

An AI-powered chatbot that helps IT support teams resolve operational incidents faster using Retrieval-Augmented Generation (RAG) with AWS Bedrock.

## 📹 Project Walkthrough Video

[Watch the 10-minute project explanation video](VIDEO_LINK_HERE)

*Video covers: Problem Statement, Architecture, Live Demo, Technical Implementation, and Key Learnings*

---

## 🎯 Problem Statement

IT support and DevOps teams face critical challenges during incident resolution:

- **Scattered Documentation**: Incident reports, runbooks, and logs distributed across multiple systems
- **Time-Consuming Searches**: Manual searches waste valuable time during critical incidents
- **Inconsistent Resolutions**: Different team members apply different solutions to similar problems
- **Knowledge Silos**: Tribal knowledge not easily accessible to all team members
- **High-Pressure Situations**: Difficult to recall relevant procedures during emergencies

**Target Users**: IT Support Engineers, DevOps Teams, SRE Teams

**Why This Problem**: In enterprise environments, every minute of downtime costs money. Faster, more consistent incident resolution directly impacts business continuity.

---

## 💡 Solution Overview

C-AIRA addresses these challenges through:

1. **Centralized Knowledge**: Indexes incident reports, runbooks, and logs
2. **Intelligent Retrieval**: Finds relevant historical information using RAG
3. **Grounded Responses**: Generates step-by-step guidance based on retrieved context
4. **Historical Insights**: Enriches responses with CSV analytics (136 incidents analyzed)
5. **Real-time Monitoring**: Integrates GitHub Status API for live service health
6. **Source Attribution**: Always cites source documents for transparency

---

## 🏗️ System Architecture

### RAG Flow

```
User Query
    ↓
┌─────────────────────────────────────┐
│  1. Document Retrieval              │
│     - Search knowledge base         │
│     - Keyword matching              │
│     - Top-3 relevant docs           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. CSV Analytics Integration       │
│     - Search incident_stats.csv     │
│     - Match similar incidents       │
│     - Extract historical patterns   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. Context Enrichment              │
│     - Combine documents + CSV data  │
│     - Build comprehensive context   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. AWS Bedrock (Nova Lite)         │
│     - Generate grounded response    │
│     - Temperature: 0.1 (focused)    │
│     - Max tokens: 1000              │
└─────────────────────────────────────┘
    ↓
Enhanced Response + Sources + Historical Insights
```

---

## ✨ Key Features

### Core Capabilities
- **RAG Implementation**: Retrieves relevant documents before generating responses
- **Grounded Responses**: LLM responses strictly based on retrieved context
- **Source Attribution**: Every response includes source document references
- **Multi-Document Types**: Supports incident reports, runbooks, and log files

### Bonus Features (External Data Integration)
- **CSV Analytics Dashboard**: 136 incidents analyzed with interactive charts
- **GitHub Status API**: Real-time service monitoring
- **Query History**: Track last 5 queries in session
- **Response Time Metrics**: Performance tracking
- **Premium UI**: Glassmorphism design with dark mode

---

## 🛠️ Technology Stack

### AI & Cloud Services
- **AWS Bedrock**: LLM hosting platform
- **Amazon Nova Lite**: Foundation model (`amazon.nova-lite-v1:0`)
- **Region**: eu-north-1

### Core Technologies
- **Python 3.8+**: Primary language
- **Streamlit**: Web application framework
- **Pandas**: CSV data analysis
- **Plotly**: Interactive visualizations

### External Data Sources
- **CSV File**: `incident_stats.csv` (136 incidents, 4 months)
- **GitHub Status API**: Real-time service health monitoring
- **Local Knowledge Base**: Incidents, runbooks, logs

---

## 📁 Project Structure

```
c-aira-incident-assistant/
│
├── chatbot_enhanced.py      # Main application
├── requirements.txt         # Python dependencies
├── .env.example            # AWS credentials template
├── .gitignore              # Git ignore rules
├── HOW_TO_RUN.md           # Quick start guide
├── VIDEO_SCRIPT.md         # Video recording guide
│
├── data/                   # Knowledge base
│   ├── incidents/          # Incident reports (3 files)
│   ├── runbooks/          # Resolution procedures (3 files)
│   ├── logs/              # Log samples (2 files)
│   └── incident_stats.csv # CSV analytics (136 incidents)
│
└── src/                    # Source code modules
    └── data_sources/
        ├── __init__.py
        ├── csv_analyzer.py      # CSV analytics logic
        └── api_integrations.py  # GitHub API integration
```

---

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **AWS Account with Bedrock Access**
   - Active AWS account
   - Bedrock enabled in `eu-north-1` region
   - AWS Access Key ID and Secret Access Key

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/c-aira-incident-assistant.git
   cd c-aira-incident-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials**
   
   Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=eu-north-1
   MODEL_ID=amazon.nova-lite-v1:0
   ```

5. **Run the application**
   ```bash
   streamlit run chatbot_enhanced.py
   ```
   
   The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### Basic Usage

1. **Navigate to the Chatbot tab**
2. **Enter your incident description**:
   - Example: "Database connection timeout errors in production"
   - Example: "Users unable to log in, receiving 401 errors"
3. **Click "🚀 Analyze"**
4. **Review the response**:
   - AI-generated resolution steps
   - Historical incident data (if similar incidents found)
   - Source documents referenced

### Example Queries

```
"How do I fix database timeout errors?"
"What causes authentication failures?"
"Steps to resolve disk space issues"
"API response time degraded to 5000ms+"
```

### Exploring Features

**Tab 1: Incident Response**
- Main chatbot interface
- Historical incident insights
- Source attribution
- Query history sidebar

**Tab 2: Analytics Hub**
- Incident statistics (136 incidents)
- Interactive charts (pie, bar, line)
- Monthly trends
- Severity distribution

**Tab 3: Live Operations**
- GitHub Status API integration
- Real-time service health
- Recent incidents
- Connected data sources

---

## 🎨 Design Decisions

### Why AWS Bedrock?
- **Multiple Models**: Access to various foundation models
- **Serverless**: No infrastructure management
- **Scalability**: Production-ready
- **Security**: Built-in AWS security features

### Why Amazon Nova Lite?
- **Cost-Effective**: Lower cost than GPT-4
- **Fast**: Quick response times
- **Capable**: Sufficient for RAG use cases
- **Available**: Accessible in eu-north-1

### Why Keyword Search (Not Vector Embeddings)?
- **Simplicity**: Easier to implement and debug
- **Sufficient**: Works well for small knowledge bases
- **Transparent**: Easy to understand matching logic
- **Fast**: No embedding generation overhead

**Future Enhancement**: Can upgrade to FAISS + embeddings for larger datasets

### Temperature Setting: 0.1
- **Low temperature**: Deterministic, focused responses
- **Reduces creativity**: Prioritizes accuracy over variety
- **Appropriate**: Perfect for technical troubleshooting
- **Minimizes hallucinations**: Stays grounded in context

---

## 🌟 Bonus Features Explained

### CSV Analytics Integration

**Data Source**: `data/incident_stats.csv`
- 136 incidents across 4 months (Jan-Apr 2024)
- 3 incident types: database_timeout, auth_failure, disk_space
- Metrics: count, avg_resolution_hours, severity, status

**Implementation**: `src/data_sources/csv_analyzer.py`
- `search_similar_incidents()`: Matches query to incident types
- `get_insights()`: Auto-generates 4 key insights
- `get_monthly_trends()`: Time series analysis

**Integration**: Enriches LLM context with historical data
```python
csv_insights = csv_analyzer.search_similar_incidents(query)
context += csv_context  # Add to LLM prompt
```

### GitHub Status API

**Endpoint**: `https://www.githubstatus.com/api/v2/status.json`
- Real-time service health
- Recent incidents
- 5-minute caching

**Implementation**: `src/data_sources/api_integrations.py`
- `get_status()`: Current operational status
- `get_recent_incidents()`: Last 3 incidents
- Error handling with fallback

---

## 🔄 Data Flow

```
User submits query
    ↓
Parallel data retrieval:
├─→ Knowledge base search (RAG)
├─→ CSV analytics query
└─→ GitHub API check (if relevant)
    ↓
Context enrichment
    ↓
AWS Bedrock (Nova Lite)
    ↓
Enhanced response with:
- Step-by-step resolution
- Historical patterns
- Average resolution time
- Source attribution
```

---

## 🧪 Testing

Run the external data integration test:
```bash
python test_external_data.py
```

Expected output:
```
✅ CSV Analyzer: PASSED
✅ GitHub API: PASSED
✅ Data Integration: PASSED
```

---

## 🎓 Key Learnings

### Technical Learnings
1. **RAG Architecture**: How retrieval improves LLM accuracy
2. **AWS Bedrock API**: Using the Converse API effectively
3. **Context Engineering**: Balancing context size vs. relevance
4. **External Data Integration**: Enriching responses with real data

### Challenges Faced
1. **Platform Switch**: Initially planned Azure, switched to AWS Bedrock
2. **Model Selection**: Tested multiple models before choosing Nova Lite
3. **Context Limits**: Balancing retrieved docs + CSV data within token limits
4. **Grounding Responses**: Preventing hallucinations with strict prompts

### Best Practices Learned
- Low temperature (0.1) for technical use cases
- Always cite sources for transparency
- Enrich context with external data when available
- Simple solutions (keyword search) can be effective

---

## 🔧 Troubleshooting

### Application Won't Start

**Problem**: `streamlit run` fails

**Solutions**:
1. Verify virtual environment is activated
2. Check dependencies: `pip install -r requirements.txt`
3. Ensure AWS credentials in `.env` file
4. Check for port conflicts (default: 8501)

### No Results Returned

**Problem**: Queries return no relevant results

**Solutions**:
1. Try more specific queries
2. Check if query topic exists in knowledge base
3. Verify data/ folder contains documents
4. Review keyword matching logic

### AWS Bedrock Errors

**Problem**: `AccessDeniedException` or model errors

**Solutions**:
1. Verify AWS credentials in `.env`
2. Ensure Bedrock is enabled in eu-north-1
3. Check model ID: `amazon.nova-lite-v1:0`
4. Verify IAM permissions for Bedrock

---

## 📊 Assessment Alignment

This project demonstrates:

✅ **Clear Problem Definition**: IT incident resolution challenges  
✅ **RAG Implementation**: Document retrieval + LLM generation  
✅ **AWS Bedrock Integration**: Amazon Nova Lite model  
✅ **Code Quality**: Modular, well-structured, documented  
✅ **Comprehensive Documentation**: This README + additional guides  
✅ **Bonus: External Data**: CSV analytics + GitHub API  
✅ **Meaningful Integration**: Historical data enriches responses  
✅ **Clear Data Flow**: Documented architecture  

---

## 🚀 Future Enhancements

### Short-term
- [ ] Migrate to vector embeddings (FAISS)
- [ ] Add conversation history
- [ ] Implement user feedback mechanism
- [ ] Support PDF/Word documents

### Long-term
- [ ] Multi-language support
- [ ] Integration with ticketing systems (Jira, ServiceNow)
- [ ] Automated incident detection from logs
- [ ] Predictive incident prevention

---

## 📄 License

This project is created for educational and demonstration purposes as part of an internship assessment.

---

## 🙏 Acknowledgments

- AWS Bedrock for LLM hosting
- Streamlit for rapid UI development
- GitHub Status API for real-time data
- The open-source community

---

**Built with ❤️ using AWS Bedrock, Python, and Streamlit**

For questions or issues, please refer to `HOW_TO_RUN.md` or check the troubleshooting section above.
