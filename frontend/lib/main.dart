import 'package:flutter/material.dart';

import 'navigation/app_shell.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const VocalFitApp());
}

class VocalFitApp extends StatelessWidget {
  const VocalFitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VocalFit AI',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      theme: AppTheme.darkTheme,
      home: const AppShell(),
    );
  }
}
