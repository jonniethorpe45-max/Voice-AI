import 'package:flutter/material.dart';

import '../models.dart';
import '../widgets/primary_button.dart';

class ControlsScreen extends StatefulWidget {
  const ControlsScreen({
    super.key,
    required this.initial,
    required this.onApply,
    required this.onBack,
  });

  final StyleControls initial;
  final Future<void> Function(StyleControls controls) onApply;
  final VoidCallback onBack;

  @override
  State<ControlsScreen> createState() => _ControlsScreenState();
}

class _ControlsScreenState extends State<ControlsScreen> {
  late StyleControls _controls;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _controls = StyleControls(
      warmth: widget.initial.warmth,
      brightness: widget.initial.brightness,
      power: widget.initial.power,
      breathiness: widget.initial.breathiness,
      smoothness: widget.initial.smoothness,
      emotionIntensity: widget.initial.emotionIntensity,
      softPitchStrength: widget.initial.softPitchStrength,
    );
  }

  Widget _slider(
    String label,
    double value,
    ValueChanged<double> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        Slider(value: value, onChanged: onChanged),
      ],
    );
  }

  Future<void> _apply() async {
    setState(() => _submitting = true);
    try {
      await widget.onApply(_controls);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView(
        children: [
          const SizedBox(height: 8),
          const Text(
            'Vocal Style Controls',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          _slider('Warmth', _controls.warmth, (v) => setState(() => _controls.warmth = v)),
          _slider('Brightness', _controls.brightness, (v) => setState(() => _controls.brightness = v)),
          _slider('Power', _controls.power, (v) => setState(() => _controls.power = v)),
          _slider('Breathiness', _controls.breathiness, (v) => setState(() => _controls.breathiness = v)),
          _slider('Smoothness', _controls.smoothness, (v) => setState(() => _controls.smoothness = v)),
          _slider(
            'Emotion Intensity',
            _controls.emotionIntensity,
            (v) => setState(() => _controls.emotionIntensity = v),
          ),
          _slider(
            'Soft Pitch Guidance',
            _controls.softPitchStrength,
            (v) => setState(() => _controls.softPitchStrength = v),
          ),
          const SizedBox(height: 14),
          PrimaryButton(
            text: _submitting ? 'Applying...' : 'Apply & Reprocess',
            icon: Icons.check_circle_outline,
            onPressed: _submitting ? null : _apply,
          ),
          const SizedBox(height: 10),
          TextButton.icon(
            onPressed: _submitting ? null : widget.onBack,
            icon: const Icon(Icons.arrow_back),
            label: const Text('Back'),
          ),
        ],
      ),
    );
  }
}
