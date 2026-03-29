class VocalVersion {
  const VocalVersion({
    required this.id,
    required this.label,
    required this.fitScore,
    required this.duration,
    required this.waveSeed,
    this.mediaUrl = '',
    this.rank = 0,
    this.metadata = const {},
    this.bestFit = false,
  });

  final String id;
  final String label;
  final double fitScore;
  final String duration;
  final int waveSeed;
  final String mediaUrl;
  final int rank;
  final Map<String, dynamic> metadata;
  final bool bestFit;

  factory VocalVersion.fromResultJson(
    Map<String, dynamic> json, {
    required bool bestFit,
  }) {
    final label = json['label'] as String? ?? 'Variation';
    final metadata = (json['metadata'] as Map?)?.cast<String, dynamic>() ?? const {};
    return VocalVersion(
      id: label.toLowerCase().replaceAll(' ', '_'),
      label: label,
      fitScore: (json['song_fit_score'] as num?)?.toDouble() ?? 0.0,
      duration: _durationFromMetadata(metadata),
      waveSeed: _seedFrom(label),
      mediaUrl: json['media_url'] as String? ?? '',
      rank: (json['rank'] as num?)?.toInt() ?? 0,
      metadata: metadata,
      bestFit: bestFit,
    );
  }
}

class JobStatus {
  const JobStatus({
    required this.status,
    required this.progress,
    required this.message,
    this.error,
  });

  const JobStatus.initial()
      : status = 'idle',
        progress = 0,
        message = 'Idle',
        error = null;

  final String status;
  final int progress;
  final String message;
  final String? error;

  bool get isTerminal =>
      status == 'completed' ||
      status == 'completed_with_warnings' ||
      status == 'failed';

  factory JobStatus.fromJson(Map<String, dynamic> json) {
    return JobStatus(
      status: json['status'] as String? ?? 'unknown',
      progress: (json['progress'] as num?)?.toInt() ?? 0,
      message: json['message'] as String? ?? '',
      error: json['error'] as String?,
    );
  }
}

class ProcessResponseModel {
  const ProcessResponseModel({
    required this.jobId,
    required this.status,
    required this.queueTarget,
    required this.requiresGpu,
  });

  final String jobId;
  final String status;
  final String queueTarget;
  final bool requiresGpu;

  factory ProcessResponseModel.fromJson(Map<String, dynamic> json) {
    return ProcessResponseModel(
      jobId: json['job_id'] as String? ?? '',
      status: json['status'] as String? ?? 'queued',
      queueTarget: json['queue_target'] as String? ?? 'cpu',
      requiresGpu: json['requires_gpu'] as bool? ?? false,
    );
  }
}

class JobResultsModel {
  const JobResultsModel({
    required this.jobId,
    required this.status,
    required this.message,
    required this.selectedVariationLabel,
    required this.analysis,
    required this.variations,
  });

  final String jobId;
  final String status;
  final String message;
  final String? selectedVariationLabel;
  final Map<String, dynamic> analysis;
  final List<VocalVersion> variations;

  String? get songName {
    return analysis['song_name'] as String? ?? analysis['track_name'] as String?;
  }

  factory JobResultsModel.fromJson(Map<String, dynamic> json) {
    final selected = json['selected_variation_label'] as String?;
    final rawVariations = (json['variations'] as List<dynamic>? ?? const [])
        .whereType<Map>()
        .map((e) => e.cast<String, dynamic>())
        .toList();
    final versions = rawVariations.map((item) {
      final rank = (item['rank'] as num?)?.toInt() ?? 0;
      final label = item['label'] as String? ?? '';
      final best = selected != null ? label == selected : rank == 1;
      return VocalVersion.fromResultJson(item, bestFit: best);
    }).toList();
    return JobResultsModel(
      jobId: json['job_id'] as String? ?? '',
      status: json['status'] as String? ?? 'unknown',
      message: json['message'] as String? ?? '',
      selectedVariationLabel: selected,
      analysis: (json['analysis'] as Map?)?.cast<String, dynamic>() ?? const {},
      variations: versions,
    );
  }
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

  Map<String, dynamic> toApiJson() {
    return {
      'warmth': warmth,
      'brightness': brightness,
      'power': power,
      'breathiness': (1 - naturalEnhanced).clamp(0.0, 1.0),
      'smoothness': naturalEnhanced.clamp(0.0, 1.0),
      'emotion_intensity': emotion.clamp(0.0, 1.0),
      'soft_pitch_strength': (1 - naturalEnhanced).clamp(0.0, 1.0),
    };
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

String _durationFromMetadata(Map<String, dynamic> metadata) {
  final raw = metadata['duration_seconds'];
  if (raw is num) {
    final sec = raw.toInt().clamp(0, 35999);
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }
  final duration = metadata['duration'];
  if (duration is String && duration.isNotEmpty) {
    return duration;
  }
  return '03:24';
}

int _seedFrom(String value) {
  var hash = 7;
  for (final rune in value.runes) {
    hash = ((hash * 31) + rune) & 0x7fffffff;
  }
  return (hash % 10) + 1;
}
