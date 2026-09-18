import 'dart:ui';
import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../app/theme/app_typography.dart';

/// CertiNexus AI — Frosted Glass Secondary Button
class GlassButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Widget? icon;
  final double? width;
  final double height;
  final Color? borderColor;

  const GlassButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.icon,
    this.width,
    this.height = 50.0,
    this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width ?? double.infinity,
      height: height,
      decoration: BoxDecoration(
        color: AppColors.glassMedium,
        borderRadius: AppSpacing.roundedMd,
        border: Border.all(
          color: borderColor ?? AppColors.glassBorder,
          width: 1.0,
        ),
      ),
      child: ClipRRect(
        borderRadius: AppSpacing.roundedMd,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 12.0, sigmaY: 12.0),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: AppSpacing.roundedMd,
              onTap: onPressed,
              splashColor: AppColors.primary.withValues(alpha: 0.15),
              child: Center(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (icon != null) ...[
                      icon!,
                      const SizedBox(width: AppSpacing.sm),
                    ],
                    Text(
                      text,
                      style: AppTypography.button.copyWith(
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
