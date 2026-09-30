import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:certinexus/app/app.dart';
import 'package:certinexus/shared/widgets/glass_card.dart';
import 'package:certinexus/shared/widgets/primary_button.dart';
import 'package:certinexus/shared/widgets/status_badge.dart';

void main() {
  testWidgets('CertiNexus AI app initialization test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: CertiNexusApp(),
      ),
    );

    // Initial frame rendered successfully
    expect(find.byType(CertiNexusApp), findsOneWidget);
  });

  testWidgets('PrimaryButton renders and responds to tap', (WidgetTester tester) async {
    bool tapped = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PrimaryButton(
            text: 'Test Button',
            onPressed: () => tapped = true,
          ),
        ),
      ),
    );

    expect(find.text('Test Button'), findsOneWidget);
    await tester.tap(find.text('Test Button'));
    expect(tapped, isTrue);
  });

  testWidgets('ConfidenceBadge displays correct level and percentage', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ConfidenceBadge(confidence: 0.94),
        ),
      ),
    );

    expect(find.text('High (94%)'), findsOneWidget);
  });

  testWidgets('GlassCard renders child content', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: GlassCard(
            child: Text('Frosted Content'),
          ),
        ),
      ),
    );

    expect(find.text('Frosted Content'), findsOneWidget);
  });
}
