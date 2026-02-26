from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import os
import warnings
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Load environment variables from .env file
load_dotenv()

# Step 1: API key is automatically loaded from .env file
# No need to set it manually - load_dotenv() does it for you!

# Step 2: Initialize the Groq LLM with timeout settings
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # You can also try: "llama3-70b-8192"
    temperature=0.7,
    max_tokens=1024,
    timeout=60,  # Increase timeout to 60 seconds
    max_retries=2  # Retry on failure
)

# Step 3: Create memory storage
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Step 4: Create a custom prompt for financial advice
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful financial advisor chatbot. You provide general financial advice 
and answer questions about personal finance, budgeting, saving, and investing.


Rules: Keep it concise and to the point and without using Sterics for headings

Important: Always remind users that you provide general information only and they should 
consult with a licensed financial advisor for personalized advice."""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Step 5: Create the conversation chain with memory
chain = prompt | llm

conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Step 6: Function to chat with the bot
def chat_with_bot():
    print("Financial Advice Chatbot")
    print("=" * 50)
    
    # Test the API connection first
    print("Testing connection to Groq API...")
    try:
        test_response = llm.invoke("Hi")
        print("✓ Connection successful!")
        print()
    except Exception as e:
        print("✗ Connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your API key is correct")
        print("2. Visit https://console.groq.com to verify your key")
        print("3. Check your internet connection")
        print("4. Try again in a few minutes")
        return
    
    print("Ask me anything about personal finance!")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    session_id = "user_session_1"  # Single user session
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thank you for using the Financial Advice Chatbot!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            # Get response from the chatbot with memory
            response = conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            print(f"\nBot: {response.content}\n")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")

# Step 7: Run the chatbot
if __name__ == "__main__":
    chat_with_bot()