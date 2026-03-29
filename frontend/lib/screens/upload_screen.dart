import 'package:flutter/material.dart';

import '../components/animated_waveform.dart';
import '../components/glass_card.dart';
import '../components/neon_button.dart';
import '../theme/app_theme.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key, required this.onAnalyze});

  final VoidCallback onAnalyze;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  bool _vocalAttached = false;
  bool _songAttached = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.s20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Upload', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppTheme.s8),
          Text(
            'Drag & drop or tap to attach files.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: AppTheme.s20),
          Expanded(
            child: GlassCard(
              child: Column(
                children: [
                  Expanded(
                    child: Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(AppTheme.r16),
                        border: Border.all(color: AppTheme.neonBlue.withOpacity(0.55)),
                        color: Colors.white.withOpacity(0.02),
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.cloud_upload_rounded, size: 42),
                            SizedBox(height: AppTheme.s12),
                            Text('Drag & Drop Vocal / Song'),
                            SizedBox(height: 4),
                            Text(
                              'Mobile-friendly upload zone',
                              style: TextStyle(color: AppTheme.textLow),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: AppTheme.s16),
                  Row(
                    children: [
                      Expanded(
                        child: NeonButton(
                          text: _vocalAttached ? 'Vocal Uploaded' : 'Upload Vocal',
                          icon: Icons.mic_rounded,
                          onPressed: () => setState(() => _vocalAttached = true),
                        ),
                      ),
                      const SizedBox(width: AppTheme.s12),
                      Expanded(
                        child: NeonButton(
                          text: _songAttached ? 'Song Uploaded' : 'Upload Song',
                          icon: Icons.library_music_rounded,
                          secondary: true,
                          onPressed: () => setState(() => _songAttached = true),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppTheme.s16),
                  const AnimatedWaveform(height: 56, bars: 38),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppTheme.s20),
          NeonButton(
            text: 'Analyze My Voice',
            icon: Icons.auto_awesome_rounded,
            onPressed: _vocalAttached ? widget.onAnalyze : null,
          ),
        ],
      ),
    );
  }
}
