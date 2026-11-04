# Gradle configuration examples

Examples only; adapt version numbers to your project and check compatibility first.

## Minimal application module (`app/build.gradle.kts`)
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")   // omit for Java-only projects
}

android {
    namespace = "com.example.myapp"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }
}
```

## Optional release signing (used only by `android-release.yml` with `sign=true`)
Reads the four values the workflow passes as Gradle properties. Without them the release APK stays unsigned and debug builds are unaffected.
```kotlin
android {
    signingConfigs {
        create("release") {
            val storeFile = providers.gradleProperty("RELEASE_STORE_FILE").orNull
            if (storeFile != null) {
                this.storeFile = file(storeFile)
                storePassword = providers.gradleProperty("RELEASE_STORE_PASSWORD").get()
                keyAlias = providers.gradleProperty("RELEASE_KEY_ALIAS").get()
                keyPassword = providers.gradleProperty("RELEASE_KEY_PASSWORD").get()
            }
        }
    }
    buildTypes {
        release {
            if (providers.gradleProperty("RELEASE_STORE_FILE").isPresent) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
    }
}
```

## Preparing the keystore secret (on a computer)
```
base64 -w0 release.keystore > keystore.b64   # paste the file contents into the ANDROID_KEYSTORE_BASE64 secret
```
Then delete `keystore.b64`. Never commit the keystore.
