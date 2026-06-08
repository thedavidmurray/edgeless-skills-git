# iOS Build Troubleshooting

## Overview
A comprehensive guide for resolving common iOS/macOS build errors, Swift compiler issues, and Xcode project problems encountered during development. Covers SwiftUI, StoreKit, App Intents, and general Xcode/Swift compilation issues.

## Common Error Patterns

### SwiftUI Compilation Errors

#### `Value of protocol type 'Any' cannot conform to 'View'; only struct/enum/class types can conform to protocols`

**Cause:** Passing a closure/result builder that returns `Any` instead of a concrete `View` type.

**Fix:** Ensure all branches in conditional views or generic code return the same concrete `View` type. Use `if/else` instead of `if` without `else`, or wrap in `@ViewBuilder`.

```swift
// BAD — returns `Any` due to conditional without else
if condition {
    Text("Hello")
}

// GOOD — concrete type `some View`
if condition {
    Text("Hello")
} else {
    EmptyView()
}

// GOOD — @ViewBuilder context
@ViewBuilder
var content: some View {
    if condition {
        Text("Hello")
    }
    // Implicit EmptyView when condition is false
}
```

#### `Value of protocol type 'Error' cannot conform to 'LocalizedError'; only struct/enum/class types can conform to protocols`

**Cause:** Attempting to throw/return a protocol existential (`Error`) where a concrete `LocalizedError` type is required.

**Fix:** Use concrete error types conforming to `LocalizedError`, or cast/erase at the call site.

```swift
// BAD
throw error as LocalizedError  // error is `Error` protocol

// GOOD
struct AppError: LocalizedError {
    var errorDescription: String? { ... }
}
throw AppError(message: "...")
```

#### `Key path value type 'Binding<Value>' cannot be converted to contextual type 'Binding<Value>'` / `Cannot convert value of type 'WritableKeyPath<Root, Value>' to expected argument type 'ReferenceWritableKeyPath<Root, Value>'`

**Cause:** `@Binding` used on a value type (struct) instead of a reference type (class/`@Observable`), or key path mismatch.

**Fix:** Use `@State` for value types, `@Bindable` for `@Observable` classes. For `NavigationSplitView` / `NavigationStack`, ensure `selection:` bindings are optional (`T?`) for optional paths.

```swift
// BAD — struct with @Binding
struct SettingsView: View {
    @Binding var model: Model  // Model is struct
}

// GOOD — @Observable class
@Observable
class Model { ... }

struct SettingsView: View {
    @Bindable var model: Model  // class
}
```

#### `Cannot convert value of type 'Binding<Value?>' to expected argument type 'Binding<Value>'` / `Initializer 'init(_:)' requires that 'Value' conform to 'Hashable'`

**Cause:** `Picker`, `List(selection:)`, `NavigationSplitView` require non-optional binding of `Hashable` type.

**Fix:** Provide a non-optional `Binding<T>` where `T: Hashable`. Handle optional selection via a computed binding or a default value.

```swift
// BAD — optional binding
NavigationSplitView(selection: $selectedItem) { ... }  // selectedItem is Item?

// GOOD — non-optional with default
@State private var selectedItem: Item.ID? = nil

NavigationSplitView(selection: $selectedItem) { ... }
// Or use a concrete default:
@State private var selectedItem: Item = .defaultItem
NavigationSplitView(selection: $selectedItem) { ... }
```

#### `The compiler is unable to type-check this expression in reasonable time`

**Cause:** Complex SwiftUI view body with too many nested generics, opaque return types, or overloaded operators.

**Fix:** Break into smaller subviews, add explicit type annotations, or use `AnyView` (as last resort).

```swift
// BAD — massive inline expression
var body: some View {
    VStack {
        HStack {
            Image(...).resizable().aspectRatio(...).frame(...)
            VStack(alignment: .leading) {
                Text(...).font(...).foregroundColor(...)
                Text(...).font(...).lineLimit(...)
            }
        }
        // ... 50 more modifiers
    }
}

// GOOD — extracted subviews
struct HeaderView: View { ... }
struct DetailView: View { ... }

var body: some View {
    VStack {
        HeaderView()
        DetailView()
    }
}
```

---

### Xcode Project / Build System Errors

