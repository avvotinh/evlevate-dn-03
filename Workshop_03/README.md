# Entertainment Recommendation Bot - Workshop 03

A simple CLI-based entertainment recommendation bot that suggests TV shows and movies based on user preferences using ChromaDB for vector storage, Azure OpenAI for embeddings and recommendations, and HuggingFace for text-to-speech.

## 🎯 Features

- **Semantic Search**: Uses Azure OpenAI embeddings to understand user preferences and find similar content
- **Vector Storage**: ChromaDB for persistent storage of movie/TV metadata and embeddings
- **Intelligent Recommendations**: Azure OpenAI GPT-4o-mini generates personalized recommendations with explanations
- **Text-to-Speech**: HuggingFace SpeechT5 converts recommendations to audio
- **Rich Database**: Pre-loaded with popular movies and TV shows including ratings and detailed descriptions
- **Interactive CLI**: User-friendly command-line interface with examples and help

## 🏗️ Architecture

The bot uses a Retrieval-Augmented Generation (RAG) architecture adapted for content-based recommendations:

1. **Input Layer**: CLI for user queries (e.g., "Recommend action movies like Inception")
2. **Retrieval Layer**: ChromaDB as vector store for movie/TV metadata with semantic search
3. **Recommendation Layer**: Azure OpenAI Chat Completions for personalized suggestions with reasoning
4. **Output Layer**: Text response + optional audio conversion via HuggingFace TTS

## 📋 Requirements

- Python 3.8+
- Azure OpenAI API access
- Internet connection (for initial model downloads)

## 🚀 Installation

1. **Clone or navigate to the Workshop_03 directory**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Azure OpenAI credentials**:

   Create a `.env` file in the project directory with your Azure OpenAI configuration:

   ```bash
   AZURE_OPENAI_API_BASE=your_azure_endpoint_here
   AZURE_OPENAI_API_VERSION=2024-02-01
   AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key_here
   AZURE_OPENAI_LLM_API_KEY=your_llm_api_key_here
   AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   AZURE_OPENAI_LLM_MODEL=GPT-4o-mini
   ```

## 💡 Usage

### Basic Usage

Run the bot:

```bash
python chatbot.py
```

### Example Queries

- "I want sci-fi movies like Inception"
- "Recommend funny TV shows"
- "Something dark and psychological"
- "Action movies with great ratings"
- "Feel-good movies for tonight"
- "Fantasy series like Game of Thrones"

### Commands

- `help` - Show example queries
- `exit` or `quit` - Exit the bot

## 🎬 Sample Data

The bot comes pre-loaded with popular entertainment content including:

**Movies:**

- Inception (2010) - Sci-fi thriller
- The Matrix (1999) - Action sci-fi
- The Dark Knight (2008) - Superhero action
- Interstellar (2014) - Space epic
- Pulp Fiction (1994) - Crime drama

**TV Shows:**

- Stranger Things (2016) - Horror sci-fi
- Friends (1994) - Comedy sitcom
- Breaking Bad (2008) - Crime drama
- The Office (2005) - Mockumentary comedy
- Game of Thrones (2011) - Epic fantasy

Each entry includes detailed descriptions, genres, ratings, and year information for accurate recommendations.

## 🔧 Technical Details

### Vector Embeddings

- Uses Azure OpenAI's `text-embedding-3-small` model
- Generates embeddings for both content descriptions and user queries
- Enables semantic similarity search for content discovery

### Recommendation Generation

- ChromaDB retrieves top-3 similar items based on vector similarity
- Azure OpenAI GPT-4o-mini analyzes retrieved content and user preferences
- Generates personalized recommendations with explanations

### Text-to-Speech

- HuggingFace SpeechT5 for natural-sounding audio
- Saves recommendations as WAV files with timestamps
- Handles long text truncation for optimal audio quality

### Data Storage

- ChromaDB persistent storage in `./chroma_db` directory
- Maintains embeddings and metadata across sessions
- Automatic initialization with sample data on first run

