import 'dart:async';

import 'package:flutter/material.dart';

import '../components/animated_waveform.dart';
import '../components/audio_player_scrubber.dart';
import '../components/floating_glow_button.dart';
import '../components/glass_card.dart';
import '../components/glow_slider.dart';
import '../components/neon_button.dart';
import '../core/app_models.dart';
import '../services/audio_player_service.dart';
import '../theme/app_theme.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({
    super.key,
    required this.trackName,
    required this.trackDuration,
    required this.versions,
    required this.selected,
    required this.controls,
    required this.onSelect,
    required this.onControlsChanged,
    required this.onMakeBetter,
    required this.onFineTune,
    required this.onExport,
  });

  final String trackName;
  final String trackDuration;
  final List<VocalVersion> versions;
  final VocalVersion selected;
  final QuickControls controls;
  final ValueChanged<VocalVersion> onSelect;
  final ValueChanged<QuickControls> onControlsChanged;
  final VoidCallback onMakeBetter;
  final VoidCallback onFineTune;
  final VoidCallback onExport;

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  final AudioPlayerService _playerService = AudioPlayerService();
  Timer? _ticker;
  String? _playbackError;

  @override
  void initState() {
    super.initState();
    _ticker = Timer.periodic(const Duration(milliseconds: 250), (_) {
      if (!mounted) {
        return;
      }
      if (_playerService.anyPlaying || _playerService.anyLoading) {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    _ticker?.cancel();
    _playerService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.s20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          GlassCard(
            child: Row(
              children: [
                const Icon(Icons.music_note_rounded, color: AppTheme.neonBlue),
                const SizedBox(width: AppTheme.s12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.trackName,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        widget.trackDuration,
                        style: const TextStyle(color: AppTheme.textLow),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppTheme.s16),
          Text('Versions', style: Theme.of(context).textTheme.headlineSmall),
          if (_playbackError != null) ...[
            const SizedBox(height: AppTheme.s8),
            Text(
              _playbackError!,
              style: const TextStyle(color: Colors.orangeAccent, fontSize: 12),
            ),
          ],
          const SizedBox(height: AppTheme.s12),
          SizedBox(
            height: 216,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: widget.versions.length,
              separatorBuilder: (_, __) => const SizedBox(width: AppTheme.s12),
              itemBuilder: (context, index) {
                final v = widget.versions[index];
                final active = v.id == widget.selected.id;
                return GestureDetector(
                  onTap: () => widget.onSelect(v),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    width: 232,
                    padding: const EdgeInsets.all(AppTheme.s16),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(AppTheme.r20),
                      border: Border.all(
                        color: active ? AppTheme.neonBlue : AppTheme.border,
                        width: active ? 1.4 : 1.0,
                      ),
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [AppTheme.glassStrong, AppTheme.glass],
                      ),
                      boxShadow: [
                        if (active)
                          BoxShadow(
                            color: AppTheme.neonBlue.withOpacity(0.24),
                            blurRadius: 20,
                            spreadRadius: 1,
                          ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                v.label,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                  fontSize: 16,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            if (v.bestFit)
                              Container(
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppTheme.neonBlue.withOpacity(0.18),
                                  borderRadius: BorderRadius.circular(999),
                                  border: Border.all(
                                    color: AppTheme.neonBlue.withOpacity(0.6),
                                  ),
                                ),
                                child: const Text(
                                  'Best Fit',
                                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: AppTheme.s12),
                        AudioPlayerScrubber(
                          durationLabel: v.duration,
                          seed: v.waveSeed,
                          playing: _playerService.isPlaying(v.id),
                          position: _playerService.positionFactor(v.id),
                          buffered: _playerService.bufferedFactor(v.id),
                          loading: _playerService.isLoading(v.id),
                          onToggle: () async {
                            final ok = await _playerService.toggle(id: v.id, url: v.mediaUrl);
                            if (!mounted) {
                              return;
                            }
                            setState(() {
                              _playbackError = ok ? null : _playerService.lastErrorMessage;
                            });
                          },
                          onSeek: (value) async {
                            final ok = await _playerService.seekFactor(id: v.id, factor: value);
                            if (!mounted) {
                              return;
                            }
                            setState(() {
                              _playbackError = ok ? null : _playerService.lastErrorMessage;
                            });
                          },
                        ),
                        if (_playerService.lastError(v.id) != null) ...[
                          const SizedBox(height: 6),
                          Text(
                            _playerService.lastError(v.id)!,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Colors.orangeAccent,
                              fontSize: 11,
                            ),
                          ),
                        ],
                        const SizedBox(height: AppTheme.s8),
                        AnimatedWaveform(
                          height: 28,
                          bars: 28,
                          seed: v.waveSeed,
                          baseColor: AppTheme.neonBlue,
                        ),
                        const Spacer(),
                        Text(
                          'Song Fit ${v.fitScore.toStringAsFixed(1)}',
                          style: const TextStyle(color: AppTheme.textMedium),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: AppTheme.s16),
          Expanded(
            child: GlassCard(
              child: ListView(
                children: [
                  GlowSlider(
                    label: 'Warmth',
                    value: widget.controls.warmth,
                    onChanged: (v) =>
                        widget.onControlsChanged(widget.controls.copyWith(warmth: v)),
                  ),
                  GlowSlider(
                    label: 'Brightness',
                    value: widget.controls.brightness,
                    onChanged: (v) =>
                        widget.onControlsChanged(widget.controls.copyWith(brightness: v)),
                  ),
                  GlowSlider(
                    label: 'Power',
                    value: widget.controls.power,
                    onChanged: (v) =>
                        widget.onControlsChanged(widget.controls.copyWith(power: v)),
                  ),
                  GlowSlider(
                    label: 'Emotion',
                    value: widget.controls.emotion,
                    onChanged: (v) =>
                        widget.onControlsChanged(widget.controls.copyWith(emotion: v)),
                  ),
                  GlowSlider(
                    label: 'Natural ↔ Enhanced',
                    value: widget.controls.naturalEnhanced,
                    onChanged: (v) => widget.onControlsChanged(
                      widget.controls.copyWith(naturalEnhanced: v),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppTheme.s12),
          NeonButton(
            text: 'Make It Even Better',
            icon: Icons.auto_awesome_rounded,
            secondary: true,
            onPressed: widget.onMakeBetter,
          ),
          const SizedBox(height: AppTheme.s12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: widget.onFineTune,
                  icon: const Icon(Icons.tune_rounded),
                  label: const Text('Fine Tune'),
                ),
              ),
              const SizedBox(width: AppTheme.s12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: widget.onExport,
                  icon: const Icon(Icons.ios_share_rounded),
                  label: const Text('Export'),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.s12),
          Align(
            alignment: Alignment.centerRight,
            child: FloatingGlowButton(
              icon: Icons.graphic_eq_rounded,
              onPressed: widget.onMakeBetter,
              tooltip: 'AI Assist',
            ),
          ),
        ],
      ),
    );
  }
}
