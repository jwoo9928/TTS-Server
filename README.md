# TTS-Server 🎙️

Flask Python XTTS Streaming Docker

A high-performance Text-to-Speech API server that provides real-time streaming capabilities with multiple voice model support and thread-safe operations.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API Documentation](#api-documentation) • [Contributing](#contributing)

## 🎯 Project Role & Purpose

This TTS-Server acts as a crucial infrastructure component for voice-enabled applications, playing several key roles:

| Role                       | Description                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| 🔊 Voice Generation Engine | Powers applications requiring high-quality text-to-speech conversion with multiple voice models |
| 🌊 Streaming Service       | Provides real-time audio streaming capabilities for immediate voice feedback                    |
| 🎭 Voice Model Hub         | Manages and serves multiple voice models for different use cases and languages                  |
| 🔒 Resource Manager        | Ensures thread-safe operations and optimal resource utilization                                 |
| 🌐 Multi-Language Support  | Handles text-to-speech conversion across multiple languages                                     |

### Key Benefits

**For Application Developers:**

- Ready-to-use TTS API endpoints
- Real-time streaming capabilities
- Multiple voice model support
- Thread-safe operations

**For Service Providers:**

- High-performance architecture
- Scalable deployment options
- Resource optimization
- Comprehensive monitoring

**For End Users:**

- High-quality voice output
- Real-time voice generation
- Multiple language support
- Customizable voice options

## 🌟 Features

| Feature              | Description                                  |
| -------------------- | -------------------------------------------- |
| 🚀 High Performance  | Optimized for fast text-to-speech conversion |
| 🌊 Streaming Support | Real-time audio streaming capabilities       |
| 🎭 Multiple Models   | Support for various voice models             |
| 🌍 Multi-Language    | Handles multiple languages                   |
| 🔄 Chunk Processing  | Configurable chunk sizes for streaming       |
| 📚 API Documentation | Comprehensive Swagger documentation          |
| 🐳 Containerization  | Full Docker support                          |
| 🔒 Thread Safety     | Secure multi-threaded operations             |

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Docker (optional)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/username/TTS-Server.git
cd TTS-Server

# Install dependencies
pip install -r requirements.txt

# Set up voice models
mkdir -p models
# Place your voice models in the models directory

# Start the server
gunicorn -w 2 --worker-class gthread --threads 2 -b 0.0.0.0:8010 wsgi:app
```

### Docker Setup

```bash
# Build the Docker image
docker build -t tts-server .

# Run the container
docker run -p 8010:8010 tts-server
```

## 💻 Usage

### Environment Variables

| Variable | Description                | Required |
| -------- | -------------------------- | -------- |
| PORT     | Server port number         | Yes      |
| WORKERS  | Number of Gunicorn workers | Yes      |
| THREADS  | Threads per worker         | Yes      |

### 🔌 API Endpoints

**Text-to-Speech Service**

| Endpoint                       | Method | Description                 | Parameters                                |
| ------------------------------ | ------ | --------------------------- | ----------------------------------------- |
| `/tts/tts_file`                | GET    | Convert text to speech file | `id`, `text`, `language`, `model`         |
| `/tts/tts_stream`              | GET    | Stream audio in real-time   | `text`, `language`, `model`               |
| `/tts/tts_stream_chunk_static` | GET    | Stream with static chunks   | `text`, `language`, `model`               |
| `/tts/tts_stream_chunk`        | GET    | Stream with custom chunks   | `text`, `language`, `model`, `chunk_size` |

### 📝 Example Usage

```python
# Using requests to get TTS file
import requests

response = requests.get(
    "http://localhost:8010/tts/tts_file",
    params={
        "id": "user123",
        "text": "Hello World",
        "language": "en",
        "model": "winter"
    }
)

# Save the audio file
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## 🏗️ Project Structure

```
TTS-Server/
├── app/
│   ├── __init__.py    # Application initialization
│   ├── routes.py      # API routes
│   └── xtts_api.py    # TTS core functionality
├── models/            # Voice models
├── test/             # Test files
├── Dockerfile        # Docker configuration
├── requirements.txt  # Python dependencies
└── wsgi.py          # WSGI entry point
```

## 🛠️ Development

```bash
# Development mode
python wsgi.py

# Run tests
python -m pytest

# Build Docker image
docker build -t tts-server .
```

## 📚 API Documentation

Once the application is running, visit:

- Swagger UI: http://localhost:8010/docs

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- XTTS Community
- Flask Team
- Docker Community
- Open Source TTS Community

---
