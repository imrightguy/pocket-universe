import 'dart:math';
import 'package:flutter/material.dart';
import 'api.dart';
import 'world_page.dart';

void main() {
  runApp(const PocketUniverseApp());
}

class PocketUniverseApp extends StatelessWidget {
  const PocketUniverseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pocket Universe',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF6ecf7e),
          secondary: const Color(0xFFe8c86a),
          surface: const Color(0xFF1a1a2e),
          onSurface: const Color(0xFFe0e0e0),
        ),
        scaffoldBackgroundColor: const Color(0xFF0f0f1a),
        fontFamily: 'monospace',
      ),
      home: const WorldListScreen(),
    );
  }
}

class WorldListScreen extends StatefulWidget {
  const WorldListScreen({super.key});

  @override
  State<WorldListScreen> createState() => _WorldListScreenState();
}

class _WorldListScreenState extends State<WorldListScreen> {
  final PocketUniverseApi _api = PocketUniverseApi();
  List<String> _seeds = [];
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSeeds();
  }

  Future<void> _loadSeeds() async {
    setState(() => _loading = true);
    try {
      final seeds = await _api.getSeeds();
      setState(() {
        _seeds = seeds;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _seeds = PocketUniverseApi.defaultSeeds();
        _loading = false;
      });
    }
  }

  void _generateWorld(String seed) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => WorldPage(seed: seed)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('POCKET UNIVERSE'),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.casino),
            tooltip: 'Surprise me!',
            onPressed: _seeds.isNotEmpty
                ? () => _generateWorld(_seeds[Random().nextInt(_seeds.length)])
                : null,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select a seed to generate a universe',
              style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey),
            ),
            if (_loading) ...[
              const SizedBox(height: 24),
              const Center(child: CircularProgressIndicator()),
            ],
            if (_error != null) ...[
              const SizedBox(height: 16),
              Text('Error: $_error', style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 16),
            Expanded(
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 4,
                  childAspectRatio: 1.2,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: _seeds.length,
                itemBuilder: (context, index) {
                  final seed = _seeds[index];
                  return _SeedCard(
                    seed: seed,
                    onTap: () => _generateWorld(seed),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SeedCard extends StatelessWidget {
  final String seed;
  final VoidCallback onTap;

  const _SeedCard({required this.seed, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF16213e),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.public, color: Colors.green[300], size: 32),
              const SizedBox(height: 8),
              Text(
                seed.toUpperCase(),
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
