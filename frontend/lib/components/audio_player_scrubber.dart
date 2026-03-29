import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class AudioPlayerScrubber extends StatefulWidget {
  const AudioPlayerScrubber({
    super.key,
    required this.durationLabel,
    required this.seed,
  });

  final String durationLabel;
  final int seed;

  @override
  State<AudioPlayerScrubber> createState() => _AudioPlayerScrubberState();
}

class _AudioPlayerScrubberState extends State<AudioPlayerScrubber> {
  double _position = 0.0;
  bool _playing = false;

  String _fmt(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  int _durationSeconds() {
    final parts = widget.durationLabel.split(':');
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
    final currentSec = (durationSec * _position).round();
    return Column(
      children: [
        Row(
          children: [
            GestureDetector(
              onTap: () => setState(() => _playing = !_playing),
              child: Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppTheme.neonBlue.withOpacity(0.16),
                  border: Border.all(color: AppTheme.neonBlue.withOpacity(0.6)),
                ),
                child: Icon(
                  _playing ? Icons.pause_rounded : Icons.play_arrow_rounded,
                  color: AppTheme.neonBlue,
                  size: 20,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Slider(
                value: _position,
                min: 0,
                max: 1,
                onChanged: (v) => setState(() => _position = v),
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
              widget.durationLabel,
              style: const TextStyle(color: AppTheme.textLow, fontSize: 11),
            ),
          ],
        ),
      ],
    );
  }
}
