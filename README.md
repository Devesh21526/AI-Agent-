

# JARVIS Voice Assistant 🎤🤖



## 🚀 Overview

JARVIS is a comprehensive voice assistant application that combines the power of modern AI with intuitive user interfaces. Built with Python and featuring both desktop and web implementations, JARVIS offers real-time voice interaction, intelligent conversation handling, and a gaming-inspired interface design.

### 🎯 Key Highlights

- **Dual Interface**: Desktop application with PyQt5 and web interface with Flask
- **Real-time Voice Processing**: Advanced speech recognition and synthesis
- **Gaming-Style UI**: Modern, futuristic interface inspired by ACER PredatorSense
- **AI-Powered**: Integration with Ollama and DeepSeek models for intelligent responses
- **Performance Monitoring**: Real-time system performance tracking and optimization
- **Wake Word Detection**: Hands-free activation with customizable wake words

## ✨ Features

### 🖥️ Desktop Application
- **Gaming-Style Interface**: Dark theme with cyan accents and glowing effects
- **Real-time Performance Monitoring**: CPU, GPU, Memory, and Temperature tracking
- **Circular Gauge Indicators**: Visual performance metrics with color-coded warnings
- **System Tray Integration**: Background operation with quick access controls
- **Voice Command Processing**: Full integration with JARVIS voice assistant
- **Conversation History**: Live display of voice interactions
- **Settings Panel**: Comprehensive configuration options

### 🌐 Web Application
- **Modern Web Interface**: Responsive design with WebSocket support
- **Real-time Updates**: Live performance metrics and conversation display
- **Cross-platform Compatibility**: Works on any modern web browser
- **Mobile Responsive**: Optimized for desktop and mobile devices
- **API Integration**: RESTful API for external integrations
- **Dashboard Analytics**: Visual charts and performance insights

### 🎤 Voice Assistant Core
- **Wake Word Detection**: Customizable activation phrases
- **Speech Recognition**: Google Speech API integration
- **Natural Language Processing**: Advanced conversation handling
- **Text-to-Speech**: Natural voice synthesis
- **Conversation Memory**: Context-aware responses
- **Interrupt Handling**: Responsive voice command processing
- **Performance Optimization**: Efficient resource usage

## 🛠️ Tech Stack

### Desktop Application
| Component | Technology | Purpose |
|-----------|------------|---------|
| **GUI Framework** | PyQt5 | Native desktop interface |
| **Voice Processing** | SpeechRecognition, PyAudio | Voice input/output |
| **AI Integration** | Ollama, LangChain | LLM processing |
| **Performance Monitoring** | psutil, threading | System metrics |
| **Wake Word Detection** | pvporcupine | Voice activation |
| **Speech Synthesis** | win32com.client (SAPI) | Text-to-speech |

### Web Application
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | Flask | Web server and API |
| **Real-time Communication** | Flask-SocketIO | WebSocket connections |
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Charts & Visualization** | Chart.js | Performance dashboards |
| **HTTP Client** | Axios | API communications |
| **WebSocket Client** | Socket.IO | Real-time updates |

### AI & Machine Learning
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language Model** | DeepSeek-R1 | Conversational AI |
| **Model Management** | Ollama | LLM optimization |
| **NLP Framework** | LangChain | Chain processing |
| **Memory Management** | ConversationBufferWindowMemory | Context retention |
| **Prompt Engineering** | Custom templates | Response optimization |

### Development & Deployment
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Version Control** | Git | Source code management |
| **Package Management** | pip, npm | Dependency management |
| **Environment Management** | venv, conda | Isolated environments |
| **Process Management** | systemd, Windows Services | Background services |
| **Logging** | Python logging | Error tracking |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ (for web interface)
- Ollama installed and running
- Microphone and speakers
- Git

### Desktop Application Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Devesh21526/jarvis-assistant.git
   cd jarvis-assistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Ollama**
   ```bash
   ollama pull deepseek-r1
   ```

5. **Run the Desktop Application**
   ```bash
   python launch_jarvis.py
   ```

### Web Application Setup

1. **Install Web Dependencies**
   ```bash
   pip install -r web_requirements.txt
   ```

2. **Setup Frontend**
   ```bash
   cd web_interface
   npm install
   npm run build
   ```

