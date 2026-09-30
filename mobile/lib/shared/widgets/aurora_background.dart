import 'dart:ui';
import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';

/// CertiNexus AI — Liquid Glass Ambient Aurora Background
class AuroraBackground extends StatelessWidget {
  final Widget child;

  const AuroraBackground({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Solid deep base
        Container(
          color: AppColors.background,
        ),

        // Glowing Top-Left Aurora Blob (Indigo)
        Positioned(
          top: -80,
          left: -80,
          width: 280,
          height: 280,
          child: Container(
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.auroraIndigo,
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Glowing Bottom-Right Aurora Blob (Violet)
        Positioned(
          bottom: -100,
          right: -80,
          width: 320,
          height: 320,
          child: Container(
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.auroraViolet,
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Mid-Center Soft Cyan Glow
        Positioned(
          top: MediaQuery.of(context).size.height * 0.4,
          right: -50,
          width: 220,
          height: 220,
          child: Container(
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.auroraCyan,
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Soft blur overlay across ambient lights
        BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 50.0, sigmaY: 50.0),
          child: Container(color: Colors.transparent),
        ),

        // Foreground application content
        SafeArea(
          child: child,
        ),
      ],
    );
  }
}
