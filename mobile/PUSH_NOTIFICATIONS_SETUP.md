# Push Notifications Setup Guide

## Current Status

The push notification infrastructure is **scaffolded** but uses **mock implementations**. The notification service structure is in place with device registration API integration, but real Firebase Cloud Messaging (FCM) is not yet implemented.

## Overview

To enable real push notifications, you need to:
1. Set up a Firebase project
2. Configure Firebase in the Android app
3. Install Firebase packages
4. Replace mock implementations with real Firebase calls

## Prerequisites

- Firebase account (Google account)
- Firebase project created
- Android app registered in Firebase Console

## Step-by-Step Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select existing project
3. Follow the setup wizard
4. Enable Google Analytics (optional but recommended)

### 2. Add Android App to Firebase

1. In Firebase Console, click "Add app" → Android
2. Enter package name: `pk.edu.pmc.consult`
3. Enter app nickname: "Consult Mobile" (optional)
4. Download `google-services.json`
5. **Place the file at:** `mobile/android/app/google-services.json`

### 3. Install Firebase Packages

Run the following command in the `mobile` directory:

```bash
cd mobile
npm install @react-native-firebase/app @react-native-firebase/messaging
```

For React Native 0.74.0, you may need to check compatible versions. Check the [React Native Firebase documentation](https://rnfirebase.io/) for the latest compatible versions.

### 4. Configure Gradle Files

#### Update `android/build.gradle`

Add the Google Services plugin to the project-level build.gradle:

```gradle
buildscript {
    dependencies {
        // ... existing dependencies
        classpath("com.google.gms:google-services:4.4.0")
    }
}
```

#### Update `android/app/build.gradle`

Add the plugin at the bottom of the file:

```gradle
apply plugin: "com.android.application"
// ... existing plugins

// Add at the bottom of the file:
apply plugin: "com.google.gms.google-services"
```

### 5. Update Notification Service

Replace the mock implementation in `mobile/src/services/notifications.ts`:

#### Current Mock Implementation Locations

The following functions need to be replaced:
- `requestNotificationPermission()` - Line ~93
- `getFCMToken()` - Line ~114
- `onForegroundNotification()` - Line ~162
- `onBackgroundNotification()` - Line ~174
- `onNotificationOpened()` - Line ~186

#### Example Implementation

```typescript
import messaging from '@react-native-firebase/messaging';

// Request permission
async function requestNotificationPermission(): Promise<boolean> {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;
  
  if (enabled) {
    logger.info('User has notification permissions');
  }
  
  return enabled;
}

// Get FCM token
async function getFCMToken(): Promise<string | null> {
  try {
    const token = await messaging().getToken();
    logger.debug('Got FCM token', { token: token.substring(0, 20) + '...' });
    return token;
  } catch (error) {
    logger.error('Failed to get FCM token', error);
    return null;
  }
}

// Handle foreground notifications
function onForegroundNotification(handler: NotificationHandler): () => void {
  return messaging().onMessage(async remoteMessage => {
    logger.debug('Received foreground notification', remoteMessage);
    handler({
      title: remoteMessage.notification?.title,
      body: remoteMessage.notification?.body,
      data: remoteMessage.data,
    });
  });
}

// Handle background notifications
function onBackgroundNotification(handler: NotificationHandler): void {
  messaging().setBackgroundMessageHandler(async remoteMessage => {
    logger.debug('Received background notification', remoteMessage);
    handler({
      title: remoteMessage.notification?.title,
      body: remoteMessage.notification?.body,
      data: remoteMessage.data,
    });
  });
}

// Handle notification tap (app opened from notification)
function onNotificationOpened(handler: NotificationHandler): () => void {
  // Check if app was opened from notification
  messaging()
    .getInitialNotification()
    .then(remoteMessage => {
      if (remoteMessage) {
        logger.debug('App opened from notification', remoteMessage);
        handler({
          title: remoteMessage.notification?.title,
          body: remoteMessage.notification?.body,
          data: remoteMessage.data,
        });
      }
    });

  // Listen for notification taps when app is in background
  return messaging().onNotificationOpenedApp(remoteMessage => {
    logger.debug('Notification tapped', remoteMessage);
    handler({
      title: remoteMessage.notification?.title,
      body: remoteMessage.notification?.body,
      data: remoteMessage.data,
    });
  });
}
```

### 6. Update AndroidManifest.xml

Add necessary permissions and services to `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <!-- Existing permissions -->
    
    <!-- Add FCM permissions -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    
    <application>
        <!-- Existing configuration -->
        
        <!-- Add FCM default notification channel -->
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_channel_id"
            android:value="@string/default_notification_channel_id" />
    </application>
</manifest>
```

### 7. Create Notification Channel (Android 8.0+)

Create or update `android/app/src/main/java/com/consultmobile/MainApplication.kt`:

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.content.Context

class MainApplication : Application(), ReactApplication {
    // ... existing code
    
    override fun onCreate() {
        super.onCreate()
        
        // Create notification channel for Android 8.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channelId = "consult_notifications"
            val channelName = "Consult Notifications"
            val channelDescription = "Notifications for consult requests and updates"
            val importance = NotificationManager.IMPORTANCE_HIGH
            
            val channel = NotificationChannel(channelId, channelName, importance).apply {
                description = channelDescription
            }
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
        
        // ... rest of existing onCreate code
    }
}
```

### 8. Update Backend Integration

Ensure the backend device registration endpoint (`/devices/register/` and `/devices/update-token/`) is working correctly. The FCM token will be sent to these endpoints automatically by the notification service.

## Testing

### Test on Physical Device

Push notifications require a physical device or an emulator with Google Play Services. They will not work on a standard Android emulator.

### Test Notifications

1. **Via Firebase Console:**
   - Go to Firebase Console → Cloud Messaging
   - Click "Send test message"
   - Enter FCM token from app logs
   - Send test notification

2. **Via Backend API:**
   - Ensure backend can send FCM notifications
   - Test consult assignment notifications
   - Verify notification payload structure matches expected format

## Troubleshooting

### Common Issues

1. **"google-services.json not found"**
   - Ensure file is at `mobile/android/app/google-services.json`
   - Clean and rebuild: `cd android && ./gradlew clean`

2. **"No Firebase App '[DEFAULT]' has been created"**
   - Ensure `google-services.json` is properly configured
   - Check that Google Services plugin is applied

3. **Notifications not received**
   - Verify device has Google Play Services
   - Check FCM token is being retrieved and registered
   - Verify backend is sending notifications correctly
   - Check notification permissions are granted

4. **Build errors after adding Firebase**
   - Clean build: `cd android && ./gradlew clean`
   - Clear Metro cache: `npm start -- --reset-cache`
   - Reinstall node_modules: `rm -rf node_modules && npm install`

## Notification Payload Structure

The backend should send notifications in this format:

```json
{
  "notification": {
    "title": "New Consult Request",
    "body": "Consult request from ER for patient John Doe"
  },
  "data": {
    "type": "consult_assigned",
    "consult_id": "123"
  }
}
```

The notification service will extract `consult_id` from the data payload to navigate to the consult detail screen when tapped.

## Security Considerations

1. **FCM Token Security:**
   - Tokens are stored securely using AsyncStorage
   - Tokens are sent to backend over HTTPS
   - Tokens are updated automatically when they change

2. **Backend Security:**
   - Verify backend validates FCM tokens
   - Ensure backend sends notifications only to authorized users
   - Implement rate limiting for notification sending

## Next Steps After Setup

1. Test notification flow end-to-end
2. Implement notification actions (e.g., quick actions in notification)
3. Add notification preferences in user settings
4. Implement notification grouping for multiple consults
5. Add sound and vibration customization

## References

- [React Native Firebase Documentation](https://rnfirebase.io/)
- [Firebase Cloud Messaging Documentation](https://firebase.google.com/docs/cloud-messaging)
- [React Native Firebase Messaging Module](https://rnfirebase.io/messaging/usage)

