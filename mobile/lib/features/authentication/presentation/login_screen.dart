import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/theme/app_typography.dart';
import '../../../shared/widgets/aurora_background.dart';
import '../../../shared/widgets/glass_button.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/glass_text_field.dart';
import '../../../shared/widgets/primary_button.dart';
import '../providers/auth_provider.dart';

/// CertiNexus AI — Liquid Glass Login Screen
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String? _localError;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _localError = null);
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    final success = await ref.read(authProvider.notifier).login(email, password);

    if (success && mounted) {
      context.go('/dashboard');
    } else if (mounted) {
      final error = ref.read(authProvider).errorMessage;
      setState(() {
        _localError = error ?? 'Login failed. Please verify credentials.';
      });
    }
  }

  void _handleDemoLogin() {
    ref.read(authProvider.notifier).loginAsDemo();
    context.go('/dashboard');
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState.status == AuthStatus.loading;

    return Scaffold(
      body: AuroraBackground(
        child: Center(
          child: SingleChildScrollView(
            padding: AppSpacing.screenPadding,
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Brand Header
                  Container(
                    width: 68,
                    height: 68,
                    decoration: BoxDecoration(
                      gradient: AppColors.primaryGradient,
                      borderRadius: AppSpacing.roundedLg,
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withValues(alpha: 0.4),
                          blurRadius: 24,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Center(
                      child: Text(
                        'C',
                        style: TextStyle(
                          fontSize: 34,
                          fontWeight: FontWeight.w900,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  Text('Welcome to CertiNexus', style: AppTypography.h1),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    'Student Certificate Intelligence Platform',
                    style: AppTypography.bodySmall,
                  ),
                  const SizedBox(height: AppSpacing.xxl),

                  // Form Glass Card
                  GlassCard(
                    glow: true,
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (_localError != null) ...[
                          Container(
                            padding: const EdgeInsets.all(12.0),
                            decoration: BoxDecoration(
                              color: AppColors.errorBg,
                              borderRadius: AppSpacing.roundedSm,
                              border: Border.all(color: AppColors.error),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.error_outline,
                                    color: AppColors.error, size: 20),
                                const SizedBox(width: AppSpacing.sm),
                                Expanded(
                                  child: Text(
                                    _localError!,
                                    style: AppTypography.bodySmall.copyWith(
                                      color: AppColors.error,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: AppSpacing.lg),
                        ],

                        GlassTextField(
                          controller: _emailController,
                          labelText: 'Student Email',
                          hintText: 'alex.kumar@student.edu',
                          keyboardType: TextInputType.emailAddress,
                          prefixIcon: const Icon(Icons.email_outlined,
                              color: AppColors.textMuted, size: 20),
                          validator: (val) {
                            if (val == null || val.trim().isEmpty) {
                              return 'Please enter your email address';
                            }
                            if (!val.contains('@') || !val.contains('.')) {
                              return 'Please enter a valid email';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: AppSpacing.lg),

                        GlassTextField(
                          controller: _passwordController,
                          labelText: 'Password',
                          hintText: '••••••••',
                          isPassword: true,
                          prefixIcon: const Icon(Icons.lock_outline,
                              color: AppColors.textMuted, size: 20),
                          validator: (val) {
                            if (val == null || val.length < 6) {
                              return 'Password must be at least 6 characters';
                            }
                            return null;
                          },
                          onFieldSubmitted: (_) => _handleLogin(),
                        ),
                        const SizedBox(height: AppSpacing.sm),

                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () => context.push('/forgot-password'),
                            child: Text(
                              'Forgot Password?',
                              style: AppTypography.caption.copyWith(
                                color: AppColors.primaryLight,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: AppSpacing.sm),

                        PrimaryButton(
                          text: 'Sign In',
                          isLoading: isLoading,
                          onPressed: _handleLogin,
                        ),
                        const SizedBox(height: AppSpacing.lg),

                        // Evaluator Quick Demo Button
                        Row(
                          children: [
                            const Expanded(child: Divider()),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 12.0),
                              child: Text(
                                'ACADEMIC EVALUATION',
                                style: AppTypography.caption.copyWith(
                                  color: AppColors.textMuted,
                                  fontSize: 10,
                                  letterSpacing: 1.0,
                                ),
                              ),
                            ),
                            const Expanded(child: Divider()),
                          ],
                        ),
                        const SizedBox(height: AppSpacing.lg),

                        GlassButton(
                          text: 'Explore Demo Mode (Instant Access)',
                          icon: const Icon(Icons.auto_awesome,
                              color: AppColors.accent, size: 18),
                          onPressed: _handleDemoLogin,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl),

                  // Register Link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "Don't have an account? ",
                        style: AppTypography.bodySmall,
                      ),
                      GestureDetector(
                        onTap: () => context.push('/register'),
                        child: Text(
                          'Create Account',
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.primaryLight,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
