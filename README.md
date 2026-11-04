# HausKaus

HausKaus is an offline-first Android business record book for small PNG trade stores.

## MVP foundation
- Kotlin, Jetpack Compose and Room local database
- Cash sales, credit sales, expenses and customer repayments
- PGK stored as integer toea (K1 = 100 toea)
- Oldest-first repayment allocation; overpayments are rejected
- Reversal records preserve the original event and reason
- Dashboard distinguishes sales, cash, expenses and receivables

This is a first development build, not yet a validated pilot or formal accounting product. It does not calculate profit.

## Build
Use the included Gradle wrapper: `./gradlew :app:assembleDebug`.
The GitHub Actions workflow builds, tests and uploads a debug APK for pull requests.
