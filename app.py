from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Initializ Flask
app = Flask(__name__)

# Configure Gemini with API key
genai.configure(api_key="AIzaSyB_huT2ncc3LuGofGLgJjRyqI8RAYflr54")

# model name
MODEL_NAME = "gemini-1.5-flash"

# Generation config
generation_config = { 
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}

# Storin chat history in good format
conversation_history = []

def generate_response(user_input: str) -> str:
    try:
        print(f"Generating response for: '{user_input}'")
        
        # Initializing Gemini model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config
        )

        if not conversation_history:
            print("Starting new conversation")
            chat = model.start_chat()
        else:
            formatted_history = []
            for msg in conversation_history:
                formatted_history.append({
                    "role": msg["role"],
                    "parts": [msg["parts"]]
                })
            print(f"Using history: {len(formatted_history)} messages")
            chat = model.start_chat(history=formatted_history)

        response = chat.send_message(user_input)
        
        conversation_history.append({"role": "user", "parts": user_input})
        conversation_history.append({"role": "model", "parts": response.text})
        
        print(f"Response generated successfully: {response.text[:100]}...")
        return response.text

    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(error_msg)
        
        # Try simple response without history if there's an error
        try:
            print("Attempting fallback response...")
            model = genai.GenerativeModel(model_name=MODEL_NAME)
            simple_response = model.generate_content(user_input)
            return simple_response.text
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")
            return f"Sorry, I'm having trouble processing your request. Please try again."

@app.route('/')
def home():
    print("Home route accessed")
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("Chat route accessed")
        print(f"Request form: {request.form}")
        
        # Get user input from form
        user_input = request.form.get('user_input')
        if not user_input:
            print("No user input received")
            return jsonify(response="Please enter a message."), 400
        
        print(f"Processing message: '{user_input}'")
        
        # Generate response
        bot_response = generate_response(user_input.strip())
        
        print(f"Sending response: {bot_response[:100]}...")
        return jsonify(response=bot_response)
        
    except Exception as e:
        error_msg = f"Chat endpoint error: {str(e)}"
        print(error_msg)
        return jsonify(response="Sorry, something went wrong. Please try again."), 500

# Test endpoint to verify API working
@app.route('/test')
def test():
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content("Say hello")
        return jsonify(success=True, response=response.text, model=MODEL_NAME)
    except Exception as e:
        return jsonify(success=False, error=str(e), model=MODEL_NAME)

if __name__ == "__main__":
    print(f"Starting Flask app with Gemini model: {MODEL_NAME}")
    print("Testing API connection...")
    
    # Test API on startup
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        test_response = model.generate_content("Test")
        print("API connection successful!")
        print(f"Test response: {test_response.text}")
    except Exception as e:
        print(f"API connection failed: {e}")
        print("The app will start but may not work properly.")
    
    app.run(debug=True, host='127.0.0.1', port=5000)