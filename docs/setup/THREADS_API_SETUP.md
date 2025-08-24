# Threads API Setup Guide

## 🚀 **Meta Threads API Integration**

Kolekt now supports Meta's official Threads API! This guide will help you set up the integration.

## 📋 **Prerequisites**

- Meta Developer Account
- Instagram Business or Creator Account
- Threads account connected to your Instagram account

## 🔧 **Step 1: Meta Developer Setup**

### **1.1 Create Meta Developer Account**

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Click "Get Started" or "Log In"
3. Complete the developer verification process
4. Accept the Meta Developer Terms

### **1.2 Create a New App**

1. In the Developer Console, click "Create App"
2. Select "Business" as the app type
3. Fill in your app details:
   - **App Name**: Kolekt
   - **App Contact Email**: your-email@domain.com
   - **Business Account**: Select your business account (if applicable)

## 🔗 **Step 2: Configure Instagram Basic Display API**

### **2.1 Enable Instagram Basic Display API**

1. In your app dashboard, go to "Add Products"
2. Find "Instagram Basic Display" and click "Set Up"
3. Follow the setup wizard

### **2.2 Configure App Settings**

1. Go to "App Settings" > "Basic"
2. Add your app domain and privacy policy URL
3. Save changes

### **2.3 Add Instagram Test Users**

1. Go to "Instagram Basic Display" > "Roles"
2. Add yourself as an Instagram Test User
3. Accept the invitation from your Instagram account

## 🔑 **Step 3: Generate Access Tokens**

### **3.1 Create Access Token**

1. Go to "Instagram Basic Display" > "Basic Display"
2. Click "Generate Token"
3. Select the required permissions:
   - `user_profile`
   - `user_media`
   - `instagram_basic`
   - `instagram_content_publish` (for posting)

### **3.2 Get App Credentials**

1. Go to "App Settings" > "Basic"
2. Copy your **App ID** and **App Secret**
3. Save your **Access Token** from the previous step

## ⚙️ **Step 4: Configure Kolekt**

### **4.1 Update Environment Variables**

Add your Threads API credentials to your `.env` file:

```bash
# Threads API Configuration
THREADS_API_KEY=your-app-id-here
THREADS_API_SECRET=your-app-secret-here
THREADS_ACCESS_TOKEN=your-access-token-here
THREADS_ACCESS_TOKEN_SECRET=your-access-token-secret-here
```

### **4.2 Test the Connection**

1. Start your Kolekt application
2. Go to the Threads API section in the UI
3. Click "Test Connection"
4. Verify that the connection is successful

## 📱 **Step 5: Connect Your Threads Account**

### **5.1 Authorize Your Account**

1. In Kolekt, go to "Threads Integration"
2. Click "Connect Threads Account"
3. Follow the OAuth flow to authorize Kolekt
4. Grant the required permissions

### **5.2 Verify Permissions**

Make sure your account has the following permissions:
- ✅ Read profile information
- ✅ Read media content
- ✅ Publish media content
- ✅ Manage comments (optional)

## 🚀 **Step 6: Test Threadstorm Publishing**

### **6.1 Create a Test Threadstorm**

1. Go to the Kolekt formatter
2. Enter some test content
3. Format it into a kolekt
4. Click "Publish to Threads"

### **6.2 Verify Publication**

1. Check your Threads account
2. Verify that the posts were published correctly
3. Check the formatting and image placement

## 🔧 **Step 7: Production Configuration**

### **7.1 App Review (Required for Production)**

1. Go to "App Review" in your Meta Developer Console
2. Submit your app for review
3. Provide detailed information about how you'll use the API
4. Wait for Meta's approval (can take 1-2 weeks)

### **7.2 Webhook Configuration (Optional)**

For real-time updates, configure webhooks:

1. Go to "Instagram Basic Display" > "Webhooks"
2. Add your webhook URL: `https://yourdomain.com/api/v1/threads/webhook`
3. Subscribe to events:
   - `media_publish`
   - `media_update`
   - `media_delete`

### **7.3 Rate Limiting**

Be aware of Meta's rate limits:
- **Default**: 200 requests per hour per user
- **Business**: 1000 requests per hour per user
- **Enterprise**: Custom limits available

## 🛠️ **Step 8: Troubleshooting**

### **Common Issues**

**"Invalid Access Token"**
- Check that your access token is valid and not expired
- Regenerate the token if necessary
- Ensure the token has the correct permissions

**"Permission Denied"**
- Verify that your app has been approved for the required permissions
- Check that your Instagram account is connected to Threads
- Ensure you're using a Business or Creator account

**"Rate Limit Exceeded"**
- Implement proper rate limiting in your application
- Use exponential backoff for retries
- Consider upgrading to a Business account for higher limits

**"Media Upload Failed"**
- Check that image URLs are publicly accessible
- Verify image formats are supported (JPG, PNG, GIF)
- Ensure images meet size requirements (max 8MB)

### **Debug Mode**

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

This will provide detailed information about API requests and responses.

## 📊 **Step 9: Monitoring and Analytics**

### **9.1 Track API Usage**

Kolekt automatically tracks:
- API call frequency
- Response times
- Error rates
- User engagement metrics

### **9.2 Monitor Performance**

1. Check the Threads API status in the UI
2. Monitor response times
3. Track success/failure rates
4. Set up alerts for API issues

## 🔒 **Step 10: Security Best Practices**

### **10.1 Token Security**

- Store tokens securely (use environment variables)
- Rotate tokens regularly
- Never commit tokens to version control
- Use different tokens for development and production

### **10.2 Data Privacy**

- Only request necessary permissions
- Implement proper data retention policies
- Follow GDPR and other privacy regulations
- Provide clear privacy notices to users

## 🎯 **Next Steps**

1. **Test thoroughly** with your own account
2. **Monitor performance** and adjust rate limiting
3. **Implement error handling** for edge cases
4. **Add user onboarding** for Threads integration
5. **Consider advanced features** like scheduling and analytics

## 📞 **Support**

If you encounter issues:

1. Check the [Meta Developer Documentation](https://developers.facebook.com/docs/instagram-basic-display-api/)
2. Review the [Threads API Reference](https://developers.facebook.com/docs/instagram-api/reference/)
3. Contact Meta Developer Support
4. Check Kolekt logs for detailed error information

Your Kolekt is now ready to publish directly to Threads! 🚀
