import os
import logging
import chromadb
from openai import AzureOpenAI
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile
import torch
import soundfile as sf
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log')
    ]
)
logger = logging.getLogger(__name__)

class EntertainmentBot:
    def __init__(self):
        """Initialize the entertainment recommendation bot."""
        # Load Azure OpenAI configuration from environment
        self.azure_api_base = os.getenv('AZURE_OPENAI_API_BASE')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        self.embedding_api_key = os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY')
        self.llm_api_key = os.getenv('AZURE_OPENAI_LLM_API_KEY')
        self.embedding_model = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        self.llm_model = os.getenv('AZURE_OPENAI_LLM_MODEL', 'GPT-4o-mini')
        
        # Initialize Azure OpenAI clients
        self.embedding_client = AzureOpenAI(
            api_key=self.embedding_api_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_api_base
        )
        
        self.llm_client = AzureOpenAI(
            api_key=self.llm_api_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_api_base
        )
        
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="entertainment_knowledge")
        
        # Initialize TTS components
        self.tts_model = None
        self.tts_tokenizer = None
        
        logger.info("Entertainment Bot initialized successfully")
        
    def initialize_tts(self):
        """Initialize Text-to-Speech models using Facebook MMS TTS."""
        try:
            logger.info("Loading MMS TTS models...")
            
            # Load Facebook MMS TTS model and tokenizer
            self.tts_model = VitsModel.from_pretrained("facebook/mms-tts-eng")
            self.tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
            
            logger.info("MMS TTS models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS models: {e}")
            logger.info("Bot will continue without TTS functionality")
            self.tts_model = None
            self.tts_tokenizer = None
    
    def load_sample_data(self):
        """Load sample entertainment data into ChromaDB if collection is empty."""
        if self.collection.count() == 0:
            logger.info("Loading sample entertainment data...")
            
            try:
                with open('sample.json', 'r', encoding='utf-8') as f:
                    entertainment_data = json.load(f)
                logger.info(f"Loaded {len(entertainment_data)} items from sample.json")
            except FileNotFoundError:
                logger.warning("sample.json not found, using fallback data")
                entertainment_data = [
                    {
                        "title": "Inception",
                        "type": "Movie",
                        "description": "Sci-fi action thriller about dream invasion and layered reality. Directed by Christopher Nolan. A skilled thief enters people's dreams to steal secrets but is tasked with planting an idea instead.",
                        "genres": ["Action", "Sci-Fi", "Thriller"],
                        "year": 2010,
                        "rating": 8.8
                    },
                    {
                        "title": "Stranger Things",
                        "type": "TV Show",
                        "description": "Horror sci-fi series about kids in a small town facing supernatural events from an alternate dimension called the Upside Down. Set in the 1980s with nostalgic references.",
                        "genres": ["Horror", "Sci-Fi", "Drama"],
                        "year": 2016,
                        "rating": 8.7
                    },
                    {
                        "title": "The Matrix",
                        "type": "Movie",
                        "description": "Action sci-fi with philosophical themes about reality and simulation. Neo discovers the world is a computer simulation and joins a rebellion against machine overlords.",
                        "genres": ["Action", "Sci-Fi"],
                        "year": 1999,
                        "rating": 8.7
                    },
                    {
                        "title": "Friends",
                        "type": "TV Show",
                        "description": "Comedy sitcom about six friends living in New York City, dealing with relationships, careers, and everyday life with humor and heart.",
                        "genres": ["Comedy", "Romance"],
                        "year": 1994,
                        "rating": 8.9
                    },
                    {
                        "title": "Breaking Bad",
                        "type": "TV Show",
                        "description": "Crime drama about a high school chemistry teacher who turns to cooking methamphetamine after being diagnosed with cancer to secure his family's future.",
                        "genres": ["Crime", "Drama", "Thriller"],
                        "year": 2008,
                        "rating": 9.5
                    }
                ]
            
            # Create text representations for embedding
            documents = []
            metadata = []
            ids = []
            
            for i, item in enumerate(entertainment_data):
                # Create rich text description for embedding
                text = f"{item['type']}: {item['title']} - {item['description']} Genres: {', '.join(item['genres'])}. Year: {item['year']}. Rating: {item['rating']}/10"
                documents.append(text)
                
                # Convert list to string for ChromaDB compatibility
                item_metadata = item.copy()
                item_metadata['genres'] = ', '.join(item['genres'])  # Convert list to comma-separated string
                metadata.append(item_metadata)
                ids.append(f"item_{i}")
            
            # Generate embeddings
            logger.info("Generating embeddings for entertainment data...")
            embeddings = []
            for doc in documents:
                response = self.embedding_client.embeddings.create(
                    input=doc,
                    model=self.embedding_model
                )
                embeddings.append(response.data[0].embedding)
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Added {len(entertainment_data)} entertainment items to database")
        else:
            logger.info(f"Database already contains {self.collection.count()} items")
    
    def search_similar_content(self, user_query, n_results=3):
        """Search for similar entertainment content based on user query."""
        try:
            # Generate embedding for user query
            response = self.embedding_client.embeddings.create(
                input=user_query,
                model=self.embedding_model
            )
            query_embedding = response.data[0].embedding
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            return results
        except Exception as e:
            logger.error(f"Error searching for similar content: {e}")
            return None
    
    def generate_recommendation(self, user_input):
        """Generate personalized entertainment recommendations."""
        try:
            # Search for similar content
            search_results = self.search_similar_content(user_input)
            
            if not search_results or not search_results['documents']:
                return "I couldn't find any matching content. Try describing the type of movies or TV shows you like!"
            
            # Prepare context from search results
            retrieved_items = []
            for i, (doc, metadata) in enumerate(zip(search_results['documents'][0], search_results['metadatas'][0])):
                retrieved_items.append({
                    'title': metadata['title'],
                    'type': metadata['type'],
                    'description': metadata['description'],
                    'genres': metadata['genres'],  # Now a string instead of list
                    'year': metadata['year'],
                    'rating': metadata['rating']
                })
            
            # Create context for the LLM
            context = "Based on your preferences, here are some relevant items from my database:\n"
            for item in retrieved_items:
                context += f"- {item['type']}: {item['title']} ({item['year']}) - {item['description']} [Genres: {item['genres']}, Rating: {item['rating']}/10]\n"
            
            # Create prompt for personalized recommendations
            prompt = f"""You are an entertainment recommendation bot. Based on the user's preferences and the similar content found, provide 2-3 personalized recommendations.

Create a natural, conversational response that introduces the recommendations. Include the titles in your response but make it sound natural and engaging.

Example format: "Based on your interests, I recommend checking out [Title 1], [Title 2], and [Title 3]. These should be perfect for what you're looking for!"

User's request: {user_input}

{context}
"""

            # Generate recommendation using Azure OpenAI
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a friendly entertainment recommendation bot. Create natural, conversational responses that include movie/TV show titles in an engaging way. Keep responses concise but warm."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content
            
            # Log the interaction
            logger.info(f"Generated recommendation for query: {user_input[:50]}...")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return f"Sorry, I encountered an error while generating recommendations: {str(e)}"
    
    def text_to_speech(self, text, filename=None):
        """Convert text to speech and save as audio file using MMS TTS."""
        if not self.tts_model or not self.tts_tokenizer:
            logger.warning("TTS not initialized. Skipping audio generation.")
            return None
        
        try:
            # Create results directory if it doesn't exist
            results_dir = "results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recommendation_{timestamp}.wav"
            
            # Add results directory to filename path
            filename = os.path.join(results_dir, filename)
            
            print(f"Text: {text}")
            print("Generating audio...")
            
            # Convert text to tokens
            inputs = self.tts_tokenizer(text, return_tensors="pt")
            
            # Generate audio
            with torch.no_grad():
                output = self.tts_model(**inputs)
                waveform = output.waveform
            
            # Convert to numpy array
            audio_array = waveform.squeeze().cpu().numpy()
            sampling_rate = self.tts_model.config.sampling_rate
            
            print("✓ Audio generated successfully!")
            print(f"Audio duration: {len(audio_array) / sampling_rate:.2f} seconds")
            
            # Save audio file using scipy
            scipy.io.wavfile.write(filename, sampling_rate, audio_array)
            
            logger.info(f"Audio saved as {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def run_cli(self):
        """Run the CLI interface for the entertainment bot."""
        print("🎬 Entertainment Recommendation Bot 🎬")
        print("=" * 50)
        print("I can recommend movies and TV shows based on your preferences!")
        print("Examples:")
        print("- 'I want sci-fi movies like Inception'")
        print("- 'Recommend funny TV shows'")
        print("- 'Something dark and psychological'")
        print("- 'Action movies with great ratings'")
        print("\nType 'exit' to quit, 'help' for more examples")
        print("=" * 50)
        
        # Initialize TTS (optional)
        try:
            self.initialize_tts()
            if self.tts_model and self.tts_tokenizer:
                print("🔊 Text-to-speech enabled! Recommendations will be saved as audio files.")
            else:
                print("⚠️  Text-to-speech disabled (MMS TTS models not available)")
                print("   Installing required models in background...")
        except Exception as e:
            print("⚠️  Text-to-speech not available (continuing without audio)")
            logger.error(f"TTS initialization error: {e}")
        
        # Load sample data
        self.load_sample_data()
        
        print("\n🤖 Bot is ready! What kind of entertainment are you looking for?")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Thanks for using the Entertainment Bot! Happy watching!")
                    break
                
                if user_input.lower() == 'help':
                    print("\n💡 Example queries:")
                    print("- 'Recommend movies like The Matrix'")
                    print("- 'I want comedy TV shows'")
                    print("- 'Something with high ratings'")
                    print("- 'Dark psychological thrillers'")
                    print("- 'Fantasy series like Game of Thrones'")
                    print("- 'Feel-good movies for tonight'")
                    continue
                
                if not user_input:
                    print("Please tell me what you're looking for!")
                    continue
                
                print("\n🤔 Let me find some great recommendations for you...")
                
                # Generate recommendation
                recommendation = self.generate_recommendation(user_input)
                
                print(f"\n🤖 Bot: {recommendation}")

                logger.info(f"TTS Model available: {self.tts_model is not None}")
                
                # Generate audio if TTS is available
                if self.tts_model and self.tts_tokenizer:
                    print("\n🔊 Generating audio...")
                    audio_file = self.text_to_speech(recommendation)
                    if audio_file:
                        print(f"💾 Audio saved as: {audio_file}")
                    else:
                        print("⚠️  Audio generation failed")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in CLI: {e}")
                print(f"❌ Sorry, something went wrong: {e}")

def main():
    """Main function to run the entertainment bot."""
    try:
        # Create and run the bot
        bot = EntertainmentBot()
        bot.run_cli()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Failed to start the bot: {e}")

if __name__ == "__main__":
    main()
