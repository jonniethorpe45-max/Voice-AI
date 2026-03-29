import 'package:flutter/material.dart';

import '../components/glass_card.dart';
import '../components/glow_slider.dart';
import '../components/neon_button.dart';
import '../core/app_models.dart';
import '../theme/app_theme.dart';

class FineTuneScreen extends StatelessWidget {
  const FineTuneScreen({
    super.key,
    required this.state,
    required this.onChanged,
    required this.onApply,
    required this.onBack,
  });

  final FineTuneState state;
  final ValueChanged<FineTuneState> onChanged;
  final VoidCallback onApply;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.s20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextButton.icon(
            onPressed: onBack,
            icon: const Icon(Icons.arrow_back),
            label: const Text('Back'),
          ),
          const SizedBox(height: AppTheme.s8),
          Text('Fine Tune', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppTheme.s8),
          Text(
            'Advanced control with minimal complexity.',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: AppTheme.s16),
          Expanded(
            child: GlassCard(
              child: ListView(
                children: [
                  GlowSlider(
                    label: 'Vibrato amount',
                    value: state.vibrato,
                    onChanged: (v) => onChanged(state.copyWith(vibrato: v)),
                  ),
                  GlowSlider(
                    label: 'Breathiness',
                    value: state.breathiness,
                    onChanged: (v) => onChanged(state.copyWith(breathiness: v)),
                  ),
                  GlowSlider(
                    label: 'Tone color',
                    value: state.toneColor,
                    onChanged: (v) => onChanged(state.copyWith(toneColor: v)),
                  ),
                  GlowSlider(
                    label: 'Pitch softness',
                    value: state.pitchSoftness,
                    onChanged: (v) => onChanged(state.copyWith(pitchSoftness: v)),
                  ),
                  GlowSlider(
                    label: 'Vocal presence',
                    value: state.vocalPresence,
                    onChanged: (v) => onChanged(state.copyWith(vocalPresence: v)),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppTheme.s16),
          NeonButton(
            text: 'Apply Fine Tune',
            icon: Icons.tune_rounded,
            onPressed: onApply,
          ),
        ],
      ),
    );
  }
}
