# Keep JavaScript bridge methods available in release builds.
-keepclassmembers class com.personal.attendance.MainActivity$AndroidBridge {
    @android.webkit.JavascriptInterface <methods>;
}
