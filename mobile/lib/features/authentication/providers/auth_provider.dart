import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/secure_storage_service.dart';
import '../../../data/api/dio_client.dart';
import '../../../data/api/endpoints.dart';

enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
  error,
}

class AuthState {
  final AuthStatus status;
  final String? token;
  final String? errorMessage;
  final bool isDemo;
  final Map<String, dynamic>? user;

  const AuthState({
    required this.status,
    this.token,
    this.errorMessage,
    this.isDemo = false,
    this.user,
  });

  factory AuthState.initial() => const AuthState(status: AuthStatus.initial);

  AuthState copyWith({
    AuthStatus? status,
    String? token,
    String? errorMessage,
    bool? isDemo,
    Map<String, dynamic>? user,
  }) {
    return AuthState(
      status: status ?? this.status,
      token: token ?? this.token,
      errorMessage: errorMessage ?? this.errorMessage,
      isDemo: isDemo ?? this.isDemo,
      user: user ?? this.user,
    );
  }
}

final authProvider = NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    return AuthState.initial();
  }

  SecureStorageService get _storage => ref.read(secureStorageServiceProvider);
  dynamic get _dio => ref.read(dioClientProvider);

  Future<void> checkAuthStatus() async {
    final isDemo = await _storage.isDemoMode();
    if (isDemo) {
      state = state.copyWith(
        status: AuthStatus.authenticated,
        isDemo: true,
        user: {
          'full_name': 'Alex Kumar (Demo Student)',
          'username': 'alexkumar',
          'email': 'alex.kumar@student.edu',
          'institution': 'Five-Year Integrated M.Sc. (Software Systems)',
          'department': 'Department of Computing & AI',
        },
      );
      return;
    }

    final token = await _storage.getAccessToken();
    if (token != null && token.isNotEmpty) {
      state = state.copyWith(
        status: AuthStatus.authenticated,
        token: token,
      );
    } else {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    try {
      final response = await _dio.post(
        Endpoints.login,
        data: {'email': email, 'password': password},
      );

      final data = response.data;
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;

      await _storage.setAccessToken(accessToken);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setDemoMode(false);

      state = state.copyWith(
        status: AuthStatus.authenticated,
        token: accessToken,
        isDemo: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    try {
      final response = await _dio.post(
        Endpoints.register,
        data: {
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
        },
      );

      final data = response.data;
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;

      await _storage.setAccessToken(accessToken);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setDemoMode(false);

      state = state.copyWith(
        status: AuthStatus.authenticated,
        token: accessToken,
        isDemo: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  void loginAsDemo() async {
    await _storage.setDemoMode(true);
    state = state.copyWith(
      status: AuthStatus.authenticated,
      isDemo: true,
      user: {
        'full_name': 'Alex Kumar (Demo Student)',
        'username': 'alexkumar',
        'email': 'alex.kumar@student.edu',
        'institution': 'Five-Year Integrated M.Sc. (Software Systems)',
        'department': 'Department of Computing & AI',
      },
    );
  }

  Future<void> logout() async {
    await _storage.clearTokens();
    await _storage.setDemoMode(false);
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}
