import 'package:flutter/material.dart';

import '../components/animated_waveform.dart';
import '../components/glass_card.dart';
import '../components/neon_button.dart';
import '../core/app_models.dart';
import '../theme/app_theme.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({
    super.key,
    required this.onPickVocal,
    required this.onPickSong,
    required this.vocalName,
    required this.songName,
    required this.onAnalyze,
    required this.busy,
  });

  final Future<void> Function() onPickVocal;
  final Future<void> Function() onPickSong;
  final String? vocalName;
  final String? songName;
  final Future<void> Function(QuickControls controls) onAnalyze;
  final bool busy;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  Future<void> _submit() async {
    await widget.onAnalyze(const QuickControls());
  }

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
            'Drag & drop or tap to attach files. Vocal is required.',
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
                      child: Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.cloud_upload_rounded, size: 42),
                            const SizedBox(height: AppTheme.s12),
                            const Text('Drag & Drop Vocal / Song'),
                            const SizedBox(height: 4),
                            Text(
                              widget.vocalName != null
                                  ? 'Vocal: ${widget.vocalName}'
                                  : 'Mobile-friendly upload zone',
                              style: const TextStyle(color: AppTheme.textLow),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.center,
                            ),
                            if (widget.songName != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                'Song: ${widget.songName}',
                                style: const TextStyle(color: AppTheme.textLow),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                textAlign: TextAlign.center,
                              ),
                            ],
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
                          text: widget.vocalName == null ? 'Upload Vocal' : 'Vocal Uploaded',
                          icon: Icons.mic_rounded,
                          onPressed: widget.busy ? null : widget.onPickVocal,
                        ),
                      ),
                      const SizedBox(width: AppTheme.s12),
                      Expanded(
                        child: NeonButton(
                          text: widget.songName == null ? 'Upload Song' : 'Song Uploaded',
                          icon: Icons.library_music_rounded,
                          secondary: true,
                          onPressed: widget.busy ? null : widget.onPickSong,
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
            text: widget.busy ? 'Analyzing...' : 'Analyze My Voice',
            icon: Icons.auto_awesome_rounded,
            onPressed: widget.vocalName != null && !widget.busy ? _submit : null,
          ),
          if (widget.vocalName == null) ...[
            const SizedBox(height: AppTheme.s8),
            const Text(
              'Please upload a vocal file to continue.',
              style: TextStyle(color: AppTheme.textLow),
            ),
          ],
        ],
      ),
    );
  }
}
