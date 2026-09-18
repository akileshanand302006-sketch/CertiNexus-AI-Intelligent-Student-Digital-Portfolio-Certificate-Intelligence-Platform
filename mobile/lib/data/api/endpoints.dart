/// CertiNexus AI — Centralized REST API Endpoints
class Endpoints {
  Endpoints._();

  // Authentication
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String refresh = '/auth/refresh';

  // Users
  static const String userMe = '/users/me';

  // Certificates
  static const String certificates = '/certificates';
  static const String certificateUpload = '/certificates/upload';
  static String certificateDetails(String id) => '/certificates/$id';
  static String certificateStatus(String id) => '/certificates/$id/processing-status';

  // Intelligence & Skills
  static const String skills = '/skills';
  static const String analytics = '/analytics';
  static const String search = '/search';

  // Portfolio & Resume
  static const String portfolio = '/portfolio';
  static String publicPortfolio(String username) => '/portfolio/public/$username';
  static const String resumeData = '/resume/data';
  static const String resumeGenerate = '/resume/generate';

  // Admin & ML Research
  static const String adminDatasetStats = '/admin/dataset-statistics';
  static const String adminModelPerformance = '/admin/model-performance';
  static const String adminExperiments = '/admin/experiments';

  // Health
  static const String health = '/health';
}
