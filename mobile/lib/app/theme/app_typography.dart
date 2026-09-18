import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// CertiNexus AI — Standardized Typography Hierarchy
class AppTypography {
  AppTypography._();

  static TextStyle get display => GoogleFonts.plusJakartaSans(
    fontSize: 34.0,
    fontWeight: FontWeight.w800,
    color: AppColors.textPrimary,
    letterSpacing: -0.8,
    height: 1.2,
  );

  static TextStyle get h1 => GoogleFonts.plusJakartaSans(
    fontSize: 26.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
    height: 1.25,
  );

  static TextStyle get h2 => GoogleFonts.plusJakartaSans(
    fontSize: 20.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.3,
    height: 1.3,
  );

  static TextStyle get h3 => GoogleFonts.plusJakartaSans(
    fontSize: 16.0,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    letterSpacing: -0.2,
    height: 1.35,
  );

  static TextStyle get bodyLarge => GoogleFonts.inter(
    fontSize: 16.0,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.5,
  );

  static TextStyle get bodyMedium => GoogleFonts.inter(
    fontSize: 14.0,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.45,
  );

  static TextStyle get bodySmall => GoogleFonts.inter(
    fontSize: 12.0,
    fontWeight: FontWeight.w400,
    color: AppColors.textMuted,
    height: 1.4,
  );

  static TextStyle get caption => GoogleFonts.inter(
    fontSize: 11.0,
    fontWeight: FontWeight.w500,
    color: AppColors.textMuted,
    letterSpacing: 0.2,
  );

  static TextStyle get button => GoogleFonts.plusJakartaSans(
    fontSize: 15.0,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.1,
  );

  static TextStyle get metric => GoogleFonts.plusJakartaSans(
    fontSize: 30.0,
    fontWeight: FontWeight.w800,
    color: AppColors.textPrimary,
    letterSpacing: -0.6,
  );

  static TextStyle get tag => GoogleFonts.inter(
    fontSize: 11.0,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.3,
  );
}
