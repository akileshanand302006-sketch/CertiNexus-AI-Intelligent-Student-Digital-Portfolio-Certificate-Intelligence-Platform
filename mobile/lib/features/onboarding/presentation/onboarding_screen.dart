import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/theme/app_typography.dart';
import '../../../core/services/secure_storage_service.dart';
import '../../../shared/widgets/aurora_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/primary_button.dart';

class OnboardingItem {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color accentColor;

  const OnboardingItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentColor,
  });
}

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentIndex = 0;

  final List<OnboardingItem> _pages = const [
    OnboardingItem(
      title: 'Your achievements, intelligently organized.',
      subtitle:
          'Consolidate academic credentials, hackathon wins, and professional certificates in one secure intelligence hub.',
      icon: Icons.auto_awesome_outlined,
      accentColor: AppColors.primaryLight,
    ),
    OnboardingItem(
      title: 'Upload certificates. Let AI understand them.',
      subtitle:
          'High-accuracy OCR and machine-learning models automatically classify documents across 11 achievement domains.',
      icon: Icons.document_scanner_outlined,
      accentColor: AppColors.accent,
    ),
    OnboardingItem(
      title: 'Discover your skills and growth.',
      subtitle:
          'Uncover technical proficiencies and domain strengths automatically mined from your verified credentials.',
      icon: Icons.insights_outlined,
      accentColor: AppColors.secondaryLight,
    ),
    OnboardingItem(
      title: 'Build a verified digital portfolio.',
      subtitle:
          'Generate ATS-friendly resumes and shareable web portfolios with cryptographic QR code verification.',
      icon: Icons.badge_outlined,
      accentColor: AppColors.success,
    ),
  ];

  Future<void> _completeOnboarding() async {
    final storage = ref.read(secureStorageServiceProvider);
    await storage.setOnboardingCompleted(true);
    if (!mounted) return;
    context.go('/login');
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLastPage = _currentIndex == _pages.length - 1;

    return Scaffold(
      body: AuroraBackground(
        child: Padding(
          padding: AppSpacing.screenPadding,
          child: Column(
            children: [
              // Top Bar with Skip
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Logo mark
                  Row(
                    children: [
                      Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          gradient: AppColors.primaryGradient,
                          borderRadius: AppSpacing.roundedSm,
                        ),
                        child: const Center(
                          child: Text(
                            'C',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Text(
                        'CertiNexus AI',
                        style: AppTypography.h3.copyWith(
                          fontSize: 15,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                  if (!isLastPage)
                    TextButton(
                      onPressed: _completeOnboarding,
                      child: Text(
                        'Skip',
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.textMuted,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    )
                  else
                    const SizedBox(width: 48),
                ],
              ),
              const Spacer(),

              // Page View
              SizedBox(
                height: 380,
                child: PageView.builder(
                  controller: _pageController,
                  onPageChanged: (index) {
                    setState(() => _currentIndex = index);
                  },
                  itemCount: _pages.length,
                  itemBuilder: (context, index) {
                    final item = _pages[index];
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4.0),
                      child: GlassCard(
                        glow: true,
                        padding: const EdgeInsets.all(28.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              width: 84,
                              height: 84,
                              decoration: BoxDecoration(
                                color: item.accentColor.withValues(alpha: 0.15),
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: item.accentColor.withValues(alpha: 0.4),
                                  width: 1.5,
                                ),
                              ),
                              child: Icon(
                                item.icon,
                                size: 40,
                                color: item.accentColor,
                              ),
                            ),
                            const SizedBox(height: AppSpacing.xxl),
                            Text(
                              item.title,
                              style: AppTypography.h2.copyWith(fontSize: 21),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: AppSpacing.md),
                            Text(
                              item.subtitle,
                              style: AppTypography.bodyMedium.copyWith(
                                color: AppColors.textSecondary,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),

              const Spacer(),

              // Indicators & Actions
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  _pages.length,
                  (index) => AnimatedContainer(
                    duration: const Duration(milliseconds: 250),
                    margin: const EdgeInsets.symmetric(horizontal: 4.0),
                    width: _currentIndex == index ? 24.0 : 8.0,
                    height: 8.0,
                    decoration: BoxDecoration(
                      color: _currentIndex == index
                          ? AppColors.primary
                          : AppColors.textMuted.withValues(alpha: 0.3),
                      borderRadius: AppSpacing.roundedPill,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.xxl),

              // Button
              PrimaryButton(
                text: isLastPage ? 'Get Started' : 'Continue',
                onPressed: () {
                  if (isLastPage) {
                    _completeOnboarding();
                  } else {
                    _pageController.nextPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeInOut,
                    );
                  }
                },
              ),
              const SizedBox(height: AppSpacing.md),
            ],
          ),
        ),
      ),
    );
  }
}
