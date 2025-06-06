class UserService:
    @staticmethod
    def validate_user_data(data):
        """Validate user data"""
        errors = []
        
        if not data.get('username'):
            errors.append('Username is required')
        elif len(data.get('username', '')) < 3:
            errors.append('Username must be at least 3 characters')
        elif not data.get('username', '').replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, hyphens and underscores')
            
        if not data.get('email'):
            errors.append('Email is required')
            
        return errors
    
    @staticmethod
    def search_users(users_db, query):
        """Search users by username or email"""
        query = query.lower()
        return [
            user for user in users_db
            if query in user.username.lower() or query in user.email.lower()
        ]
