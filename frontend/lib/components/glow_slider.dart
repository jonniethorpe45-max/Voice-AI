import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class GlowSlider extends StatelessWidget {
  const GlowSlider({
    super.key,
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final double value;
  final ValueChanged<double> onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: AppTheme.textMedium,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 4),
        ShaderMask(
          shaderCallback: (rect) {
            return const LinearGradient(
              colors: [AppTheme.neonBlue, AppTheme.neonPurple],
            ).createShader(rect);
          },
          child: Slider(
            value: value,
            min: 0,
            max: 1,
            onChanged: onChanged,
          ),
        ),
        const SizedBox(height: 2),
      ],
    );
  }
}
