import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class FloatingGlowButton extends StatefulWidget {
  const FloatingGlowButton({
    super.key,
    required this.icon,
    required this.onPressed,
    this.tooltip,
  });

  final IconData icon;
  final VoidCallback onPressed;
  final String? tooltip;

  @override
  State<FloatingGlowButton> createState() => _FloatingGlowButtonState();
}

class _FloatingGlowButtonState extends State<FloatingGlowButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: widget.tooltip ?? '',
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: AppTheme.neonBlue.withOpacity(_hovering ? 0.55 : 0.3),
              blurRadius: _hovering ? 24 : 14,
              spreadRadius: _hovering ? 1.5 : 0,
            ),
          ],
        ),
        child: FloatingActionButton(
          onPressed: widget.onPressed,
          backgroundColor: AppTheme.neonBlue.withOpacity(0.2),
          foregroundColor: AppTheme.textHigh,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
            side: BorderSide(color: AppTheme.neonBlue.withOpacity(0.7)),
          ),
          child: MouseRegion(
            onEnter: (_) => setState(() => _hovering = true),
            onExit: (_) => setState(() => _hovering = false),
            child: Icon(widget.icon),
          ),
        ),
      ),
    );
  }
}
