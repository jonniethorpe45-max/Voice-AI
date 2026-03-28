class StyleControls {
  double warmth;
  double brightness;
  double power;
  double breathiness;
  double smoothness;
  double emotionIntensity;
  double softPitchStrength;

  StyleControls({
    this.warmth = 0.5,
    this.brightness = 0.5,
    this.power = 0.5,
    this.breathiness = 0.3,
    this.smoothness = 0.6,
    this.emotionIntensity = 0.6,
    this.softPitchStrength = 0.35,
  });

  Map<String, dynamic> toJson() => {
        'warmth': warmth,
        'brightness': brightness,
        'power': power,
        'breathiness': breathiness,
        'smoothness': smoothness,
        'emotion_intensity': emotionIntensity,
        'soft_pitch_strength': softPitchStrength,
      };
}

class JobStatus {
  final String status;
  final int progress;
  final String message;
  final String? error;

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

  factory JobStatus.fromJson(Map<String, dynamic> json) {
    return JobStatus(
      status: json['status'] as String? ?? 'unknown',
      progress: (json['progress'] as num?)?.toInt() ?? 0,
      message: json['message'] as String? ?? '',
      error: json['error'] as String?,
    );
  }
}

class VocalVariation {
  final String label;
  final String mediaUrl;
  final Map<String, dynamic> metadata;

  const VocalVariation({
    required this.label,
    required this.mediaUrl,
    required this.metadata,
  });

  factory VocalVariation.fromJson(Map<String, dynamic> json) {
    return VocalVariation(
      label: json['label'] as String? ?? 'Unknown',
      mediaUrl: json['media_url'] as String? ?? '',
      metadata: (json['metadata'] as Map<String, dynamic>?) ?? const {},
    );
  }
}

class JobResults {
  final String jobId;
  final String status;
  final String message;
  final Map<String, dynamic> analysis;
  final List<VocalVariation> variations;

  const JobResults({
    required this.jobId,
    required this.status,
    required this.message,
    required this.analysis,
    required this.variations,
  });

  factory JobResults.fromJson(Map<String, dynamic> json) {
    final raw = (json['variations'] as List<dynamic>? ?? []);
    return JobResults(
      jobId: json['job_id'] as String? ?? '',
      status: json['status'] as String? ?? 'unknown',
      message: json['message'] as String? ?? '',
      analysis: (json['analysis'] as Map<String, dynamic>?) ?? const {},
      variations: raw
          .whereType<Map<String, dynamic>>()
          .map(VocalVariation.fromJson)
          .toList(),
    );
  }
}
