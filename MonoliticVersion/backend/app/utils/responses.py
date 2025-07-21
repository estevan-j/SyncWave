from flask import jsonify

class ApiResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Create a successful API response"""
        response = {
            'success': True,
            'message': message,
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message="Error", status_code=400, error_code=None):
        """Create an error API response"""
        response = {
            'success': False,
            'message': message,
            'data': None
        }
        
        if error_code:
            response['error_code'] = error_code
            
        return jsonify(response), status_code
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Create a 404 not found response"""
        return ApiResponse.error(message, 404, "NOT_FOUND")
    
    @staticmethod
    def validation_error(message="Validation failed"):
        """Create a 400 validation error response"""
        return ApiResponse.error(message, 400, "VALIDATION_ERROR")
    
    @staticmethod
    def server_error(message="Internal server error"):
        """Create a 500 server error response"""
        return ApiResponse.error(message, 500, "SERVER_ERROR")
    
    @staticmethod
    def unauthorized(message="Unauthorized"):
        """Create a 401 unauthorized response"""
        return ApiResponse.error(message, 401, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message="Forbidden"):
        """Create a 403 forbidden response"""
        return ApiResponse.error(message, 403, "FORBIDDEN")
    
    @staticmethod
    def paginated_success(data, page=1, per_page=10, total=0, message="Success"):
        """Create a paginated success response"""
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        
        response_data = {
            'items': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        return ApiResponse.success(response_data, message)
