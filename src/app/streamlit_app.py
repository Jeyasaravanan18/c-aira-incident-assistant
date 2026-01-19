"""
C-AIRA Streamlit Application
Context-Aware Incident Response Assistant UI
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.config import Config
from src.retrieval.retriever import Retriever
from src.generation.llm_client import LLMClient
from src.generation.prompt_template import create_messages
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="C-AIRA - Incident Response Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = None
    if 'index_loaded' not in st.session_state:
        st.session_state.index_loaded = False
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def load_system():
    """Load retriever and LLM client"""
    try:
        with st.spinner("Loading C-AIRA system..."):
            # Validate configuration
            is_valid, error_msg = Config.validate()
            if not is_valid:
                st.error(f"❌ Configuration Error: {error_msg}")
                st.info("Please ensure your .env file is properly configured with Azure OpenAI credentials.")
                return False
            
            # Initialize retriever
            if st.session_state.retriever is None:
                st.session_state.retriever = Retriever()
            
            # Load index
            if not st.session_state.index_loaded:
                st.session_state.retriever.load_index()
                st.session_state.index_loaded = True
            
            # Initialize LLM client
            if st.session_state.llm_client is None:
                st.session_state.llm_client = LLMClient()
            
            return True
            
    except FileNotFoundError as e:
        st.error("❌ Vector index not found!")
        st.info("Please run the index building script first:")
        st.code("python scripts/build_index.py", language="bash")
        return False
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        logger.error(f"System loading failed: {str(e)}", exc_info=True)
        return False


def display_header():
    """Display application header"""
    st.markdown('<div class="main-header">🔧 C-AIRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Context-Aware Incident Response Assistant</div>', unsafe_allow_html=True)
    st.markdown("---")


def display_sidebar():
    """Display sidebar with information and settings"""
    with st.sidebar:
        st.header("About C-AIRA")
        st.write("""
        C-AIRA is an AI-powered assistant that helps IT support and DevOps teams 
        resolve operational incidents faster by retrieving relevant internal 
        documents and generating accurate, step-by-step resolution guidance.
        """)
        
        st.markdown("---")
        
        st.header("How It Works")
        st.write("""
        1. **Describe your incident** in the text area
        2. **Submit** your query
        3. **Review** the AI-generated resolution steps
        4. **Check sources** for detailed documentation
        """)
        
        st.markdown("---")
        
        st.header("Settings")
        
        top_k = st.slider(
            "Number of sources to retrieve",
            min_value=1,
            max_value=10,
            value=Config.TOP_K_RESULTS,
            help="How many relevant documents to retrieve"
        )
        
        temperature = st.slider(
            "Response creativity",
            min_value=0.0,
            max_value=1.0,
            value=Config.LLM_TEMPERATURE,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        
        st.markdown("---")
        
        # System status
        st.header("System Status")
        if st.session_state.index_loaded:
            st.success("✅ Index Loaded")
            stats = st.session_state.retriever.vector_store.get_stats()
            st.metric("Total Documents", stats.get('total_vectors', 'N/A'))
        else:
            st.warning("⚠️ Index Not Loaded")
        
        return top_k, temperature


def display_query_interface(top_k, temperature):
    """Display query input interface"""
    st.header("Describe Your Incident")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.write("""
        - "Database connection timeout errors in production"
        - "Users unable to log in, getting 401 errors"
        - "Server disk space full, deployment failing"
        - "API response times very slow"
        - "Authentication service returning invalid token errors"
        """)
    
    # Query input
    query = st.text_area(
        "Incident Description",
        height=150,
        placeholder="Describe the incident, error messages, symptoms, or paste log snippets here...",
        help="Provide as much detail as possible for better results"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        submit_button = st.button("🔍 Get Resolution", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    return query, submit_button, top_k, temperature


def process_query(query, top_k, temperature):
    """Process user query and display results"""
    if not query.strip():
        st.warning("⚠️ Please enter an incident description")
        return
    
    try:
        # Add to history
        st.session_state.query_history.append({
            'query': query,
            'timestamp': datetime.now()
        })
        
        # Retrieve context
        with st.spinner("🔍 Searching knowledge base..."):
            retrieval_result = st.session_state.retriever.retrieve(query, top_k=top_k)
        
        if not retrieval_result.chunks:
            st.warning("⚠️ No relevant information found in the knowledge base.")
            st.info("Try rephrasing your query or check if the relevant documentation has been indexed.")
            return
        
        # Display retrieved sources
        with st.expander(f"📚 Retrieved {len(retrieval_result.chunks)} Relevant Sources", expanded=False):
            for i, chunk in enumerate(retrieval_result.chunks, 1):
                metadata = chunk['metadata']
                with st.container():
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {i}:</strong> {metadata['filename']}<br>
                        <strong>Type:</strong> {metadata['doc_type']}<br>
                        <strong>Relevance:</strong> {chunk['similarity']:.1%}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show snippet
                    chunk_text = metadata.get('chunk_text', '')
                    if chunk_text:
                        st.text(chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text)
                    st.markdown("---")
        
        # Generate response
        with st.spinner("🤖 Generating resolution guidance..."):
            messages = create_messages(query, retrieval_result.context)
            response = st.session_state.llm_client.generate(
                messages,
                temperature=temperature
            )
        
        # Display response
        st.markdown("### 📋 Resolution Guidance")
        st.markdown(response)
        
        # Display sources summary
        st.markdown("### 📖 Sources Referenced")
        sources = retrieval_result.get_sources()
        for source in sources:
            st.markdown(f"- `{source}`")
        
        # Success message
        st.success("✅ Resolution guidance generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error processing query: {str(e)}")
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)


def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    
    # Load system
    if not load_system():
        st.stop()
    
    # Display sidebar and get settings
    top_k, temperature = display_sidebar()
    
    # Display query interface
    query, submit_button, top_k, temperature = display_query_interface(top_k, temperature)
    
    # Process query
    if submit_button:
        process_query(query, top_k, temperature)
    
    # Query history
    if st.session_state.query_history:
        with st.sidebar:
            st.markdown("---")
            st.header("Recent Queries")
            for item in reversed(st.session_state.query_history[-5:]):
                st.text(f"• {item['query'][:50]}...")


if __name__ == "__main__":
    main()
