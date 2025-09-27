# Avatar Upload Implementation Guide

## Overview
This guide documents the complete avatar upload functionality implemented in the EspritVerse backend and frontend.

## Backend Implementation

### 1. Model Configuration
The `User` model in `accounts/models.py` includes:
```python
avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

@property
def avatar_url(self):
    return self.avatar.url if self.avatar else None
```

### 2. Serializer Updates
The `RegisterSerializer` in `accounts/serializers.py` supports avatar uploads:
```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ("username", "email", "password", "display_name", "role", "avatar")
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True}
        }
```

### 3. API Endpoints

#### Registration with Avatar
- **Endpoint**: `POST /api/auth/register/`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `username` (required): String, max 150 chars, pattern: `^[\w.@+-]+$`
  - `email` (required): Valid email format
  - `password` (required): Min 6 characters
  - `display_name` (optional): String, max 120 chars
  - `role` (optional): One of: `student`, `club_manager`, `committee_admin`, `admin`
  - `avatar` (optional): Image file (jpg, png, gif, etc.)

#### Profile Update with Avatar
- **Endpoint**: `PATCH /api/profiles/me/`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `display_name` (optional): String, max 120 chars
  - `bio` (optional): Text field
  - `avatar` (optional): Image file

### 4. Media File Serving
- **Media URL**: `/media/`
- **Media Root**: `BASE_DIR/media/`
- **Avatar Storage**: `media/avatars/`
- **Development**: Files served automatically via Django's static file serving
- **Production**: Configure web server (nginx/Apache) to serve media files

### 5. File Validation
- **Supported Formats**: All image formats supported by PIL/Pillow
- **Storage**: Files stored in `media/avatars/` directory
- **Naming**: Django automatically generates unique filenames to prevent conflicts

## Frontend Implementation

### 1. Registration Form
The registration form in `src/app/register/page.tsx` includes:
- File input for avatar selection
- Image preview functionality
- Remove avatar option
- Form validation

### 2. Profile Update Form
The profile update form in `src/app/profile/me/page.tsx` includes:
- Avatar upload with preview
- Update existing avatar
- Remove avatar functionality

### 3. API Integration
The frontend uses `FormData` to send multipart requests:
```typescript
const formData = new FormData();
formData.append('username', userData.username);
formData.append('email', userData.email);
formData.append('password', userData.password);
if (userData.display_name) formData.append('display_name', userData.display_name);
formData.append('role', userData.role || 'student');
if (avatar) {
  formData.append('avatar', avatar);
}
```

## Usage Examples

### 1. Register with Avatar (cURL)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -F "username=john_doe" \
  -F "email=john@example.com" \
  -F "password=securepass123" \
  -F "display_name=John Doe" \
  -F "role=student" \
  -F "avatar=@/path/to/avatar.jpg"
```

### 2. Update Profile with Avatar (cURL)
```bash
curl -X PATCH http://127.0.0.1:8000/api/profiles/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "display_name=John Smith" \
  -F "bio=I love coding!" \
  -F "avatar=@/path/to/new_avatar.jpg"
```

## Error Handling

### Common Issues
1. **File too large**: Configure `FILE_UPLOAD_MAX_MEMORY_SIZE` in settings
2. **Invalid file type**: Only image files are accepted
3. **Storage permissions**: Ensure `media/avatars/` directory is writable
4. **CORS issues**: Configure CORS settings for frontend requests

### Frontend Validation
- File type validation (images only)
- File size limits (configurable)
- Username pattern validation
- Password strength requirements

## Security Considerations

1. **File Validation**: Only image files are accepted
2. **File Size Limits**: Configure appropriate limits
3. **Storage Security**: Ensure proper file permissions
4. **CORS Configuration**: Restrict to allowed origins
5. **Authentication**: Profile updates require authentication

## Testing

### Backend Tests
```python
# Test avatar upload during registration
def test_register_with_avatar(self):
    with open('test_avatar.jpg', 'rb') as avatar:
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'avatar': avatar
        })
    self.assertEqual(response.status_code, 201)
```

### Frontend Tests
- Test file selection and preview
- Test form validation
- Test API integration
- Test error handling

## Deployment Notes

1. **Media Files**: Configure web server to serve media files
2. **Storage**: Consider using cloud storage (AWS S3, etc.) for production
3. **CDN**: Use CDN for better performance
4. **Backup**: Implement regular backups of user avatars

## Troubleshooting

### Common Issues
1. **404 on avatar URLs**: Check media file serving configuration
2. **Upload fails**: Check file permissions and size limits
3. **CORS errors**: Configure CORS settings properly
4. **Database errors**: Run migrations after model changes

### Debug Steps
1. Check Django logs for errors
2. Verify file permissions
3. Test API endpoints with cURL
4. Check browser network tab for request details
