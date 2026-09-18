import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/theme/app_typography.dart';
import '../../../shared/widgets/aurora_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/glass_text_field.dart';
import '../../../shared/widgets/primary_button.dart';
import '../providers/auth_provider.dart';

/// CertiNexus AI — Student Registration Screen
class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _institutionController = TextEditingController();
  String? _localError;

  @override
  void dispose() {
    _fullNameController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _institutionController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _localError = null);
    final email = _emailController.text.trim();
    final username = _usernameController.text.trim();
    final password = _passwordController.text;
    final fullName = _fullNameController.text.trim();

    final success = await ref.read(authProvider.notifier).register(
      email: email,
      username: username,
      password: password,
      fullName: fullName.isNotEmpty ? fullName : null,
    );

    if (success && mounted) {
      context.go('/dashboard');
    } else if (mounted) {
      final error = ref.read(authProvider).errorMessage;
      setState(() {
        _localError = error ?? 'Registration failed. Please check your details.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState.status == AuthStatus.loading;

    return Scaffold(
      body: AuroraBackground(
        child: SingleChildScrollView(
          padding: AppSpacing.screenPadding,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IconButton(
                  onPressed: () => context.pop(),
                  icon: const Icon(Icons.arrow_back_ios_new,
                      color: AppColors.textPrimary, size: 20),
                ),
                const SizedBox(height: AppSpacing.md),

                Text('Create Account', style: AppTypography.h1),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Join CertiNexus AI and build your intelligent verified portfolio',
                  style: AppTypography.bodySmall,
                ),
                const SizedBox(height: AppSpacing.xl),

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

                GlassCard(
                  padding: const EdgeInsets.all(22.0),
                  child: Column(
                    children: [
                      GlassTextField(
                        controller: _fullNameController,
                        labelText: 'Full Name',
                        hintText: 'Alex Kumar',
                        prefixIcon: const Icon(Icons.person_outline,
                            color: AppColors.textMuted, size: 20),
                      ),
                      const SizedBox(height: AppSpacing.md),

                      GlassTextField(
                        controller: _usernameController,
                        labelText: 'Username',
                        hintText: 'alexkumar',
                        prefixIcon: const Icon(Icons.alternate_email,
                            color: AppColors.textMuted, size: 20),
                        validator: (val) {
                          if (val == null || val.trim().length < 3) {
                            return 'Username must be at least 3 characters';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSpacing.md),

                      GlassTextField(
                        controller: _emailController,
                        labelText: 'Email Address',
                        hintText: 'alex.kumar@student.edu',
                        keyboardType: TextInputType.emailAddress,
                        prefixIcon: const Icon(Icons.email_outlined,
                            color: AppColors.textMuted, size: 20),
                        validator: (val) {
                          if (val == null || !val.contains('@')) {
                            return 'Please enter a valid email address';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSpacing.md),

                      GlassTextField(
                        controller: _institutionController,
                        labelText: 'College / University',
                        hintText: 'e.g. Department of Software Systems',
                        prefixIcon: const Icon(Icons.school_outlined,
                            color: AppColors.textMuted, size: 20),
                      ),
                      const SizedBox(height: AppSpacing.md),

                      GlassTextField(
                        controller: _passwordController,
                        labelText: 'Password',
                        hintText: 'Minimum 6 characters',
                        isPassword: true,
                        prefixIcon: const Icon(Icons.lock_outline,
                            color: AppColors.textMuted, size: 20),
                        validator: (val) {
                          if (val == null || val.length < 6) {
                            return 'Password must be at least 6 characters';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: AppSpacing.xl),

                      PrimaryButton(
                        text: 'Complete Registration',
                        isLoading: isLoading,
                        onPressed: _handleRegister,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.xl),

                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Already have an account? ',
                        style: AppTypography.bodySmall),
                    GestureDetector(
                      onTap: () => context.pop(),
                      child: Text(
                        'Sign In',
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.primaryLight,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.xxl),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
