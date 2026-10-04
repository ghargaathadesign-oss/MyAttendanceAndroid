# Step 9 / v13.0 production R8 rules
# My Attendance release hardening for R8.
#
# WebView JavaScript bridge methods are invoked by JavaScript name at runtime.
# They must not be removed or renamed, and their runtime annotation must survive.
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations,AnnotationDefault,Signature,InnerClasses,EnclosingMethod

-keepclassmembers,allowoptimization class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep the bridge entry class itself stable enough for WebView/runtime inspection,
# while still allowing R8 to optimize its implementation.
-keep,allowoptimization class com.personal.attendance.MainActivity$AndroidBridge {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep Firebase/AndroidX consumer rules in control of their own reflective APIs.
# No broad -dontobfuscate/-dontoptimize rule is used here on purpose.
