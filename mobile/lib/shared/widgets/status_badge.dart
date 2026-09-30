import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../app/theme/app_typography.dart';
import '../../core/constants/app_constants.dart';

/// CertiNexus AI — AI Confidence Level Indicator Badge
class ConfidenceBadge extends StatelessWidget {
  final double confidence; // 0.0 to 1.0
  final bool showPercentage;

  const ConfidenceBadge({
    super.key,
    required this.confidence,
    this.showPercentage = true,
  });

  @override
  Widget build(BuildContext context) {
    final Color badgeColor;
    final Color badgeBg;
    final String label;

    if (confidence >= AppConstants.highConfidenceThreshold) {
      badgeColor = AppColors.success;
      badgeBg = AppColors.successBg;
      label = 'High';
    } else if (confidence >= AppConstants.mediumConfidenceThreshold) {
      badgeColor = AppColors.warning;
      badgeBg = AppColors.warningBg;
      label = 'Medium';
    } else {
      badgeColor = AppColors.error;
      badgeBg = AppColors.errorBg;
      label = 'Low';
    }

    final percentageStr = '${(confidence * 100).toInt()}%';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: badgeBg,
        borderRadius: AppSpacing.roundedPill,
        border: Border.all(color: badgeColor.withValues(alpha: 0.35), width: 1.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6.0,
            height: 6.0,
            decoration: BoxDecoration(
              color: badgeColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: AppSpacing.xs + 2),
          Text(
            showPercentage ? '$label ($percentageStr)' : label,
            style: AppTypography.tag.copyWith(
              color: badgeColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

/// Category Pill Badge
class CategoryBadge extends StatelessWidget {
  final String category;

  const CategoryBadge({
    super.key,
    required this.category,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.15),
        borderRadius: AppSpacing.roundedPill,
        border: Border.all(
          color: AppColors.primaryLight.withValues(alpha: 0.3),
          width: 1.0,
        ),
      ),
      child: Text(
        category,
        style: AppTypography.tag.copyWith(
          color: AppColors.primaryLight,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
