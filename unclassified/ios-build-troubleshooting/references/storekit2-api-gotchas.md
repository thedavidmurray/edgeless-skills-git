# StoreKit 2 API Gotchas

Field notes on StoreKit 2 entitlement and purchase pattern traps.

## Entitlement Check

- `Product.subscriptionStatus` does **not exist**.
- The correct runtime check is `product.currentEntitlement` (singular):
  ```swift
  let result = await product.currentEntitlement
  switch result {
  case .verified(let transaction):
      // Subscription is active
      print("Active until \(transaction.expirationDate)")
  case .unverified(_, let error):
      // Receipt validation failed or revoked
      print("Unverified: \(error)")
  }
  ```

## Purchase Flow

- Use `Product.purchase()` for one-time and subscription purchases alike.
- Always verify the result:
  ```swift
  let result = try await product.purchase()
  switch result {
  case .success(let verification):
      switch verification {
      case .verified(let transaction):
          await transaction.finish()
      case .unverified(_, let error):
          // Handle server-side verification failure
      }
  case .userCancelled:
      break
  case .pending:
      // Waiting for parent approval (SKAN / family)
  @unknown default:
      break
  }
  ```

## Product Lookup

- Query products with a static ID set:
  ```swift
  let products = try await Product.products(for: ["premium_monthly", "premium_yearly"])
  ```

## Receipt Caveat

- StoreKit 2 uses server-to-server notifications + `currentEntitlement`.
- Do NOT parse `appStoreReceiptURL` manually unless you have a legacy path.