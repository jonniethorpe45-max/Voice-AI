import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class NeonButton extends StatefulWidget {
  const NeonButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.icon,
    this.secondary = false,
  });

  final String text;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool secondary;

  @override
  State<NeonButton> createState() => _NeonButtonState();
}

class _NeonButtonState extends State<NeonButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final accent = widget.secondary ? AppTheme.neonPurple : AppTheme.neonBlue;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(AppTheme.r16),
        boxShadow: [
          BoxShadow(
            color: accent.withOpacity(_hover ? 0.56 : 0.28),
            blurRadius: _hover ? 26 : 14,
            spreadRadius: _hover ? 1.2 : 0,
          ),
        ],
      ),
      child: ElevatedButton.icon(
        onPressed: widget.onPressed,
        onHover: (value) => setState(() => _hover = value),
        icon: Icon(widget.icon ?? Icons.auto_awesome_rounded),
        label: Text(widget.text),
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(56),
          elevation: 0,
          backgroundColor: accent.withOpacity(widget.secondary ? 0.16 : 0.22),
          foregroundColor: AppTheme.textHigh,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.r16),
            side: BorderSide(color: accent.withOpacity(0.65)),
          ),
        ),
      ),
    );
  }
}