#### `No such module 'ModuleName'` / `Cannot find 'ModuleName' in scope`

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| Missing framework in **Link Binary with Libraries** | Build Phases → Link Binary With Libraries → Add `+` |
| Missing **Framework Search Paths** | Build Settings → Framework Search Paths → add `$(inherited)` and custom paths |
| SPM package not resolved | File → Packages → Resolve Package Versions |
| Module cache stale | `rm -rf ~/Library/Developer/Xcode/DerivedData` |
| Wrong target/platform (macOS vs iOS) | Build Settings → Supported Platforms / Base SDK |
| `@testable import` in non-test target | Only works in test targets (Unit Tests / UI Tests) |

#### `Command CompileSwift failed with a nonzero exit code` / `Segmentation fault: 11`

**Causes:** Swift compiler crash — usually complex generics, deeply nested closures, or circular references.

**Fixes:**
1. Clean build folder: `Cmd+Shift+K` then `Cmd+B`
2. Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData`
3. Simplify the offending expression (break into smaller pieces)
4. Add explicit type annotations to help the type checker
5. Check for compiler bug — try latest Xcode / Swift version

**One-liner:**
```bash
rm -rf ~/Library/Developer/Xcode/DerivedData && xcodebuild clean
```

#### `Unable to find a destination matching the provided destination specifier`

**Cause:** Xcode can't find simulator/device matching build settings.

**Fix:**
```bash
# List available simulators
xcrun simctl list devices available

# Reset simulators
xcrun simctl erase all

# Or specify explicit destination
xcodebuild -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest'
```

#### `Provisioning profile "..." doesn't include the currently selected device`

**Cause:** Device UDID not in provisioning profile, or wrong signing team.

**Fix:**
1. Xcode → Settings → Accounts → Download Manual Profiles
2. Or: developer.apple.com → Certificates, Identifiers & Profiles → add device UDID
3. Check **Signing & Capabilities** → Team matches the profile

#### `The sandbox is not in sync with the Podfile.lock`

**Cause:** CocoaPods dependencies out of sync.

**Fix:**
```bash
pod deintegrate && pod install
# Or
rm -rf Pods/ Podfile.lock && pod install
```

---

### StoreKit / IAP Errors

#### `Cannot find 'Product' in scope` / `No such module 'StoreKit'`

**Cause:** StoreKit not imported, or using StoreKit 2 APIs on older iOS version without `@available`.

**Fix:**
```swift
import StoreKit

// For StoreKit 2 (iOS 15+)
if #available(iOS 15.0, macOS 12.0, tvOS 15.0, watchOS 8.0, *) {
    // StoreKit 2 APIs: Product, Transaction, etc.
}
```

#### `Type 'Product' has no member 'purchase'` / `Type 'Transaction' has no member 'current'`

**Cause:** Mixing StoreKit 1 and StoreKit 2 APIs, or wrong import.

**Fix:** Use consistent StoreKit version. StoreKit 2 uses async/await:
```swift
// StoreKit 2
let result = try await product.purchase()
switch result {
case .success(let verification):
    let transaction = try checkVerified(verification)
    await transaction.finish()
}

// Current entitlements (StoreKit 2)
for await result in Transaction.currentEntitlements {
    let transaction = try checkVerified(result)
    // process
}
```

#### `Value of optional type 'Transaction?' must be unwrapped`

**Cause:** StoreKit 2 transactions are `VerificationResult<Transaction>`, not plain `Transaction`.

**Fix:** Use `checkVerified()` helper:
```swift
func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .unverified(_, let error):
        throw error
    case .verified(let safe):
        return safe
    }
}
```

---

### App Intents / Shortcuts Errors

#### `Type 'IntentName' does not conform to protocol 'AppIntent'` / `AppIntent requires 'perform()' method`

**Cause:** Missing required methods or wrong return type in `perform()`.

**Fix:** Implement `perform()` returning `some IntentResult` or `some ReturnsValue`:
```swift
struct MyIntent: AppIntent {
    static var title: LocalizedStringResource = "My Intent"
    
    func perform() async throws -> some IntentResult {
        // Do work
        return .result()
    }
}

// With return value:
struct MyQueryIntent: AppIntent {
    func perform() async throws -> some ReturnsValue<String> {
        let result = await fetchData()
        return .result(value: result)
    }
}
```

#### `AppIntent requires property 'title' to be 'LocalizedStringResource'`

**Cause:** Using `String` instead of `LocalizedStringResource`.

**Fix:**
```swift
static var title: LocalizedStringResource = "My Intent Title"
// NOT:
// static var title: String = "My Intent Title"  // ❌
```

