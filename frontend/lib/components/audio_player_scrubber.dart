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

  @override
  Widget build(BuildContext context) {
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
              '${(_position * 100).toStringAsFixed(0)}%',
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
