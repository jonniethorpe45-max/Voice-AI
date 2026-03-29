class VocalVersion {
  const VocalVersion({
    required this.id,
    required this.label,
    required this.fitScore,
    required this.duration,
    required this.waveSeed,
    this.bestFit = false,
  });

  final String id;
  final String label;
  final double fitScore;
  final String duration;
  final int waveSeed;
  final bool bestFit;
}

class QuickControls {
  const QuickControls({
    this.warmth = 0.56,
    this.brightness = 0.54,
    this.power = 0.6,
    this.emotion = 0.64,
    this.naturalEnhanced = 0.5,
  });

  final double warmth;
  final double brightness;
  final double power;
  final double emotion;
  final double naturalEnhanced;

  QuickControls copyWith({
    double? warmth,
    double? brightness,
    double? power,
    double? emotion,
    double? naturalEnhanced,
  }) {
    return QuickControls(
      warmth: warmth ?? this.warmth,
      brightness: brightness ?? this.brightness,
      power: power ?? this.power,
      emotion: emotion ?? this.emotion,
      naturalEnhanced: naturalEnhanced ?? this.naturalEnhanced,
    );
  }
}

class FineTuneState {
  const FineTuneState({
    this.vibrato = 0.45,
    this.breathiness = 0.35,
    this.toneColor = 0.52,
    this.pitchSoftness = 0.4,
    this.vocalPresence = 0.6,
  });

  final double vibrato;
  final double breathiness;
  final double toneColor;
  final double pitchSoftness;
  final double vocalPresence;

  FineTuneState copyWith({
    double? vibrato,
    double? breathiness,
    double? toneColor,
    double? pitchSoftness,
    double? vocalPresence,
  }) {
    return FineTuneState(
      vibrato: vibrato ?? this.vibrato,
      breathiness: breathiness ?? this.breathiness,
      toneColor: toneColor ?? this.toneColor,
      pitchSoftness: pitchSoftness ?? this.pitchSoftness,
      vocalPresence: vocalPresence ?? this.vocalPresence,
    );
  }
}
