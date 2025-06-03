#backend server for legal chatbot
from flask import Flask, request, jsonify
from flask_cors import CORS
from legal_chatbot_logic.qa_logic import qa_pipeline
import os

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080","http://localhost:5173"],  # Your frontend URL
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize QA pipeline
qa_chain = qa_pipeline()

# Add this at the top of your file
GREETINGS = [
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
    "how are you", "what's up", "yo", "greetings"
]

SMALL_TALK = [
    "how are you", "how's it going", "what's up", "how do you do", "how are you doing"
]

@app.route("/api/chat", methods=["POST"])
def chat():
    if not qa_chain:
        return jsonify({
            "error": "Chatbot not initialized properly"
        }), 500
    
    try:
        # Get request data
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({
                "error": "Message is required"
            }), 400
        
        user_message = data["message"].strip().lower()

        # Handle greetings
        if any(greet in user_message for greet in GREETINGS):
            return jsonify({
                "answer": "Hello! How can I assist you with your legal questions today?",
                "sources": []
            })

        # Handle small talk
        if any(talk in user_message for talk in SMALL_TALK):
            return jsonify({
                "answer": "I'm here to help you with legal matters. Please let me know your legal question or concern!",
                "sources": []
            })

        # Otherwise, use the QA pipeline
        response = qa_chain.invoke({"query": data["message"]})
        
        # Format sources
        sources = []
        if response.get("source_documents"):
            for doc in response["source_documents"]:
                sources.append({
                    "source": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page', 'N/A')
                })
        
        return jsonify({
            "answer": response["result"],
            "sources": sources
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 