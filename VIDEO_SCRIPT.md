# Video Explanation Script (5-10 minutes)

## Introduction (30 seconds)

"Hi! I'm [Your Name], and I've built an AI-powered IT Support Chatbot using AWS Bedrock for this internship assessment. Let me walk you through my solution."

---

## Problem Statement (1 minute)

"The problem I'm solving is incident resolution in IT support teams.

Currently, when engineers face issues like database timeouts or authentication failures, they have to:
- Search through multiple documents
- Remember past solutions
- Ask senior engineers

This wastes time and creates inconsistent solutions.

My chatbot solves this by providing instant, grounded answers using AI and RAG architecture."

---

## Architecture Overview (2 minutes)

"Let me explain how it works:

**[Show architecture diagram]**

1. **User asks a question** - Like 'How do I fix database timeout errors?'

2. **Retrieval System** - Searches our knowledge base
   - I use keyword search for simplicity and reliability
   - Retrieves top 3 relevant documents
   - Also pulls statistics from a CSV file - this is my bonus feature!

3. **Context Building** - Combines documents and statistics

4. **AWS Bedrock** - This is the cloud AI service
   - I'm using Amazon Nova Lite model
   - It generates a grounded response
   - Only uses information from retrieved documents

5. **Response** - Shows step-by-step solution with source citations

The key here is RAG - Retrieval-Augmented Generation. The AI doesn't hallucinate because it only uses real documentation."

---

## Live Demo (3 minutes)

"Let me show you how it works:

**[Screen recording of chatbot]**

1. **Starting the app**: `streamlit run chatbot.py`

2. **First query**: 'How do I fix database timeout errors?'
   - See how it retrieves 3 relevant documents
   - Shows incident statistics from CSV
   - Generates step-by-step solution
   - Cites sources

3. **Analytics query**: 'How many database incidents occurred?'
   - This demonstrates external data integration
   - Pulls from CSV file
   - Shows trends

4. **Sidebar features**:
   - Analytics dashboard
   - Query history
   - Confidence scores

Notice the response time - about 2-3 seconds. The UI shows which documents were used, building trust."

---

## Technical Implementation (1.5 minutes)

"Let me quickly show the code structure:

**[Show chatbot.py]**

- **AWS Bedrock integration**: Using boto3 client, Converse API
- **Retrieval**: Simple keyword matching - scores documents by word overlap
- **CSV integration**: pandas reads incident_stats.csv
- **Streamlit**: Clean UI with metrics, expandable sections

**Key design decisions**:
- Keyword search instead of embeddings - simpler, works reliably
- CSV for external data - easy to integrate, demonstrates bonus requirement
- Nova Lite model - available in my region, cost-effective"

---

## Challenges & Learnings (1.5 minutes)

"I faced three main challenges:

**Challenge 1: Model availability**
- Some models weren't available in eu-north-1 region
- Solution: Tested multiple models, found Nova Lite works

**Challenge 2: Retrieval approach**
- Initially tried vector embeddings but had performance issues
- Solution: Switched to keyword search - simpler and more reliable

**Challenge 3: Response grounding**
- Needed to prevent AI hallucinations
- Solution: Strict system prompts + source citation

**What I learned**:
- AWS Bedrock API and model selection
- RAG architecture - balancing complexity vs reliability
- Prompt engineering for grounded responses
- External data integration with pandas
- Building production-ready AI applications"

---

## Bonus Features (30 seconds)

"I added several bonus features to stand out:

1. **CSV Integration** - Incident statistics from external file
2. **Analytics Dashboard** - Visual metrics in sidebar
3. **Query History** - Tracks recent questions
4. **Response Time** - Performance monitoring
5. **Feedback System** - User satisfaction tracking

These demonstrate clean integration and meaningful use of external data."

---

## Conclusion (30 seconds)

"To summarize:
- Built a working RAG chatbot using AWS Bedrock
- Solves real IT support problems
- Includes bonus external data integration
- Clean code, comprehensive documentation
- Ready for production use

Thank you for watching! I'm excited about the opportunity to work with your team and build more AI solutions."

---

## Recording Tips

### **Setup**
- Use OBS Studio or Loom for screen recording
- Test audio before recording
- Have chatbot running and ready

### **What to Show**
1. README file (problem statement)
2. Architecture diagram
3. Live demo of chatbot
4. Code walkthrough (brief)
5. CSV file (bonus feature)

### **Delivery Tips**
- Speak clearly and at moderate pace
- It's okay to pause and think
- Show enthusiasm for the project
- Be authentic - they value honesty over polish

### **Time Breakdown**
- Introduction: 30s
- Problem: 1min
- Architecture: 2min
- Demo: 3min
- Technical: 1.5min
- Challenges: 1.5min
- Bonus: 30s
- Conclusion: 30s
**Total: ~8 minutes**

---

## Practice Run Checklist

Before recording:
- [ ] Test chatbot works
- [ ] Have example queries ready
- [ ] Open files you'll show
- [ ] Test screen recording
- [ ] Practice once (don't over-rehearse!)
- [ ] Relax - authenticity matters more than perfection

---

**You've got this! Your chatbot is impressive and you understand it well. Just explain it clearly and you'll do great!** 🚀
