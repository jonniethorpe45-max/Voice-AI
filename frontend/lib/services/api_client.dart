import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';

import '../core/app_models.dart';

class ApiClient {
  ApiClient({required String baseUrl}) : baseUrl = _normalizeBaseUrl(baseUrl);

  final String baseUrl;

  static String _normalizeBaseUrl(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) {
      return 'http://localhost:8000';
    }
    return trimmed.endsWith('/') ? trimmed.substring(0, trimmed.length - 1) : trimmed;
  }

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  String absoluteMediaUrl(String mediaUrl) {
    final trimmed = mediaUrl.trim();
    if (trimmed.isEmpty) {
      return '';
    }
    final parsed = Uri.tryParse(trimmed);
    if (parsed != null && parsed.hasScheme && parsed.hasAuthority) {
      return trimmed;
    }
    if (trimmed.startsWith('/')) {
      return '$baseUrl$trimmed';
    }
    return '$baseUrl/$trimmed';
  }

  String _errorMessage(String action, http.BaseResponse response, String body) {
    if (response.statusCode == 404) {
      return '$action failed: resource not found (404).';
    }
    if (response.statusCode == 409) {
      return '$action failed: job state conflict (409).';
    }
    if (response.statusCode == 413) {
      return '$action failed: file too large (413).';
    }
    if (response.statusCode >= 500) {
      return '$action failed: server error (${response.statusCode}).';
    }
    return '$action failed (${response.statusCode}): $body';
  }

  Future<String> upload({
    required String vocalPath,
    String? instrumentalPath,
  }) async {
    try {
      final request = http.MultipartRequest('POST', _uri('/upload'));
      request.files.add(await _filePart('vocal_track', vocalPath));
      if (instrumentalPath != null && instrumentalPath.isNotEmpty) {
        request.files.add(await _filePart('instrumental_track', instrumentalPath));
      }
      final response = await request.send();
      final body = await response.stream.bytesToString();
      if (response.statusCode >= 400) {
        throw Exception(_errorMessage('Upload', response, body));
      }
      return (jsonDecode(body) as Map<String, dynamic>)['job_id'] as String;
    } on SocketException {
      throw Exception('Upload failed: network unavailable.');
    } on HttpException {
      throw Exception('Upload failed: unable to reach API server.');
    }
  }

  Future<ProcessResponseModel> process({
    required String jobId,
    required QuickControls controls,
  }) async {
    try {
      final response = await http.post(
        _uri('/process'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'job_id': jobId,
          'style_controls': controls.toApiJson(),
          'preferred_variations': const <String>[],
        }),
      );
      if (response.statusCode >= 400) {
        throw Exception(_errorMessage('Process', response, response.body));
      }
      return ProcessResponseModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } on SocketException {
      throw Exception('Process failed: network unavailable.');
    } on HttpException {
      throw Exception('Process failed: unable to reach API server.');
    }
  }

  Future<JobStatus> status(String jobId) async {
    try {
      final response = await http.get(_uri('/status/$jobId'));
      if (response.statusCode >= 400) {
        throw Exception(_errorMessage('Status', response, response.body));
      }
      return JobStatus.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } on SocketException {
      throw Exception('Status check failed: network unavailable.');
    } on HttpException {
      throw Exception('Status check failed: unable to reach API server.');
    }
  }

  Future<JobResultsModel> results(String jobId) async {
    try {
      final response = await http.get(_uri('/results/$jobId'));
      if (response.statusCode >= 400) {
        throw Exception(_errorMessage('Results', response, response.body));
      }
      return JobResultsModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } on SocketException {
      throw Exception('Results failed: network unavailable.');
    } on HttpException {
      throw Exception('Results failed: unable to reach API server.');
    }
  }

  Future<http.MultipartFile> _filePart(String field, String path) async {
    final mime = lookupMimeType(path) ?? 'audio/wav';
    final split = mime.split('/');
    return http.MultipartFile.fromPath(
      field,
      path,
      filename: File(path).uri.pathSegments.last,
      contentType: MediaType(
        split.isNotEmpty ? split.first : 'audio',
        split.length > 1 ? split[1] : 'wav',
      ),
    );
  }
}