3. **Start the Web Server**
   ```bash
   python app.py
   ```

4. **Access the Interface**
   Open your browser and navigate to `http://localhost:5000`

### Quick Start with Docker

```bash
# Build and run the complete application
docker-compose up -d

# Access desktop app: Connect to VNC on port 5900
# Access web app: http://localhost:5000
```

## 🎮 Usage

### Desktop Application

1. **Launch JARVIS**
   ```bash
   python launch_jarvis.py
   ```

2. **System Tray Operation**
   - Application minimizes to system tray
   - Right-click for quick access menu
   - Double-click to restore window

3. **Voice Commands**
   - Say "Jarvis" to activate
   - Speak your command naturally
   - View conversation history in real-time

4. **Performance Monitoring**
   - Monitor CPU, GPU, and memory usage
   - View temperature readings
   - Track system performance metrics

### Web Application

1. **Start the Server**
   ```bash
   python app.py
   ```

2. **Access the Dashboard**
   - Open `http://localhost:5000` in your browser
   - View real-time performance metrics
   - Monitor voice assistant activity

3. **Voice Interaction**
   - Click the microphone button to start listening
   - Speak your commands
   - View responses in the chat interface

### Voice Commands Examples

| Command | Action |
|---------|--------|
| "Jarvis, what's the weather?" | Get weather information |
| "Jarvis, open YouTube" | Open YouTube in browser |
| "Jarvis, what time is it?" | Get current time |
| "Jarvis, tell me a joke" | Get a random joke |
| "Jarvis, system status" | Show system information |
| "Jarvis, stop" | Deactivate assistant |

## 🔧 Configuration

### Desktop Application Settings

Create a `config.json` file in the root directory:

```json
{
  "voice": {
    "wake_word": "jarvis",
    "speech_rate": 4,
    "language": "en-US",
    "timeout": 5
  },
  "ai": {
    "model": "deepseek-r1",
    "temperature": 0.5,
    "max_tokens": 512,
    "context_window": 2048
  },
  "ui": {
    "theme": "dark",
    "accent_color": "#00D4FF",
    "show_performance": true,
    "minimize_to_tray": true
  }
}
```

### Web Application Settings

Set environment variables:

```bash
export FLASK_ENV=production
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export OLLAMA_URL=http://localhost:11434
export SECRET_KEY=your-secret-key-here
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Test Desktop Application
```bash
python -m pytest tests/test_desktop.py -v
```

### Test Web Application
```bash
python -m pytest tests/test_web.py -v
```

### Test Voice Processing
```bash
python -m pytest tests/test_voice.py -v
```

## 🚀 Deployment

### Desktop Application

1. **Windows Service Installation**
   ```bash
   python scripts/setup_service.py install
   ```

2. **Linux systemd Service**
   ```bash
   sudo cp jarvis.service /etc/systemd/system/
   sudo systemctl enable jarvis
   sudo systemctl start jarvis
   ```

### Web Application

1. **Using Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Using Docker**
   ```bash
   docker build -t jarvis-web .
   docker run -p 5000:5000 jarvis-web
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🔍 API Documentation

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Get system status |
| POST | `/api/voice/command` | Send voice command |
| GET | `/api/performance` | Get performance metrics |
| GET | `/api/conversations` | Get conversation history |
| POST | `/api/settings` | Update settings |

### WebSocket Events

| Event | Description | Data |
|-------|-------------|------|
| `connect` | Client connected | - |
| `disconnect` | Client disconnected | - |
| `voice_command` | Voice command received | `{command: string}` |
| `performance_update` | Performance metrics | `{cpu: number, memory: number}` |
| `conversation_update` | New conversation | `{user: string, assistant: string}` |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Your Changes**
4. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```
5. **Submit a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Add docstrings for all functions
- Include type hints where appropriate
- Write unit tests for new features

## 📊 Performance Benchmarks

| Metric | Desktop App | Web App |
|--------|-------------|---------|
| **Memory Usage** | ~150MB | ~80MB |
| **CPU Usage** | ~5-10% | ~3-7% |
| **Response Time** | 

**Built with ❤️ by [Your Name](https://github.com/yourusername)**

[⬆ Back to Top](#jarvis-voice-assistant-🎤🤖)


