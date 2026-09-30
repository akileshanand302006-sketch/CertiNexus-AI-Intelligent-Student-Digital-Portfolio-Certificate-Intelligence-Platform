import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../app/theme/app_typography.dart';
import '../../../shared/widgets/aurora_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../authentication/providers/auth_provider.dart';

/// CertiNexus AI — Main Dashboard Foundation Screen
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final userName = authState.user?['full_name'] ?? 'Alex Kumar';
    final institution = authState.user?['institution'] ?? 'Five-Year Integrated M.Sc. (Software Systems)';
    final isDemo = authState.isDemo;

    return Scaffold(
      body: AuroraBackground(
        child: SingleChildScrollView(
          padding: AppSpacing.screenPadding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Row with Avatar & Logout
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          gradient: AppColors.primaryGradient,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withValues(alpha: 0.3),
                              blurRadius: 12,
                            ),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            userName[0].toUpperCase(),
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.md),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text('Welcome back,', style: AppTypography.bodySmall),
                              if (isDemo) ...[
                                const SizedBox(width: 6),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppColors.accent.withValues(alpha: 0.2),
                                    borderRadius: AppSpacing.roundedPill,
                                  ),
                                  child: Text(
                                    'DEMO',
                                    style: AppTypography.caption.copyWith(
                                      color: AppColors.accent,
                                      fontSize: 9,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                          Text(userName, style: AppTypography.h3),
                        ],
                      ),
                    ],
                  ),
                  IconButton(
                    onPressed: () async {
                      await ref.read(authProvider.notifier).logout();
                      if (context.mounted) {
                        context.go('/login');
                      }
                    },
                    icon: const Icon(Icons.logout_outlined,
                        color: AppColors.textMuted, size: 22),
                    tooltip: 'Sign Out',
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.xxl),

              // AI Insight Glass Banner
              GlassCard(
                glow: true,
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: AppColors.accent.withValues(alpha: 0.15),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.auto_awesome,
                          color: AppColors.accent, size: 22),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'AI Portfolio Insight',
                            style: AppTypography.tag.copyWith(
                              color: AppColors.accent,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Strong activity in Machine Learning & Cloud. Verified credentials cover 8 distinct domains.',
                            style: AppTypography.bodySmall.copyWith(
                              color: AppColors.textPrimary,
                              height: 1.3,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.xl),

              // Achievement Metrics 2x2 Bento Grid
              Text('Achievement Overview', style: AppTypography.h2),
              const SizedBox(height: AppSpacing.md),

              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 14,
                crossAxisSpacing: 14,
                childAspectRatio: 1.35,
                children: [
                  _MetricCard(
                    title: 'Certificates',
                    value: '24',
                    icon: Icons.military_tech_outlined,
                    accentColor: AppColors.primaryLight,
                  ),
                  _MetricCard(
                    title: 'Achievements',
                    value: '31',
                    icon: Icons.emoji_events_outlined,
                    accentColor: AppColors.secondaryLight,
                  ),
                  _MetricCard(
                    title: 'Skills Extracted',
                    value: '18',
                    icon: Icons.psychology_outlined,
                    accentColor: AppColors.accent,
                  ),
                  _MetricCard(
                    title: 'Portfolio Score',
                    value: '86%',
                    icon: Icons.verified_outlined,
                    accentColor: AppColors.success,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.xxl),

              // Quick Action / Academic Lab Info
              GlassCard(
                padding: const EdgeInsets.all(18.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.school_outlined,
                            color: AppColors.primaryLight, size: 20),
                        const SizedBox(width: AppSpacing.sm),
                        Text(
                          '20MSSL12 Machine Learning Lab',
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.primaryLight,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      institution,
                      style: AppTypography.bodyMedium.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.huge),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color accentColor;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.accentColor,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: AppTypography.caption),
              Icon(icon, color: accentColor, size: 18),
            ],
          ),
          Text(
            value,
            style: AppTypography.metric.copyWith(
              fontSize: 26,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
