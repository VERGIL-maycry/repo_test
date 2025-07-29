# Chatbot - Commune de Fès (Python Version)

A bilingual chatbot for the municipality of Fès (Morocco) built with Python Flask, providing information about municipal services and documents in French and Arabic.

## Features

### 🤖 **Smart Chat Interface**
- **Bilingual responses** (French + Arabic)
- **Typing indicator** with animated dots
- **Quick reply buttons** for common questions
- **Smart suggestions** that appear as you type
- **Persistent chat history** (saves your conversation)

### 🎨 **Accessibility & Design**
- **Dark/Light theme toggle** (🌙/☀️)
- **Font size toggle** for visually impaired users (📝/🔍/🔎)
- **Modern, responsive design**
- **Mobile-friendly interface**

### 🧠 **Advanced AI Features**
- **Intent recognition** - Understands what users want
- **Conversation flow** - Multi-step guided processes
- **Follow-up questions** - Contextual assistance
- **Smart suggestions** - Relevant quick reply buttons

### 📋 **Services Covered**
- **Document requests**: Birth certificates, marriage certificates, death certificates
- **Identity documents**: National ID cards, passports
- **Municipal services**: Residence certificates, business permits
- **Practical info**: Opening hours, address, contact numbers
- **Social services**: Aid applications, disability services
- **Urban services**: Waste collection, transport, events

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project files**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
chatbot-fes-python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # HTML template
└── static/
    └── styles.css        # CSS styles
```

## API Endpoints

### POST `/chat`
Send a message to the chatbot.

**Request:**
```json
{
    "question": "Comment obtenir un acte de naissance?",
    "session_id": "session_123"
}
```

**Response:**
```json
{
    "answer": "Pour obtenir un acte de naissance...",
    "buttons": [
        {"text": "Extrait simple", "value": "Extrait simple"},
        {"text": "Copie intégrale", "value": "Copie intégrale"}
    ],
    "in_conversation": true
}
```

### POST `/clear_chat`
Clear the conversation history for a session.

**Request:**
```json
{
    "session_id": "session_123"
}
```

**Response:**
```json
{
    "success": true
}
```

## Key Features Explained

### **Intent Recognition**
The chatbot recognizes user intents using keyword matching:
- Document requests (birth certificates, ID cards, etc.)
- Service inquiries (opening hours, addresses)
- General help requests

### **Conversation Flow**
Multi-step processes guide users through complex requests:
1. **Intent detection** - Understand what the user wants
2. **Follow-up questions** - Gather specific information
3. **Complete response** - Provide detailed requirements
4. **Conversation end** - Offer additional help

### **Dynamic Quick Replies**
Context-aware buttons that change based on the conversation:
- **Regular mode**: General service buttons
- **Conversation mode**: Specific options for current step

### **Session Management**
Each user gets a unique session ID for:
- Conversation state persistence
- Context maintenance across messages
- Independent conversation flows

## Customization

### Adding New Services
1. Add new Q&A pairs to the `qa_pairs` list in `app.py`
2. Update the `recognize_intent()` function for new intents
3. Add conversation flows in `get_follow_up_question()` and `process_conversation_step()`
4. Update button configurations in `get_conversation_buttons()`

### Modifying Styles
Edit `static/styles.css` to customize:
- Color themes
- Font sizes
- Layout and spacing
- Responsive design

### Adding Languages
1. Add new language patterns to intent recognition
2. Include bilingual responses in Q&A pairs
3. Update UI text in `templates/index.html`

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider using:
- **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
- **Docker**: Create a Dockerfile for containerization
- **Cloud platforms**: Deploy to Heroku, AWS, or Google Cloud

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

2. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Static files not loading**
   - Check that `static/` folder exists
   - Verify file permissions

### Debug Mode
The application runs in debug mode by default. For production, set:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**Note**: This is the Python Flask version of the original JavaScript chatbot. All functionality has been preserved and enhanced with server-side processing capabilities. 