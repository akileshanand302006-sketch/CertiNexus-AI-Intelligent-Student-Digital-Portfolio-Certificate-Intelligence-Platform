/// CertiNexus AI — Application Constants
class AppConstants {
  AppConstants._();

  // Storage Keys
  static const String tokenKey = 'certinexus_access_token';
  static const String refreshTokenKey = 'certinexus_refresh_token';
  static const String onboardingKey = 'certinexus_onboarding_completed';
  static const String userProfileKey = 'certinexus_user_profile';
  static const String demoModeKey = 'certinexus_demo_mode_active';

  // 11 Academic & Professional Certificate Categories
  static const List<String> certificateCategories = [
    'Academic Achievement',
    'Certification',
    'Conference',
    'Cultural Activity',
    'Hackathon',
    'Internship',
    'Seminar',
    'Sports',
    'Technical Competition',
    'Volunteer Activity',
    'Workshop',
  ];

  // AI Confidence Bands
  static const double highConfidenceThreshold = 0.85;
  static const double mediumConfidenceThreshold = 0.70;

  // Animation Durations
  static const Duration splashDuration = Duration(milliseconds: 2000);
  static const Duration quickAnimation = Duration(milliseconds: 200);
  static const Duration standardAnimation = Duration(milliseconds: 350);
  static const Duration smoothPageTransition = Duration(milliseconds: 400);
}
