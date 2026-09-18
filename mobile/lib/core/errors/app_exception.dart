/// CertiNexus AI — Standard Application Exceptions
class AppException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalError;

  const AppException({
    required this.message,
    this.statusCode,
    this.originalError,
  });

  @override
  String toString() => 'AppException(statusCode: $statusCode, message: $message)';
}

class NetworkException extends AppException {
  const NetworkException({
    super.message = 'Unable to connect to the server. Please check your network connection.',
    super.statusCode,
    super.originalError,
  });
}

class UnauthorizedException extends AppException {
  const UnauthorizedException({
    super.message = 'Your session has expired. Please sign in again.',
    super.statusCode = 401,
    super.originalError,
  });
}

class ForbiddenException extends AppException {
  const ForbiddenException({
    super.message = 'You do not have permission to perform this action.',
    super.statusCode = 403,
    super.originalError,
  });
}

class NotFoundException extends AppException {
  const NotFoundException({
    super.message = 'The requested resource was not found.',
    super.statusCode = 404,
    super.originalError,
  });
}

class ValidationException extends AppException {
  final Map<String, dynamic>? errors;

  const ValidationException({
    super.message = 'Invalid data provided. Please verify your inputs.',
    super.statusCode = 422,
    this.errors,
    super.originalError,
  });
}

class ServerException extends AppException {
  const ServerException({
    super.message = 'A server error occurred. Please try again later.',
    super.statusCode = 500,
    super.originalError,
  });
}