#### `Cannot find 'AppIntent' in scope`

**Cause:** Missing `AppIntents` framework import.

**Fix:**
```swift
import AppIntents
```

---

### Swift Concurrency / Async-Await Errors

#### `Expression is 'async' but is not marked with 'await'`

**Cause:** Calling async function without `await`.

**Fix:**
```swift
// BAD
let result = fetchData()

// GOOD
let result = await fetchData()
```

#### `Call can throw, but it is not marked with 'try' and the error is not handled`

**Fix:**
```swift
// Option 1: try + do/catch
do {
    let result = try await fetchData()
} catch {
    // handle
}

// Option 2: try?
let result = try? await fetchData()  // Optional

// Option 3: try!
let result = try! await fetchData()  // Force unwrap (crash on error)
```

#### `Actor-isolated property 'propertyName' can not be mutated from a non-isolated context`

**Cause:** Accessing `@MainActor` or actor-isolated state from non-isolated context.

**Fix:**
```swift
// Option 1: @MainActor
@MainActor
func updateUI() {
    self.count += 1  // MainActor-isolated property
}

// Option 2: await MainActor.run
await MainActor.run {
    self.count += 1
}

// Option 3: Task with @MainActor
Task { @MainActor in
    self.count += 1
}
```

---

### General Swift Errors

#### `Cannot assign to property: 'self' is immutable` / `Cannot use mutating member on immutable value`

**Cause:** Modifying struct property in non-mutating context, or modifying constant (`let`).

**Fix:**
```swift
// BAD — struct in let
let model = Model()
model.count += 1  // ❌

// GOOD — var
var model = Model()
model.count += 1  // ✅

// BAD — non-mutating method
struct Counter {
    var count = 0
    func increment() { count += 1 }  // ❌
}

// GOOD
struct Counter {
    var count = 0
    mutating func increment() { count += 1 }  // ✅
}
```

#### `Type 'X' does not conform to protocol 'Y'` — Stub fixer

**Fix:** Let Xcode auto-fill stubs:
1. Click the red error indicator
2. Click **Fix** → "Add protocol stubs"
3. Or: `Cmd+.` (Quick Fix) on the error line

#### `Initializer 'init()' requires that 'T' conform to 'Initiable'`

**Cause:** Generic constraint missing.

**Fix:** Add constraint to generic parameter:
```swift
// BAD
func create<T>() -> T {
    return T()  // ❌ T might not have init()
}

// GOOD
func create<T: Initiable>() -> T {
    return T()  // ✅
}
```

---

## Quick Reference: Fix Priorities

| Priority | Error Type | Fix Time |
|----------|-----------|----------|
| 🔴 P0 | Compiler crash / segfault | 5-30 min (clean + simplify) |
| 🔴 P0 | Missing module / framework | 2-10 min (add import / SPM) |
| 🟡 P1 | Protocol conformance / generics | 5-15 min (add stubs / constraints) |
| 🟡 P1 | SwiftUI type-checker timeout | 10-30 min (break into subviews) |
| 🟢 P2 | Optional binding / unwrap | 1-5 min (add `?` / `!` / `if let`) |
| 🟢 P2 | @MainActor / concurrency | 2-5 min (add `await MainActor.run`) |

## One-Liner Commands

```bash
# Nuclear option — clean everything
rm -rf ~/Library/Developer/Xcode/DerivedData && xcodebuild clean

# Reset SPM
rm -rf .build/ Package.resolved && swift package resolve

# Reset CocoaPods
pod deintegrate && pod install

# Reset simulators
xcrun simctl erase all

# Check Swift version
swift --version

# Build from CLI
xcodebuild -scheme MyScheme -destination 'platform=iOS Simulator,name=iPhone 15 Pro' build
```

## Prevention Checklist

Before every build:
- [ ] Clean build folder (`Cmd+Shift+K`)
- [ ] Derived data cleared (if weird errors)
- [ ] SPM/CocoaPods resolved
- [ ] Target / platform settings correct
- [ ] Signing team + provisioning matches
- [ ] Simulator/device available and selected

## Related Skills
- `swiftui-architecture` — SwiftUI app structure patterns
- `storekit-iap` — In-app purchase implementation
- `xcode-project-management` — Xcode project/workspace setup
- `swift-concurrency` — async/await, actors, structured concurrency
