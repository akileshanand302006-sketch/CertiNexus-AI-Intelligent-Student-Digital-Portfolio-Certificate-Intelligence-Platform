import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/theme/app_typography.dart';
import '../../../shared/widgets/aurora_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/glass_text_field.dart';
import '../../../shared/widgets/primary_button.dart';

/// CertiNexus AI — Password Recovery Screen
class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _isSent = false;
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  void _handleReset() async {
    final email = _emailController.text.trim();
    if (email.isEmpty || !email.contains('@')) return;

    setState(() => _isLoading = true);
    await Future.delayed(const Duration(milliseconds: 800));
    if (!mounted) return;

    setState(() {
      _isLoading = false;
      _isSent = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuroraBackground(
        child: Padding(
          padding: AppSpacing.screenPadding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              IconButton(
                onPressed: () => context.pop(),
                icon: const Icon(Icons.arrow_back_ios_new,
                    color: AppColors.textPrimary, size: 20),
              ),
              const SizedBox(height: AppSpacing.lg),

              Text('Reset Password', style: AppTypography.h1),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Enter your student email and we will send you instructions to reset your password.',
                style: AppTypography.bodySmall,
              ),
              const SizedBox(height: AppSpacing.xxl),

              if (_isSent)
                GlassCard(
                  glow: true,
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          color: AppColors.successBg,
                          shape: BoxShape.circle,
                          border: Border.all(color: AppColors.success),
                        ),
                        child: const Icon(Icons.mark_email_read_outlined,
                            color: AppColors.success, size: 28),
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Text('Check Your Email', style: AppTypography.h2),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        'We have sent a verification code to ${_emailController.text}',
                        style: AppTypography.bodySmall,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: AppSpacing.xl),
                      PrimaryButton(
                        text: 'Return to Sign In',
                        onPressed: () => context.go('/login'),
                      ),
                    ],
                  ),
                )
              else
                GlassCard(
                  padding: const EdgeInsets.all(22.0),
                  child: Column(
                    children: [
                      GlassTextField(
                        controller: _emailController,
                        labelText: 'Email Address',
                        hintText: 'alex.kumar@student.edu',
                        keyboardType: TextInputType.emailAddress,
                        prefixIcon: const Icon(Icons.email_outlined,
                            color: AppColors.textMuted, size: 20),
                      ),
                      const SizedBox(height: AppSpacing.xl),
                      PrimaryButton(
                        text: 'Send Reset Link',
                        isLoading: _isLoading,
                        onPressed: _handleReset,
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
