import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_spacing.dart';

/// CertiNexus AI — Liquid Glass AI Design Tokens and Decorations
class GlassTheme {
  GlassTheme._();

  static const double defaultBlur = 16.0;
  static const double cardBlur = 20.0;
  static const double modalBlur = 24.0;

  /// Standard Liquid Glass Card Decoration
  static BoxDecoration cardDecoration({
    BorderRadius? borderRadius,
    Color? backgroundColor,
    Color? borderColor,
    bool glow = false,
  }) {
    return BoxDecoration(
      color: backgroundColor ?? AppColors.glass,
      borderRadius: borderRadius ?? AppSpacing.roundedLg,
      border: Border.all(
        color: borderColor ?? AppColors.glassBorder,
        width: 1.0,
      ),
      boxShadow: [
        BoxShadow(
          color: glow ? AppColors.primary.withValues(alpha: 0.18) : Colors.black.withValues(alpha: 0.25),
          blurRadius: glow ? 24.0 : 16.0,
          spreadRadius: glow ? 2.0 : 0.0,
          offset: const Offset(0, 8),
        ),
      ],
    );
  }

  /// Subtle frosted input field decoration
  static InputDecoration inputDecoration({
    required String hintText,
    Widget? prefixIcon,
    Widget? suffixIcon,
    String? labelText,
    String? errorText,
  }) {
    return InputDecoration(
      hintText: hintText,
      labelText: labelText,
      errorText: errorText,
      prefixIcon: prefixIcon,
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: AppColors.glassMedium,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
      hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 14.0),
      labelStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 14.0),
      border: OutlineInputBorder(
        borderRadius: AppSpacing.roundedMd,
        borderSide: const BorderSide(color: AppColors.glassBorder, width: 1.0),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: AppSpacing.roundedMd,
        borderSide: const BorderSide(color: AppColors.glassBorder, width: 1.0),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: AppSpacing.roundedMd,
        borderSide: const BorderSide(color: AppColors.primaryLight, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: AppSpacing.roundedMd,
        borderSide: const BorderSide(color: AppColors.error, width: 1.0),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: AppSpacing.roundedMd,
        borderSide: const BorderSide(color: AppColors.error, width: 1.5),
      ),
    );
  }
}
