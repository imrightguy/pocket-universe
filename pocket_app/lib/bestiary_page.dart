import 'package:flutter/material.dart';

class BestiaryPage extends StatelessWidget {
  final List<Map<String, dynamic>> creatures;
  final String worldName;
  final String seed;

  const BestiaryPage({
    super.key,
    required this.creatures,
    required this.worldName,
    required this.seed,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('BESTIARY'),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: creatures.length,
        itemBuilder: (context, index) {
          final c = creatures[index];
          return _CreatureCard(creature: c, index: index);
        },
      ),
    );
  }
}

class _CreatureCard extends StatelessWidget {
  final Map<String, dynamic> creature;
  final int index;

  const _CreatureCard({required this.creature, required this.index});

  @override
  Widget build(BuildContext context) {
    final name = creature['name'] as String? ?? 'Unknown';
    final height = creature['height_m'] as num? ?? 0;
    final diet = creature['diet'] as String? ?? '';
    final locomotion = creature['locomotion'] as String? ?? '';
    final coloration = creature['coloration'] as String? ?? '';
    final integument = creature['integument'] as String? ?? '';
    final activity = creature['activity_cycle'] as String? ?? '';
    final sense = creature['primary_sense'] as String? ?? '';
    final social = creature['social_structure'] as String? ?? '';
    final traits = (creature['traits'] as List<dynamic>?)?.cast<String>() ?? [];
    final notes = (creature['notes'] as List<dynamic>?)?.cast<String>() ?? [];

    return Card(
      color: const Color(0xFF16213e),
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.05)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: const Color(0xFF0a0a1a),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.white.withOpacity(0.1)),
                  ),
                  child: const Icon(Icons.bug_report,
                      size: 20, color: Color(0xFF81c784)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('#${index + 1}  $name',
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold)),
                      Text(
                        '$height m · $diet · $locomotion',
                        style: TextStyle(
                            color: Colors.grey[400], fontSize: 13),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(height: 1, color: Color(0xFF2a2a4a)),
            const SizedBox(height: 12),

            _StatRow('Coloration', coloration),
            _StatRow('Integument', integument),
            _StatRow('Activity', activity),
            _StatRow('Primary Sense', sense),
            _StatRow('Social Structure', social),

            if (traits.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('Traits',
                  style: TextStyle(
                      color: Colors.grey[500],
                      fontSize: 11,
                      letterSpacing: 1)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: traits
                    .map((t) => Chip(
                          label: Text(t, style: const TextStyle(fontSize: 11)),
                          backgroundColor: const Color(0xFF1a2a1a),
                          side: BorderSide.none,
                          padding: EdgeInsets.zero,
                          visualDensity: VisualDensity.compact,
                        ))
                    .toList(),
              ),
            ],

            if (notes.isNotEmpty) ...[
              const SizedBox(height: 8),
              ...notes.map((n) => Padding(
                    padding: const EdgeInsets.only(bottom: 2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• ',
                            style: TextStyle(color: Colors.amber[200])),
                        Expanded(
                          child: Text(n,
                              style: TextStyle(
                                  color: Colors.amber[200],
                                  fontSize: 12,
                                  fontStyle: FontStyle.italic)),
                        ),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}

class _StatRow extends StatelessWidget {
  final String label;
  final String value;
  const _StatRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$label: ',
              style: TextStyle(color: Colors.grey[500], fontSize: 13)),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}
