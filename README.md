# AI-Powered Interactive Quiz System

A beautiful, interactive quiz system that uses AI to generate questions from your course chapter content. Perfect for course certification websites!

## 🌟 Features

- **AI-Generated Questions**: Uses OpenAI or Anthropic APIs to create questions from your content
- **Beautiful UI**: Modern, responsive design that works on all devices
- **Real-time Feedback**: Instant feedback with explanations for each answer
- **Progress Tracking**: Visual progress bar and score tracking
- **Easy Integration**: Simple to integrate into existing websites
- **Fallback System**: Works even if AI APIs are unavailable

## 🚀 Quick Start

### Step 1: Run the Setup Script
```bash
python setup.py
```

### Step 2: Get an API Key
Choose one of these AI providers:
- **OpenAI** (Recommended): https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

### Step 3: Configure Your API Key
Edit the `.env` file and add your API key:
```
OPENAI_API_KEY=your_actual_key_here
```

### Step 4: Start the Server
```bash
python server.py
```

### Step 5: Open Your Quiz
Go to: http://localhost:5000

## 📁 File Structure

```
quiz-system/
├── index.html          # Main quiz interface
├── styles.css          # Beautiful styling
├── script.js           # Quiz logic and AI integration
├── server.py           # Backend server with AI APIs
├── requirements.txt    # Python dependencies
├── setup.py           # Easy setup script
└── README.md          # This file
```

## 🔧 How to Use Your Own Chapter Content

1. Open `script.js`
2. Find the `getChapterContent()` function
3. Replace the sample content with your chapter text
4. Save and refresh your quiz

Example:
```javascript
getChapterContent() {
    return `
    Your Chapter Title
    
    Your chapter content goes here...
    Include all the important concepts, definitions, and information
    that you want the AI to create questions about.
    `;
}
```

## 🎨 Customization

### Changing the Number of Questions
In `script.js`, modify:
```javascript
this.totalQuestions = 5; // Change this number
```

### Styling
Edit `styles.css` to match your website's design:
- Colors: Change the gradient backgrounds
- Fonts: Modify the font-family
- Layout: Adjust spacing and sizing

### Adding More AI Providers
The system supports both OpenAI and Anthropic. To add more:
1. Add the API integration in `server.py`
2. Update the `AIQuizGenerator` class
3. Add the new provider to the configuration

## 🔒 Security Notes

- **Never commit your API keys** to version control
- The `.env` file is already in `.gitignore`
- API keys are stored as environment variables
- The backend handles all AI requests securely

## 🌐 Integration into Your Website

### Option 1: Direct Integration
Copy these files to your website:
- `index.html`
- `styles.css` 
- `script.js`

### Option 2: Iframe Embed
```html
<iframe src="http://your-domain.com/quiz" width="800" height="600"></iframe>
```

### Option 3: API Integration
Use the `/api/generate-questions` endpoint to generate questions in your own application.

## 🐛 Troubleshooting

### "No AI API keys configured"
- Make sure you've added your API key to the `.env` file
- Restart the server after adding the key

### "Failed to generate questions"
- Check your API key is correct
- Ensure you have credits/usage remaining
- The system will fall back to sample questions

### Quiz not loading
- Make sure the server is running (`python server.py`)
- Check the browser console for errors
- Try refreshing the page

## 📞 Support

If you need help:
1. Check the troubleshooting section above
2. Look at the browser console for error messages
3. Make sure all dependencies are installed

## 🎯 Next Steps

Once you have the basic system working:
1. Add more chapter content
2. Customize the styling to match your brand
3. Add user authentication if needed
4. Implement score tracking and analytics
5. Add more question types (true/false, fill-in-the-blank)

## 📄 License

This project is open source and free to use for educational and commercial purposes.

---

**Happy Quizzing! 🎉**


