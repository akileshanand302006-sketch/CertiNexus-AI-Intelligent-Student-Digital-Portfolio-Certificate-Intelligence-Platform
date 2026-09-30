import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

/// Provider for the SecureStorageService singleton
final secureStorageServiceProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService(const FlutterSecureStorage());
});

/// CertiNexus AI — Hardware-backed Secure Key-Value Storage Service
class SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService(this._storage);

  Future<String?> getAccessToken() async {
    return await _storage.read(key: AppConstants.tokenKey);
  }

  Future<void> setAccessToken(String token) async {
    await _storage.write(key: AppConstants.tokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: AppConstants.refreshTokenKey);
  }

  Future<void> setRefreshToken(String token) async {
    await _storage.write(key: AppConstants.refreshTokenKey, value: token);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: AppConstants.tokenKey);
    await _storage.delete(key: AppConstants.refreshTokenKey);
  }

  Future<bool> isOnboardingCompleted() async {
    final value = await _storage.read(key: AppConstants.onboardingKey);
    return value == 'true';
  }

  Future<void> setOnboardingCompleted(bool completed) async {
    await _storage.write(
      key: AppConstants.onboardingKey,
      value: completed ? 'true' : 'false',
    );
  }

  Future<String?> getUserProfile() async {
    return await _storage.read(key: AppConstants.userProfileKey);
  }

  Future<void> setUserProfile(String json) async {
    await _storage.write(key: AppConstants.userProfileKey, value: json);
  }

  Future<bool> isDemoMode() async {
    final value = await _storage.read(key: AppConstants.demoModeKey);
    return value == 'true';
  }

  Future<void> setDemoMode(bool active) async {
    await _storage.write(
      key: AppConstants.demoModeKey,
      value: active ? 'true' : 'false',
    );
  }
}
