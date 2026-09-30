import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/config/app_config.dart';
import '../../core/errors/app_exception.dart';
import '../../core/services/secure_storage_service.dart';

/// Provider for the configured Dio HTTP client
final dioClientProvider = Provider<Dio>((ref) {
  final storageService = ref.watch(secureStorageServiceProvider);
  return createDioClient(storageService);
});

Dio createDioClient(SecureStorageService storage) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: AppConfig.connectTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      sendTimeout: AppConfig.sendTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.getAccessToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (DioException error, handler) {
        final appException = _mapDioException(error);
        return handler.reject(
          DioException(
            requestOptions: error.requestOptions,
            response: error.response,
            type: error.type,
            error: appException,
            message: appException.message,
          ),
        );
      },
    ),
  );

  return dio;
}

AppException _mapDioException(DioException error) {
  switch (error.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.connectionError:
      return NetworkException(
        message: 'Connection timed out. Please check your internet connection.',
        originalError: error,
      );

    case DioExceptionType.badResponse:
      final statusCode = error.response?.statusCode;
      final data = error.response?.data;
      String message = 'An unexpected server error occurred.';

      if (data is Map<String, dynamic>) {
        message = data['detail'] ?? data['message'] ?? message;
      }

      if (statusCode == 401) {
        return UnauthorizedException(message: message, originalError: error);
      } else if (statusCode == 403) {
        return ForbiddenException(message: message, originalError: error);
      } else if (statusCode == 404) {
        return NotFoundException(message: message, originalError: error);
      } else if (statusCode == 422) {
        return ValidationException(
          message: message,
          originalError: error,
          errors: data is Map<String, dynamic> ? data : null,
        );
      } else {
        return ServerException(
          message: message,
          statusCode: statusCode,
          originalError: error,
        );
      }

    case DioExceptionType.cancel:
      return const AppException(message: 'Request was cancelled.');

    default:
      return AppException(
        message: error.message ?? 'An unknown error occurred.',
        originalError: error,
      );
  }
}
