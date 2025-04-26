# 🗣️ FAAC Backend

## 📋 Overview

FAAC (Fast Augmentative and Alternative Communication) Backend is a robust API service designed to support AAC applications for non-verbal individuals, particularly children with autism. This backend provides essential services for generating, managing, and delivering AAC resources including pictograms, audio files, and keyword management.

## ✨ Features

- 🖼️ **Pictogram Generation**: Create clear, accessible pictograms using multiple AI providers:
  - OpenAI DALL-E
  - Google Imagen
  - Ideogram
  - OpenSymbols integration

- 🔊 **Voice Generation**: Generate high-quality speech for AAC symbols:
  - ElevenLabs integration for realistic voices
  - Support for multiple languages and voice types (male/female)
  - Flemish language support

- 🔑 **Keyword Management**: Comprehensive keyword database with:
  - CRUD operations for keyword entries
  - Association with pictograms and audio files
  - Search and filtering capabilities
  
- ☁️ **Cloud Storage**: Efficient asset management:
  - Digital Ocean Spaces integration
  - Secure URL generation for assets
  - Background removal for pictograms

## 🛠️ Technologies

- **Framework**: FastAPI
- **Database**: PostgreSQL (via Supabase)
- **AI Services**:
  - OpenAI (DALL-E)
  - Google AI (Imagen)
  - ElevenLabs (Voice synthesis)
  - Ideogram
- **Storage**: Digital Ocean Spaces
- **Deployment**: Docker containerization

## 🔧 Setup & Installation

### Prerequisites

- Python 3.13+
- PostgreSQL database
- API keys for OpenAI, Google AI, ElevenLabs, etc.
- Digital Ocean Spaces account (or compatible S3 storage)

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/faac-backend.git
   cd faac-backend
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. Create a `.env` file with the following variables:

   ```
   # API Keys
   OPENAI_API_KEY=your_openai_key
   GOOGLE_API_KEY=your_google_key
   ELEVEN_LABS_API_KEY=your_elevenlabs_key
   IDEOGRAM_API_KEY=your_ideogram_key
   OPEN_SYMBOLS_SECRET_KEY=your_opensymbols_key
   ADMIN_API_KEY=your_admin_key

   # Digital Ocean
   SPACES_KEY=your_spaces_key
   SPACES_SECRET=your_spaces_secret
   BUCKET=your_bucket_name
   REGION=your_region

   # Database - Supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### Database Setup

Create the necessary database tables:

```bash
psql -U your_username -d your_database -f create_tables.sql
```

### Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload
```

Or use the Makefile:

```bash
make run
```

### Docker Deployment

Build and run with Docker:

```bash
docker build -t faac-backend .
docker run -p 8000:8000 -d --env-file .env faac-backend
```

## 🔌 API Endpoints

### Keyword API

- `GET /api/v1/keywords` - List all keywords
- `GET /api/v1/keywords/{id}` - Get specific keyword
- `POST /api/v1/keywords` - Create a new keyword
- `PUT /api/v1/keywords/{id}` - Update a keyword
- `DELETE /api/v1/keywords/{id}` - Delete a keyword

### Pictogram API

- `POST /pictogram/generate/{provider}` - Generate pictogram using specified provider
- `GET /pictogram/{id}` - Get a specific pictogram
- `GET /pictogram/search/{query}` - Search for pictograms

### Voice API

- `POST /voice/generate` - Generate voice audio for text
- `POST /voice/generate/flemish` - Generate Flemish voice audio for text

## 📁 Project Structure

```
faac-backend/
├── app/                       # Main application package
│   ├── api/                   # API routes
│   ├── core/                  # Core configuration
│   ├── models/                # Data models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── utils/                 # Utility functions
├── create_tables.sql          # SQL for creating database tables
├── Dockerfile                 # Docker configuration
├── Makefile                   # Makefile for common commands
└── pyproject.toml             # Project dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- This project is part of a larger effort to create accessible AAC tools for non-verbal individuals
- Special thanks to all the AI providers for making their APIs available for this important cause
