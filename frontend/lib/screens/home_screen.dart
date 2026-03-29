import 'package:flutter/material.dart';

import '../components/animated_waveform.dart';
import '../components/neon_button.dart';
import '../theme/app_theme.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.onUpload,
    required this.onDemo,
  });

  final VoidCallback onUpload;
  final VoidCallback onDemo;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        const Positioned.fill(
          child: AnimatedWaveform(
            bars: 64,
            height: 120,
            backgroundMode: true,
          ),
        ),
        Positioned.fill(
          child: DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  AppTheme.bg.withOpacity(0.36),
                  AppTheme.bg.withOpacity(0.9),
                ],
              ),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(AppTheme.s24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              Text(
                'Make Your Voice\nFit Any Song',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: AppTheme.s12),
              Text(
                'AI studio transformation with invisible intelligence.',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: AppTheme.s24),
              NeonButton(
                text: 'Upload Your Vocal',
                icon: Icons.mic_rounded,
                onPressed: onUpload,
              ),
              const SizedBox(height: AppTheme.s12),
              NeonButton(
                text: 'Use Demo Track',
                icon: Icons.headphones_rounded,
                secondary: true,
                onPressed: onDemo,
              ),
              const Spacer(),
            ],
          ),
        ),
      ],
    );
  }
}
