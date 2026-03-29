import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class AudioPlayerScrubber extends StatelessWidget {
  const AudioPlayerScrubber({
    super.key,
    required this.durationLabel,
    required this.seed,
    required this.playing,
    required this.position,
    required this.onToggle,
    required this.onSeek,
    this.buffered = 0.0,
    this.loading = false,
  });

  final String durationLabel;
  final int seed;
  final bool playing;
  final double position;
  final double buffered;
  final bool loading;
  final VoidCallback onToggle;
  final ValueChanged<double> onSeek;

  String _fmt(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  int _durationSeconds() {
    final parts = durationLabel.split(':');
    if (parts.length != 2) {
      return 0;
    }
    final minutes = int.tryParse(parts[0]) ?? 0;
    final seconds = int.tryParse(parts[1]) ?? 0;
    return (minutes * 60) + seconds;
  }

  @override
  Widget build(BuildContext context) {
    final durationSec = _durationSeconds();
    final clampedPos = position.clamp(0.0, 1.0);
    final clampedBuffered = buffered.clamp(0.0, 1.0);
    final currentSec = (durationSec * clampedPos).round();
    return Column(
      children: [
        Row(
          children: [
            GestureDetector(
              onTap: onToggle,
              child: Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppTheme.neonBlue.withOpacity(0.16),
                  border: Border.all(color: AppTheme.neonBlue.withOpacity(0.6)),
                ),
                child: loading
                    ? const Padding(
                        padding: EdgeInsets.all(8),
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppTheme.neonBlue,
                        ),
                      )
                    : Icon(
                        playing ? Icons.pause_rounded : Icons.play_arrow_rounded,
                        color: AppTheme.neonBlue,
                        size: 20,
                      ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SliderTheme(
                    data: SliderTheme.of(context).copyWith(
                      thumbShape: SliderComponentShape.noThumb,
                      overlayShape: SliderComponentShape.noOverlay,
                      activeTrackColor: Colors.white24,
                      inactiveTrackColor: Colors.white10,
                    ),
                    child: Slider(
                      value: clampedBuffered,
                      min: 0,
                      max: 1,
                      onChanged: (_) {},
                    ),
                  ),
                  Slider(
                    value: clampedPos,
                    min: 0,
                    max: 1,
                    onChanged: onSeek,
                  ),
                ],
              ),
            ),
          ],
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _fmt(currentSec),
              style: const TextStyle(color: AppTheme.textLow, fontSize: 11),
            ),
            Text(
              durationLabel,
              style: const TextStyle(color: AppTheme.textLow, fontSize: 11),
            ),
          ],
        ),
      ],
    );
  }
}