## 📁 Project Structure

```
Workshop_03/
├── chatbot.py               # Main application
├── sample.json              # Entertainment data
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── chroma_db/              # ChromaDB storage (created on first run)
├── chatbot.log             # Application logs
└── recommendation_*.wav    # Generated audio files
```

## 🔧 Configuration

### Environment Variables

Required Azure OpenAI configuration in `.env` file:

- `AZURE_OPENAI_API_BASE` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION` - API version (e.g., 2024-02-01)
- `AZURE_OPENAI_EMBEDDING_API_KEY` - API key for embedding model
- `AZURE_OPENAI_LLM_API_KEY` - API key for LLM model
- `AZURE_OPENAI_EMBEDDING_MODEL` - Embedding model name (default: text-embedding-3-small)
- `AZURE_OPENAI_LLM_MODEL` - LLM model name (default: GPT-4o-mini)

### Customization Options

- Modify `sample.json` to add more entertainment content
- Adjust `n_results` parameter to change number of similar items retrieved
- Modify Azure OpenAI model parameters (temperature, max_tokens) for different response styles

## 🌟 Best Practices Implemented

1. **Content-Based Filtering**: Uses semantic similarity for cold-start scenarios
2. **Explainable AI**: Provides reasoning for each recommendation
3. **Modular Architecture**: Separates concerns for easy maintenance
4. **Error Handling**: Graceful degradation when components fail
5. **Logging**: Comprehensive logging for debugging and monitoring

## 🎯 Example Interaction

```
🎬 Entertainment Recommendation Bot 🎬
==================================================
I can recommend movies and TV shows based on your preferences!

You: I want something like Inception but maybe a TV show

🤖 Bot: Based on your interest in Inception, I have some fantastic recommendations that share its mind-bending, layered storytelling!

1. **Stranger Things** (2016) - This sci-fi horror series shares Inception's love for alternate realities and mysterious dimensions. Like Inception's dream layers, Stranger Things explores the "Upside Down" - a dark parallel dimension that mirrors our world. The show combines supernatural elements with emotional storytelling, perfect if you enjoyed Inception's blend of high-concept sci-fi and human drama.

2. **The Matrix** (1999) - While technically a movie, this is the closest match to Inception's themes about questioning reality. Both films explore the nature of what's real versus simulated, featuring protagonists who must navigate multiple layers of existence.

3. **For a TV series with similar complexity**: Consider exploring sci-fi shows that play with time, reality, and consciousness - they capture that same "what is real?" feeling that makes Inception so compelling.

🔊 Audio saved as: recommendation_20250809_143022.wav
```

## 🚀 Future Enhancements

- Integration with TMDB API for real-time movie/TV data
- User preference learning and history
- Multi-language support
- Web interface with Flask/FastAPI
- Collaborative filtering for user-based recommendations
- Rating-based filtering options

## 🤝 Contributing

This is a workshop project for learning purposes. Feel free to experiment with:

- Adding more entertainment data
- Implementing new recommendation algorithms
- Enhancing the TTS functionality
- Adding new output formats

## 📝 License

This project is for educational purposes as part of AI Learning Workshop 03.

## 🆘 Troubleshooting

### Common Issues

1. **Azure OpenAI API Key Error**:

   - Ensure your Azure OpenAI credentials are set correctly in `.env` file
   - Check that your Azure OpenAI resource is active and has available quota
   - Verify the model deployments exist in your Azure OpenAI resource

2. **TTS Models Not Loading**:

   - Models download automatically on first use
   - Ensure stable internet connection
   - Check available disk space (models are ~1GB)

3. **ChromaDB Issues**:

   - Delete `./chroma_db` directory to reset database
   - Ensure write permissions in the project directory

4. **Memory Issues**:
   - TTS models require significant RAM
   - Consider running without TTS on limited hardware

### Getting Help

Check the logs in `chatbot.log` for detailed error information.
