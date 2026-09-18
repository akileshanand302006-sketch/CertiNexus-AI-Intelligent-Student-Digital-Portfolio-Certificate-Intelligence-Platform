import 'package:flutter/material.dart';

/// CertiNexus AI — Semantic Color Palette & Liquid Glass AI Theme
class AppColors {
  AppColors._();

  // Backgrounds & Base Surfaces
  static const Color background = Color(0xFF0B0E17);
  static const Color backgroundSecondary = Color(0xFF0F1422);
  static const Color surface = Color(0xFF13192B);
  static const Color surfaceElevated = Color(0xFF1A2238);
  static const Color surfaceCard = Color(0xFF161E31);

  // Liquid Glass Tokens
  static const Color glass = Color(0x14FFFFFF);           // ~8% white
  static const Color glassMedium = Color(0x20FFFFFF);     // ~12% white
  static const Color glassThick = Color(0x2EFFFFFF);      // ~18% white
  static const Color glassBorder = Color(0x26FFFFFF);     // ~15% white border
  static const Color glassBorderHighlight = Color(0x40FFFFFF); // ~25% white border
  static const Color glassShadow = Color(0x40000000);

  // Primary Brand & Electric Accents
  static const Color primary = Color(0xFF6366F1);         // Indigo electric
  static const Color primaryLight = Color(0xFF818CF8);
  static const Color primaryDark = Color(0xFF4F46E5);
  static const Color secondary = Color(0xFF8B5CF6);       // Violet
  static const Color secondaryLight = Color(0xFFA78BFA);
  static const Color accent = Color(0xFF06B6D4);          // Cyan neon
  static const Color accentLight = Color(0xFF22D3EE);

  // Aurora Ambient Glow Colors
  static const Color auroraIndigo = Color(0x554F46E5);
  static const Color auroraViolet = Color(0x447C3AED);
  static const Color auroraCyan = Color(0x4006B6D4);

  // Semantic Feedback States
  static const Color success = Color(0xFF10B981);         // Emerald
  static const Color successBg = Color(0x2010B981);
  static const Color warning = Color(0xFFF59E0B);         // Amber
  static const Color warningBg = Color(0x20F59E0B);
  static const Color error = Color(0xFFEF4444);           // Rose
  static const Color errorBg = Color(0x20EF4444);
  static const Color info = Color(0xFF3B82F6);            // Blue
  static const Color infoBg = Color(0x203B82F6);

  // High-Contrast Typography
  static const Color textPrimary = Color(0xFFF8FAFC);     // Slate 50
  static const Color textSecondary = Color(0xFFCBD5E1);   // Slate 300
  static const Color textMuted = Color(0xFF64748B);       // Slate 500
  static const Color textDisabled = Color(0xFF475569);    // Slate 600

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentGradient = LinearGradient(
    colors: [primary, accent],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient glassGradient = LinearGradient(
    colors: [Color(0x1FFFFFFF), Color(0x0AFFFFFF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
