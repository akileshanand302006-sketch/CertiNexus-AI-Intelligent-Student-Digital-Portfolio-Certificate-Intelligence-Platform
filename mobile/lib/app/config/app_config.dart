import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'environment.dart';

/// CertiNexus AI — Global Application Configuration
class AppConfig {
  AppConfig._();

  static Environment currentEnvironment = kReleaseMode
      ? Environment.production
      : Environment.development;

  static const String appName = 'CertiNexus AI';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'Intelligent Student Digital Portfolio & Certificate Intelligence';

  /// Centralized API base URL.
  /// Android emulator uses 10.0.2.2 to access host machine; web/desktop/other uses localhost.
  static String get defaultBaseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000/api';
    }
    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000/api';
      }
    } catch (_) {
      // Fallback if Platform check fails
    }
    return 'http://localhost:8000/api';
  }

  static String _customBaseUrl = '';

  static String get apiBaseUrl =>
      _customBaseUrl.isNotEmpty ? _customBaseUrl : defaultBaseUrl;

  static void setCustomBaseUrl(String url) {
    _customBaseUrl = url;
  }

  // Network Timeouts
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 60);

  // Upload constraints
  static const int maxFileSizeBytes = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedFileExtensions = ['pdf', 'png', 'jpg', 'jpeg', 'webp'];
}
