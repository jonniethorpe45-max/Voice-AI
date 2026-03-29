import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';

import '../core/app_models.dart';

class ApiClient {
  ApiClient({required this.baseUrl});

  final String baseUrl;

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<String> upload({
    required String vocalPath,
    String? instrumentalPath,
  }) async {
    final request = http.MultipartRequest('POST', _uri('/upload'));
    request.files.add(await _filePart('vocal_track', vocalPath));
    if (instrumentalPath != null && instrumentalPath.isNotEmpty) {
      request.files.add(await _filePart('instrumental_track', instrumentalPath));
    }
    final response = await request.send();
    final body = await response.stream.bytesToString();
    if (response.statusCode >= 400) {
      throw Exception('Upload failed (${response.statusCode}): $body');
    }
    return (jsonDecode(body) as Map<String, dynamic>)['job_id'] as String;
  }

  Future<ProcessResponseModel> process({
    required String jobId,
    required QuickControls controls,
  }) async {
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
      throw Exception('Process failed (${response.statusCode}): ${response.body}');
    }
    return ProcessResponseModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<JobStatus> status(String jobId) async {
    final response = await http.get(_uri('/status/$jobId'));
    if (response.statusCode >= 400) {
      throw Exception('Status failed (${response.statusCode}): ${response.body}');
    }
    return JobStatus.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<JobResultsModel> results(String jobId) async {
    final response = await http.get(_uri('/results/$jobId'));
    if (response.statusCode >= 400) {
      throw Exception('Results failed (${response.statusCode}): ${response.body}');
    }
    return JobResultsModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
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
