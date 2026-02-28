# 🎯 Smart Sales Lead Analyst

An AI-powered sales intelligence tool that analyzes sales call PDF transcripts and ranks leads by their likelihood of purchasing within the next month. Built for sales managers who want actionable, data-driven insights without manual review of every call recording.

---

## 📸 Demo

> Ask: *"Which leads are most likely to buy next month?"*

**Output:**

```
#1 Emma Wilson — Score: 95/100
• Series B funded, $25M raised — budget explicitly confirmed at $200K authority
• Self-imposed deadline of November 30th — board meeting December 5th creates urgency
• LinkedIn: CRO-level seniority, full signing authority, no committee needed
• Already shortlisted to final 2 vendors; demo Thursday with intent to sign

#2 Nina Patel — Score: 91/100
• CEO and sole decision-maker, no approval chain
• Calculated ROI herself: pays back in month 2
• Trial started yesterday; calling back Monday with contract intent
• LinkedIn: Founder, 1-10 person company, fast-moving culture

#3 Sarah Johnson — Score: 78/100
• Board-approved $80K budget, procurement involved this week
• Hard deadline: running by January for Q1 hiring push
• LinkedIn: VP-level, decision-maker status confirmed
• Wants contract signed by December 15th
```

---

## 🏗️ Architecture

```
PDFs in /data/pdfs/
        │
        ▼
   ingest.py
   ┌─────────────────────────┐
   │ PyPDFLoader             │  ← Extract text from PDFs
   │ RecursiveCharacterSplitter │ ← Chunk into ~500 token pieces
   │ Metadata tagging        │  ← lead_name, source_pdf, chunk_id
   └────────────┬────────────┘
                │
                ▼
         vectorstore.py
   ┌─────────────────────────┐
   │ OpenAI Embeddings       │  ← text-embedding-3-small
   │ ChromaDB (persistent)   │  ← stored in ./chroma_db/
   └────────────┬────────────┘
                │
                ▼
           agent.py
   ┌─────────────────────────┐
   │ LangChain ReAct Agent   │
   │  ├─ VectorSearchTool    │  ← searches ChromaDB
   │  └─ LinkedInSearchTool  │  ← simulated enrichment
   │ GPT-4o-mini (LLM)       │
   └────────────┬────────────┘
                │
                ▼
            app.py
   ┌─────────────────────────┐
   │ Streamlit UI            │  ← ranked leads + scores + reasoning
   └─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Orchestration | LangChain (ReAct Agent) |
| Vector Database | ChromaDB (local persistent) |
| PDF Parsing | PyPDF via LangChain |
| UI | Streamlit |
| Environment | python-dotenv |

---

## 🤖 How the Agent Works

The system uses a **LangChain ReAct Agent** — a reasoning + acting loop where the model alternates between thinking, calling tools, and observing results.

### ReAct Loop (simplified):

```
Thought: I need to find leads with buying signals
Action: VectorSearchTool("buying intent budget timeline")
Observation: [chunks from Sarah, Emma, Nina transcripts...]

Thought: I found 3 strong leads. Let me enrich with LinkedIn data
Action: LinkedInSearchTool("Emma Wilson")  
Observation: CRO | Senior Leadership | Decision Maker: Yes | 501-1000 employees

Thought: Emma has C-suite authority, confirmed budget, and self-imposed deadline
Action: LinkedInSearchTool("Nina Patel")
Observation: Founder | C-Suite | Decision Maker: Yes | 1-10 employees

Thought: Now I have enough to rank. Emma scores highest because...
Final Answer: [Ranked lead list with scores and reasoning]
```

### Scoring signals the agent looks for:

- **Budget signals** — explicit dollar amounts, CFO/board approval, budget confirmed
- **Timeline urgency** — hard deadlines, quarter-end pressure, event-driven urgency
- **Decision authority** — C-suite, VP, founder vs. manager or committee buyer
- **Intent phrases** — "ready to sign", "move forward", "contract by X date"
- **Objections** — budget frozen, long procurement cycles, multiple approvers
- **LinkedIn enrichment** — seniority, company size, decision-maker flag

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-sales-lead-analyst.git
cd smart-sales-lead-analyst
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here
```

### 5. Add PDF transcripts (or generate samples)

```bash
# Option A: Generate 5 realistic sample transcripts
python generate_sample_pdfs.py

# Option B: Copy your own PDFs
cp /your/transcripts/*.pdf data/pdfs/
```

### 6. Run the Streamlit app

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### 7. In the UI:
1. Enter your OpenAI API key (or it reads from `.env`)
2. Click **"⚡ Process PDFs"** to ingest transcripts
3. Type your question and click **"🔍 Analyze Leads"**

---

## 📁 Project Structure

```
smart-sales-lead-analyst/
│
├── data/
│   └── pdfs/                  # Place your PDF transcripts here
│
├── chroma_db/                 # Auto-created: persisted vector DB
│
├── app.py                     # Streamlit UI
├── ingest.py                  # PDF loading → chunking → embeddings
├── agent.py                   # LangChain ReAct agent + tool definitions
├── vectorstore.py             # ChromaDB wrapper (init, store, search)
├── linkedin_tool.py           # Simulated LinkedIn profile enrichment
├── utils.py                   # Parsing, formatting, config helpers
├── generate_sample_pdfs.py    # Creates demo PDFs for testing
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 💡 Example Questions to Ask

- `"Which leads are most likely to buy in the next month?"`
- `"Who has confirmed budget and a hard deadline?"`
- `"Show me leads where the decision-maker is C-suite level"`
- `"Which leads mentioned specific dollar amounts?"`
- `"Who had the most objections in their calls?"`

---

## 🔮 Future Improvements

| Feature | Description |
|---------|-------------|
| **Real LinkedIn API** | Replace simulation with actual LinkedIn Sales Navigator or People Data Labs API |
| **CRM Integration** | Push ranked leads directly into Salesforce or HubSpot |
| **Audio Transcription** | Accept `.mp3`/`.mp4` sales calls and auto-transcribe with Whisper |
| **Deal Velocity Tracking** | Track score changes across multiple calls over time |
| **Email Alerts** | Notify sales manager when a lead crosses a score threshold |
| **Multi-model Support** | Allow switching between GPT-4o, Claude, Gemini via a dropdown |
| **Batch Processing** | Queue-based async ingestion for large PDF libraries (100+) |
| **Analytics Dashboard** | Win/loss tracking, avg score by industry, rep performance |
| **RAG Evaluation** | Add RAGAS metrics to measure retrieval quality automatically |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built as a portfolio project demonstrating production LangChain + RAG + Agent patterns.*
