# Phone workflow (first-time guide)

You only need a phone, a browser and a GitHub account. The GitHub mobile app is fine for monitoring, but file upload, artifacts and settings are easier in the browser. If a page looks cut down, use your browser menu → **Desktop site**.

## A. Create your project repository from the template
1. Open the template repository in your browser.
2. Tap **Use this template → Create a new repository**.
3. Name it, choose **Public** (free minutes, but code is visible) or **Private** (uses your monthly included minutes; see FREE_USAGE_AND_BILLING.md), then **Create**.

## B. Add your Android project
4. In your new repository: **Add file → Upload files**.
5. Upload the project files at the repository root. You need `gradlew`, `gradle/wrapper/gradle-wrapper.jar`, `gradle/wrapper/gradle-wrapper.properties`, `settings.gradle(.kts)`, `build.gradle(.kts)` and the `app/` folder. Uploading folders from a phone browser can be unreliable; if it is, upload a few files at a time or use the GitHub web editor (**Add file → Create new file**, type `folder/name` to create a path).
6. Tap **Commit changes**.

## C. Run the build
7. Open the **Actions** tab. If asked, tap **I understand my workflows, go ahead and enable them**.
8. Tap **Android build and test → Run workflow → Run workflow**. (A push to `main` also starts it.)
9. Tap the new run to watch progress. Typical first run: several minutes.

## D. If it fails
10. Open the run summary at the top, then the failed step's log. Follow `DEBUGGING_GUIDE.md`. Send the first error to ChatGPT or Claude.

## E. If it succeeds
11. On the run page scroll to **Artifacts** and tap `android-debug-apk-run<N>`. You get a ZIP file.
12. Open it with your Files app (tap → **Extract**) to get the `.apk`.
13. Tap the APK. Android will ask permission to install from your browser or Files app ("install unknown apps"); allow it for this install only. Play Protect may warn about an unrecognised debug app; this is expected for a debug build you made yourself. Do not install APKs from sources you do not trust.
14. Open the app and test it.

## F. Fix and repeat
15. Report problems to ChatGPT or Claude with the app's behaviour and the run link.
16. Upload corrected files (GitHub overwrites same-named files), commit, and the workflow runs again.

## Notes
- Artifacts expire (default 7 days here). Download what you need.
- Artifacts in public repositories can be downloaded by any signed-in GitHub user.
- No Linux terminal, Android Studio, Expo Go or paid service is needed.
