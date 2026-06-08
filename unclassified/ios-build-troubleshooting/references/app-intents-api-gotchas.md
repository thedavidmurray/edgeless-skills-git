# App Intents API Gotchas

Condensed field notes from fixing App Intents compilation errors in iOS 26 / Xcode 16.

## AppShortcutsProvider

- **Result builder**, not an array literal. Do NOT wrap `AppShortcut(...)` in `[ ]`.
  ```swift
  // WRONG
  static var appShortcuts: [AppShortcut] {
      [ AppShortcut(...) ]
  }

  // CORRECT
  static var appShortcuts: [AppShortcut] {
      AppShortcut(...)
  }
  ```

- **Multiple shortcuts**: result builders support arrays naturally; if you need more than one, add them in sequence:
  ```swift
  static var appShortcuts: [AppShortcut] {
      AppShortcut(intent: A(), phrases: ["..."])
      AppShortcut(intent: B(), phrases: ["..."])
  }
  ```

## ParameterSummary

- Property wrapper syntax uses `$` prefix:
  ```swift
  Summary("When \(\.$gesture) is detected, \(\.$action)")
  ```

## App Shortcut Phrases

- **Every phrase MUST contain** `\(.applicationName)`.
- Phrases without it fail the `appintentsmetadataprocessor` export step with:
  > `Invalid Utterance. Every App Shortcut utterance should have one '${applicationName}' in it.`
- Keep phrases simple and literal; avoid user-specific pronouns ("I clap") unless the app name is present.

## Enum String Representation

- Enum cases do NOT have `.intentName` or similar derived properties.
- Use `.rawValue` (if `String`-backed) or compute a mapping:
  ```swift
  let notificationName = "com.edgeless.clapper.\(type.rawValue)"
  ```

## Quick API Shape Probe

Use `swiftc -typecheck` to validate syntax without a full Xcode build:
```bash
cat > /tmp/probe.swift << 'EOF'
import AppIntents
struct P: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: TestIntent(),
            phrases: ["When \(.applicationName) does X"],
            shortTitle: "X",
            systemImageName: "hand.wave.fill"
        )
    }
}
struct TestIntent: AppIntent {
    static var title: LocalizedStringResource = "Test"
    func perform() async throws -> some IntentResult { .result() }
}
EOF
swiftc -typecheck /tmp/probe.swift
```