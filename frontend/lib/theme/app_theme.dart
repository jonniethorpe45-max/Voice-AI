import 'package:flutter/material.dart';

class AppTheme {
  static const Color bg = Color(0xFF0A0A0A);
  static const Color glass = Color(0x1FFFFFFF);
  static const Color glassStrong = Color(0x2BFFFFFF);
  static const Color border = Color(0x2FFFFFFF);
  static const Color neonBlue = Color(0xFF00D4FF);
  static const Color neonPurple = Color(0xFF7B61FF);
  static const Color textHigh = Colors.white;
  static const Color textMedium = Color(0xB3FFFFFF);
  static const Color textLow = Color(0x80FFFFFF);

  static const double s8 = 8;
  static const double s12 = 12;
  static const double s16 = 16;
  static const double s20 = 20;
  static const double s24 = 24;
  static const double r16 = 16;
  static const double r20 = 20;

  static ThemeData get darkTheme {
    final scheme = ColorScheme.fromSeed(
      seedColor: neonPurple,
      brightness: Brightness.dark,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: bg,
      fontFamily: 'Inter',
      textTheme: const TextTheme(
        headlineLarge: TextStyle(fontSize: 44, fontWeight: FontWeight.w800, color: textHigh),
        headlineMedium: TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: textHigh),
        headlineSmall: TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: textHigh),
        bodyLarge: TextStyle(fontSize: 16, color: textMedium),
        bodyMedium: TextStyle(fontSize: 14, color: textLow),
      ),
      sliderTheme: SliderThemeData(
        activeTrackColor: neonBlue,
        inactiveTrackColor: Colors.white24,
        thumbColor: neonPurple,
        overlayColor: neonPurple.withOpacity(0.18),
        trackHeight: 4,
      ),
    );
  }
}
