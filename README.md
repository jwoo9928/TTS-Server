# TTS-Server 🎙️

<div align="center">

![TTS Server Banner](https://raw.githubusercontent.com/username/TTS-Server/main/assets/banner.png)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

_A high-performance Text-to-Speech API server with streaming capabilities and multiple voice models support_

[Features](#features) • [Quick Start](#quick-start) • [API Documentation](#api-documentation) • [Docker](#docker-deployment) • [Contributing](#contributing)

</div>

## 🌟 Features

- 🚀 High-performance TTS conversion
- 🔄 Real-time streaming support
- 🌐 Multiple language support
- 🎭 Multiple voice model support
- 🔧 Configurable chunk sizes for streaming
- 📚 Swagger documentation
- 🐳 Docker support
- 🔒 Thread-safe model instance management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Docker

### Installation

1. Clone the repository:

```bash
git clone https://github.com/username/TTS-Server.git
cd TTS-Server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place your voice models in the `models` directory:

```bash
models/
  ├── winter.wav
  └── other_models.wav
```

4. Start the server:

```bash
gunicorn -w 2 --worker-class gthread --threads 2 -b 0.0.0.0:8010 wsgi:app
```

## 📚 API Documentation

Access the Swagger documentation at `/docs` endpoint after starting the server.

### Available Endpoints

| Endpoint                       | Method | Description                                  | Parameters                                |
| ------------------------------ | ------ | -------------------------------------------- | ----------------------------------------- |
| `/tts/tts_file`                | GET    | Convert text to speech and return audio file | `id`, `text`, `language`, `model`         |
| `/tts/tts_stream`              | GET    | Stream audio in real-time                    | `text`, `language`, `model`               |
| `/tts/tts_stream_chunk_static` | GET    | Stream audio with static chunks              | `text`, `language`, `model`               |
| `/tts/tts_stream_chunk`        | GET    | Stream audio with configurable chunks        | `text`, `language`, `model`, `chunk_size` |

### Example Request

```bash
curl -X GET "http://localhost:8010/tts/tts_file?id=user123&text=Hello%20World&language=en&model=winter"
```

## 🐳 Docker Deployment

1. Build the Docker image:

```bash
docker build -t tts-server .
```

2. Run the container:

```bash
docker run -p 8010:8010 tts-server
```

## 🔧 Configuration

The server can be configured through environment variables:

| Variable  | Description                | Default |
| --------- | -------------------------- | ------- |
| `PORT`    | Server port                | 8010    |
| `WORKERS` | Number of Gunicorn workers | 2       |
| `THREADS` | Threads per worker         | 2       |

## 🎯 Performance Optimization

- Singleton pattern for model instances
- Thread-safe operations
- Optimized memory usage
- Efficient streaming with configurable chunk sizes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Special thanks to the open-source TTS community

---
