# Deployment Guide - Chatbot Commune de Fès

## 🚀 Quick Deploy to Vercel

### Method 1: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy from project directory**:
   ```bash
   cd Chatbot1
   vercel --prod
   ```

3. **Set environment variables**:
   ```bash
   vercel env add SECRET_KEY production
   # Enter a secure random string (e.g., use: python -c "import secrets; print(secrets.token_hex(32))")
   ```

### Method 2: Vercel Dashboard

1. **Connect repository** to Vercel dashboard
2. **Add environment variables**:
   - `SECRET_KEY`: Your secure secret key
3. **Deploy** automatically

## 📋 Pre-deployment Checklist

- ✅ `vercel.json` configured for Python
- ✅ `requirements.txt` includes all dependencies
- ✅ Environment variables configured
- ✅ Static files in `/static` directory
- ✅ Templates in `/templates` directory
- ✅ Security headers implemented
- ✅ Rate limiting configured
- ✅ Error handling in place

## 🔧 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask session secret | Yes | `your-secret-key-here` |
| `PORT` | Server port | No | `5000` |

## 🏗️ Project Structure

```
Chatbot1/
├── app.py              # Main Flask application
├── vercel.json         # Vercel deployment config
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
├── README.md          # Project documentation
├── DEPLOYMENT.md      # This deployment guide
├── templates/
│   └── index.html     # HTML template with meta tags
└── static/
    └── styles.css     # Optimized CSS with responsive design
```

## 🔒 Security Features

- **Environment-based secret key management**
- **Input validation and sanitization**
- **Rate limiting (20 requests per 5 minutes per session)**
- **Security headers (XSS, clickjacking, content-type protection)**
- **Session-based state management**

## 📱 Features Ready for Production

- **Responsive design** for all devices
- **Accessibility features** (font size controls, high contrast support)
- **Bilingual support** (French/Arabic)
- **Error handling** with graceful fallbacks
- **SEO optimization** with proper meta tags
- **Performance optimized** CSS and HTML

## 🚦 Testing Deployment

After deployment, test these features:

1. **Basic chat functionality**
2. **Theme switching** (dark/light)
3. **Font size controls**
4. **Quick reply buttons**
5. **Conversation flows**
6. **Mobile responsiveness**
7. **Rate limiting** (try rapid requests)

## 🔗 Expected URLs

- **Production**: `https://your-project.vercel.app`
- **Health check**: Visit the URL to see the chatbot interface

## 🛠️ Troubleshooting

### Common Deployment Issues

1. **Build fails**: Check `requirements.txt` syntax
2. **500 errors**: Verify `SECRET_KEY` environment variable
3. **Static files not found**: Ensure files are in `/static` directory
4. **Rate limiting too strict**: Adjust limits in `app.py`

### Vercel Specific

- Verify Python runtime is detected
- Check function logs in Vercel dashboard
- Ensure environment variables are properly set

## 📈 Post-Deployment

### Monitoring
- Check Vercel analytics dashboard
- Monitor error logs
- Track response times

### Updates
- Deploy updates with `vercel --prod`
- Test in preview environment first

---

**Ready for production!** 🎉

The chatbot is now production-ready with all security features, responsive design, and proper error handling implemented.