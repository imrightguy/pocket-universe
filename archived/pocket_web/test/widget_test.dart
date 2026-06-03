import 'package:flutter_test/flutter_test.dart';

import 'package:pocket_web/main.dart';

void main() {
  testWidgets('PocketUniverseApp renders without error', (WidgetTester tester) async {
    await tester.pumpWidget(const PocketUniverseApp());

    // Verify the main screen renders with the app title
    expect(find.text('Pocket Universe'), findsOneWidget);
    expect(find.text('Generate'), findsOneWidget);
  });
}
