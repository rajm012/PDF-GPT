# 📄 PDF-GPT

**PDF-GPT** is a private, local-first chatbot that lets you **upload PDF documents, extract content into vector embeddings**, and ask questions about the documents using an LLM backend (powered by [Ollama](https://ollama.com/)). It's perfect for research, legal docs, notes, and more.

---

## 🚀 Features

- ✅ Upload PDF files from the frontend
- 🧠 Converts PDF into text chunks & generates embeddings
- 🔎 Stores embeddings in FAISS vector database
- 🤖 Query using local LLMs via Ollama (e.g., `llama3`, `mistral`, etc.)
- 🧩 Modular architecture (separated frontend/backend)
- 🌐 Frontend built using Streamlit
- 🛠️ Backend built using Flask

---

## 📁 Project Structure

```

PDF-GPT/
│
├── app\_back.py             # Flask backend server
├── app\_front.py            # Streamlit frontend
├── chat\_utils.py           # Utility functions for chat flow
├── config\_loader.py        # Loads config from config.toml
├── config.py               # Global constants / settings
├── config.toml             # Editable config file
├── llm\_handler.py          # Talks to Ollama or other LLMs
├── pdf\_processor.py        # PDF parsing, chunking, embedding
├── readme.md               # (You are here)
├── requirements.txt        # Python dependencies
├── vector\_store.py         # FAISS vector store logic
│
├── logs/                   # Log files
└── data/
├── uploads/            # Uploaded PDFs
└── vector\_db/          # FAISS DB for vector embeddings

````

---

## ⚙️ Setup Instructions

### ✅ 1. Install Dependencies

> ⚠️ Requires Python 3.9+

```bash
git clone https://github.com/your-username/pdf-gpt.git
cd pdf-gpt
pip install -r requirements.txt
````

### ✅ 2. Install & Run Ollama

Install [Ollama](https://ollama.com/download) and run a model:

```bash
ollama serve
ollama run llama3  # or mistral, gemma, etc.
```

This will expose Ollama on `http://localhost:11434`

### ✅ 3. Run Backend

```bash
python app_back.py
```

* Default: `http://localhost:5000`
* Make sure Ollama is running and model is pulled.

### ✅ 4. Run Frontend

```bash
streamlit run app_front.py
```

* Will open at `http://localhost:8501`

---

## ⚠️ .env / Config

All runtime settings are stored in `config.toml`, including:

```toml
[ollama]
base_url = "http://localhost:11434"
model_name = "llama3"

[flask]
port = 5000
debug = true

[vectorstore]
index_path = "data/vector_db"
```

No `.env` is used by default, but you can modify to use it if needed.

---

## 🌐 Deployment Guide

This project is meant to run locally, but if users want to deploy it themselves, here are some possible ways:

---

### 🧩 Option 1: Host Entire App Locally

**Ideal for personal use or internal networks.**

* Backend (Flask) runs on `localhost:5000`
* Frontend (Streamlit) on `localhost:8501`
* Ollama LLM runs on `localhost:11434`

This is how it's set up out-of-the-box.

---

### 🌍 Option 2: Tunnel Ollama using Ngrok

If you want to deploy the frontend (e.g. Streamlit Cloud) but keep Ollama local:

1. Start Ollama locally:

   ```bash
   ollama serve
   ollama run llama3
   ```

2. Create a tunnel to Ollama:

   ```bash
   ngrok http 11434
   ```

3. Use the public `https://xxxx.ngrok-free.app` in your `config.toml`:

   ```toml
   [ollama]
   base_url = "https://xxxx.ngrok-free.app"
   ```

> ⚠️ Don't expose Ollama directly to public without access control!

---

### ☁️ Option 3: Tunnel with Cloudflare

Cloudflare Tunnel is a free and more secure way to expose local ports:

1. Install cloudflared and login:

   ```bash
   cloudflared tunnel --url http://localhost:11434
   ```

2. Use the generated `https://xxxx.trycloudflare.com` in `config.toml`

---

### 🛡️ Recommended (Optional) Proxy Security

To avoid open LLM endpoints:

* Create a small Flask proxy that checks an API key
* Tunnel the proxy instead of Ollama directly
* Add authentication if deploying publicly

---

## 🧪 Testing

You can test your setup with:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3", "prompt": "Hello"}'
```

And test backend endpoint:

```bash
curl http://localhost:5000/ollama-status
```

---

## 🧠 Models Support

Any [Ollama](https://ollama.com/library) model can be used. Just change in `config.toml`:

```toml
model_name = "mistral"  # or llama3, gemma, phi3, etc.
```

---

## 🌐 Cloudflare Deployment for Public Access

You can expose your local Ollama API to the internet using Cloudflare Tunnel for remote access or deployment.

### Prerequisites
- Local Ollama server running (`ollama serve`)
- Cloudflared CLI installed

### Setup Cloudflare Tunnel

1. **Install Cloudflared**:
   ```bash
   # Windows
   winget install --id Cloudflare.cloudflared
   
   # macOS
   brew install cloudflared
   
   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Create a tunnel for your local Ollama**:
   ```bash
   cloudflared tunnel --url http://localhost:11434
   ```

3. **Update configuration**: The tunnel will provide a public URL like:
   ```
   https://actions-neither-printing-monaco.trycloudflare.com
   ```

4. **Configure PDF-GPT**: Update `config.toml`:
   ```toml
   [server]
   OLLAMA_HOST = "https://your-tunnel-url.trycloudflare.com"
   ```

### Security Considerations

⚠️ **Important Security Notice**: Exposing your LLM API publicly means anyone can:
- Send queries to your model
- Consume your bandwidth and compute resources
- Potentially overwhelm your server

**Recommended security measures**:
- Use Cloudflare Access for authentication
- Implement rate limiting
- Monitor usage and costs
- Consider using API keys or tokens
- Set up firewall rules

### Production Deployment

For production use, consider:
- Setting up a dedicated server/VPS
- Using Docker containers
- Implementing proper authentication
- Setting up monitoring and logging
- Using a reverse proxy (nginx/Apache)

---

## 📦 To-Do / Future Improvements

* [ ] Add support for multiple PDF uploads
* [ ] Track chat history per session
* [ ] LLM response streaming in frontend
* [ ] Dockerized version
* [ ] HuggingFace LLM support (optional fallback)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss.

---

## 📄 License

MIT License. See `LICENSE` file.

---

## 🙌 Acknowledgements

* [Ollama](https://ollama.com/)
* [Streamlit](https://streamlit.io/)
* [FAISS](https://github.com/facebookresearch/faiss)
* [SentenceTransformers](https://www.sbert.net/)

---
