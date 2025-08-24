# Kolekt Admin Panel Setup Guide

## Overview

The Kolekt Admin Panel provides comprehensive site administration capabilities including user management, announcement publishing, and system monitoring. This guide will help you set up and use the admin panel.

## 🔧 Setup Requirements

### Prerequisites
- Kolekt application running
- Supabase database configured
- Admin user account

### 1. Database Setup

First, ensure your Supabase database has the required tables. Run the updated schema in your Supabase SQL editor:

```sql
-- The schema includes the new announcements table and admin-specific policies
-- Run the complete supabase_schema.sql file
```

### 2. Create Admin User

Run the admin user creation script:

```bash
python create_admin.py
```

This will:
- Prompt for admin email, password, and name
- Create a user account with admin privileges
- Set the user as verified

### 3. Access the Admin Panel

Once your admin user is created, access the admin panel at:

```
http://127.0.0.1:8000/admin
```

## 🎯 Admin Panel Features

### Dashboard
- **User Statistics**: Total users, active users, kolekts created
- **API Usage**: Total API calls, storage usage, revenue metrics
- **Real-time Updates**: Refresh stats and export data

### User Management
- **User List**: View all users with pagination and search
- **User Details**: See user profiles, kolekts, and API usage
- **User Actions**: Edit user information, change plans, activate/deactivate accounts
- **Filtering**: Filter by plan (Free/Pro/Business) and status (Active/Inactive)

### Announcement System
- **Create Announcements**: Publish site-wide announcements
- **Priority Levels**: Low, Normal, High, Critical
- **Scheduling**: Set expiration dates for announcements
- **Management**: Edit, delete, and manage announcement status

### System Management
- **Health Monitoring**: Check database, Redis, and API health
- **Maintenance Mode**: Enable/disable maintenance mode with custom messages
- **System Status**: Real-time system monitoring

## 🔐 Security Features

### Access Control
- **Admin-only Access**: Only users with admin role can access the panel
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Automatic logout on token expiration

### Audit Logging
- **Action Tracking**: All admin actions are logged
- **User Activity**: Track user management and system changes
- **Security Events**: Monitor authentication and authorization events

## 📱 User Interface

### Cyberpunk Theme
- **Consistent Design**: Matches the main Kolekt theme
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Elements**: Hover effects, animations, and visual feedback

### Navigation
- **Tab-based Interface**: Easy navigation between sections
- **Breadcrumbs**: Clear navigation hierarchy
- **Quick Actions**: Common actions accessible from any section

## 🚀 Usage Guide

### Managing Users

1. **View Users**
   - Navigate to the "Users" section
   - Use search to find specific users
   - Filter by plan or status

2. **Edit User**
   - Click "Edit" on any user row
   - Modify name, email, plan, or status
   - Save changes

3. **Delete User**
   - Click "Delete" on any user row
   - Confirm the action (soft delete - sets user as inactive)

### Publishing Announcements

1. **Create Announcement**
   - Navigate to "Announcements" section
   - Click "Create Announcement"
   - Fill in title, content, priority, and expiration date
   - Set active status

2. **Manage Announcements**
   - View all announcements in a grid layout
   - Edit existing announcements
   - Delete announcements when no longer needed

### System Monitoring

1. **Check Health**
   - Navigate to "System" section
   - View real-time health status
   - Click "Check Health" to refresh

2. **Maintenance Mode**
   - Toggle maintenance mode switch
   - Add custom maintenance message
   - Monitor system status

## 🔧 Troubleshooting

### Common Issues

1. **Access Denied**
   - Ensure user has admin role in database
   - Check JWT token validity
   - Verify authentication status

2. **Database Errors**
   - Check Supabase connection
   - Verify schema is up to date
   - Check RLS policies

3. **Missing Data**
   - Refresh the page
   - Check browser console for errors
   - Verify API endpoints are working

### Debug Mode

Enable debug logging by checking browser console for detailed error messages.

## 📊 API Endpoints

The admin panel uses these API endpoints:

### Dashboard
- `GET /api/v1/admin/dashboard` - Get dashboard statistics

### User Management
- `GET /api/v1/admin/users` - List users with pagination
- `GET /api/v1/admin/users/{id}` - Get user details
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user

### Announcements
- `GET /api/v1/admin/announcements` - List announcements
- `POST /api/v1/admin/announcements` - Create announcement
- `PUT /api/v1/admin/announcements/{id}` - Update announcement
- `DELETE /api/v1/admin/announcements/{id}` - Delete announcement

### System
- `GET /api/v1/admin/system/health` - Check system health
- `POST /api/v1/admin/system/maintenance` - Toggle maintenance mode

## 🔒 Security Best Practices

1. **Strong Passwords**: Use complex passwords for admin accounts
2. **Regular Updates**: Keep admin credentials secure and updated
3. **Access Logging**: Monitor admin panel access regularly
4. **Session Management**: Logout when not using the panel
5. **Backup Data**: Regularly backup user and system data

## 📞 Support

If you encounter issues with the admin panel:

1. Check the browser console for error messages
2. Verify your Supabase configuration
3. Ensure all required tables exist in your database
4. Check that your admin user has the correct role

For additional support, refer to the main Kolekt documentation or contact the development team.

---

**Note**: The admin panel is designed for site administrators only. Regular users should not have access to this interface. Always ensure proper access controls are in place.
