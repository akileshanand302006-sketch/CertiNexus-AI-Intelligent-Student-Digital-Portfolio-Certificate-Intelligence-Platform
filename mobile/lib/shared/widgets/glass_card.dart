import 'dart:ui';
import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

/// CertiNexus AI — Frosted Liquid Glass Card
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final BorderRadius? borderRadius;
  final VoidCallback? onTap;
  final bool glow;
  final Color? backgroundColor;
  final Color? borderColor;
  final double? width;
  final double? height;

  const GlassCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.borderRadius,
    this.onTap,
    this.glow = false,
    this.backgroundColor,
    this.borderColor,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveRadius = borderRadius ?? AppSpacing.roundedLg;

    Widget content = Container(
      width: width,
      height: height,
      padding: padding ?? AppSpacing.cardPadding,
      decoration: BoxDecoration(
        color: backgroundColor ?? AppColors.glass,
        borderRadius: effectiveRadius,
        border: Border.all(
          color: borderColor ?? (glow ? AppColors.primaryLight : AppColors.glassBorder),
          width: glow ? 1.5 : 1.0,
        ),
        boxShadow: [
          BoxShadow(
            color: glow
                ? AppColors.primary.withValues(alpha: 0.22)
                : Colors.black.withValues(alpha: 0.25),
            blurRadius: glow ? 20.0 : 16.0,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: child,
    );

    if (onTap != null) {
      content = Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: effectiveRadius,
          onTap: onTap,
          splashColor: AppColors.primary.withValues(alpha: 0.15),
          highlightColor: Colors.white.withValues(alpha: 0.05),
          child: content,
        ),
      );
    }

    final cardWithBlur = ClipRRect(
      borderRadius: effectiveRadius,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16.0, sigmaY: 16.0),
        child: content,
      ),
    );

    if (margin != null) {
      return Padding(
        padding: margin!,
        child: cardWithBlur,
      );
    }

    return cardWithBlur;
  }
}
