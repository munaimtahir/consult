# Mobile App Development Guide

## Overview

This is the React Native + TypeScript mobile app for the Hospital Consult System. It provides a native Android experience for Residents, Consultants, and Heads of Department (HODs) to manage consults.

## Tech Stack

- **React Native** 0.74.0 - Cross-platform mobile framework
- **TypeScript** 5.4+ - Type-safe JavaScript
- **React Navigation** 6.x - Navigation library (Stack + Bottom Tabs)
- **Axios** 1.7+ - HTTP client for API calls
- **AsyncStorage** - Persistent local storage

## Project Structure

```
mobile/
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── app.json                  # App name and display settings
├── index.js                  # Entry point
├── babel.config.js           # Babel configuration
├── metro.config.js           # Metro bundler configuration
├── build-debug.sh            # Debug APK build script
├── build-release.sh          # Release APK/AAB build script
├── MOBILE_DEV.md             # This file
├── android/                  # Android native project
│   ├── app/
│   │   ├── build.gradle      # App-level Gradle config
│   │   ├── consult-release-key.keystore  # Release signing key
│   │   └── src/main/         # Android source and resources
│   ├── build.gradle          # Project-level Gradle config
│   ├── gradle.properties     # Gradle settings and signing config
│   └── gradlew               # Gradle wrapper
├── .vscode/
│   └── tasks.json            # VS Code build tasks
└── src/
    ├── App.tsx               # Root component with providers
    ├── api/                  # API layer
    │   ├── client.ts         # Axios client with interceptors
    │   ├── auth.ts           # Authentication endpoints
    │   ├── consults.ts       # Consult CRUD operations
    │   ├── dashboard.ts      # HOD dashboard data
    │   ├── devices.ts        # FCM device registration
    │   └── types.ts          # TypeScript interfaces
    ├── components/           # Reusable UI components
    │   ├── ConsultCard.tsx   # Consult list item card
    │   ├── StatusBadge.tsx   # Status/urgency badges
    │   ├── SummaryCard.tsx   # Dashboard summary cards
    │   ├── Loading.tsx       # Loading indicator
    │   ├── ErrorState.tsx    # Error display with retry
    │   └── EmptyState.tsx    # Empty list state
    ├── config/               # App configuration
    │   ├── env.ts            # Environment variables
    │   ├── constants.ts      # App-wide constants
    │   └── permissions.ts    # Permission helper functions
    ├── hooks/                # Custom React hooks
    │   ├── useAuth.ts        # Auth context and actions
    │   ├── useConsults.ts    # Consult data management
    │   ├── useDashboard.ts   # Dashboard data
    │   └── useNotifications.ts # Push notification handling
    ├── navigation/           # Navigation configuration
    │   ├── RootNavigator.tsx # Main navigator (Auth/Main split)
    │   ├── AuthStack.tsx     # Login screens
    │   ├── MainTabs.tsx      # Bottom tab navigation
    │   └── types.ts          # Navigation type definitions
    ├── screens/              # Screen components
    │   ├── Auth/
    │   │   └── LoginScreen.tsx
    │   ├── Consults/
    │   │   ├── MyConsultsScreen.tsx
    │   │   ├── DepartmentConsultsScreen.tsx
    │   │   ├── ConsultDetailScreen.tsx
    │   │   └── AddNoteScreen.tsx
    │   ├── Dashboard/
    │   │   └── HODDashboardScreen.tsx
    │   └── Settings/
    │       └── ProfileScreen.tsx
    ├── services/             # Business logic services
    │   ├── storage.ts        # AsyncStorage wrapper
    │   ├── notifications.ts  # FCM integration
    │   └── logger.ts         # Logging utility
    ├── theme/                # Design system
    │   ├── colors.ts         # Color palette
    │   ├── spacing.ts        # Spacing and layout
    │   └── typography.ts     # Font styles
    └── utils/                # Utility functions
        ├── date.ts           # Date formatting
        ├── format.ts         # Text formatting
        └── helpers.ts        # General helpers
```

## Getting Started

### Prerequisites

- Node.js 18+
- Java JDK 17
- Android Studio with Android SDK
- React Native CLI (`npm install -g react-native-cli`)

### Installation

```bash
cd mobile
npm install
```

### Running on Android

```bash
# Start Metro bundler
npm start

# In another terminal, run on connected device/emulator
npm run android
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Building APKs

### Debug Build

Build a debug APK for testing:

```bash
npm run build:debug
```

Output: `android/app/build/outputs/apk/debug/app-debug.apk`

### Release Build

Build a signed release APK and Android App Bundle:

```bash
npm run build:release
```

Output:
- APK: `android/app/build/outputs/apk/release/app-release.apk`
- AAB: `android/app/build/outputs/bundle/release/app-release.aab`

### VS Code One-Click Build

1. Open Command Palette (Ctrl+Shift+P)
2. Select "Tasks: Run Task"
3. Choose "Build Debug APK" or "Build Release APK"

### Production Keystore Setup

For production releases, generate a new keystore:

```bash
keytool -genkeypair -v -keystore production-key.keystore \
  -alias productionKey -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass YOUR_SECURE_PASSWORD -keypass YOUR_SECURE_PASSWORD
```

Update `android/gradle.properties`:
```properties
CONSULT_UPLOAD_STORE_FILE=production-key.keystore
CONSULT_UPLOAD_KEY_ALIAS=productionKey
CONSULT_UPLOAD_STORE_PASSWORD=YOUR_SECURE_PASSWORD
CONSULT_UPLOAD_KEY_PASSWORD=YOUR_SECURE_PASSWORD
```

**⚠️ SECURITY**: Never commit production passwords to version control. Use environment variables or a secure vault for CI/CD.

## Features

### Authentication

- JWT token-based authentication
- Automatic token refresh handling
- Secure token storage using AsyncStorage
- Auto-login on app restart

### Consult Management

- View assigned consults with filters (All, Pending, Acknowledged, In Progress, Completed)
- View department consults (for authorized users)
- Consult detail view with full patient and clinical information
- Acknowledge consults
- Complete consults
- Add progress notes

### HOD Dashboard

- Today's overview with summary cards
- List of delayed/overdue consults
- Activity summary by user
- Quick navigation to consult details

### User Profile

- View user information
- Permission summary display
- Logout functionality

### Push Notifications (Scaffolded)

The notification infrastructure is in place with mock implementations:
- FCM token management ready
- Device registration API integrated
- Navigation from notification tap configured

To enable real push notifications:
1. Set up a Firebase project
2. Add `google-services.json` to `android/app/`
3. Install Firebase packages:
   ```bash
   npm install @react-native-firebase/app @react-native-firebase/messaging
   ```
4. Update `services/notifications.ts` to use real Firebase calls

## API Integration

The app connects to the Django backend at:

- **Development**: `https://dev-consult.pmc.edu.pk/api/v1`
- **Production**: `https://consult.pmc.edu.pk/api/v1`

### Key Endpoints

- `POST /auth/token/` - Login (JWT)
- `GET /auth/users/me/` - Current user profile
- `GET /consults/requests/` - List consults (with filters)
- `GET /consults/requests/:id/` - Consult detail
- `POST /consults/requests/:id/acknowledge/` - Acknowledge consult
- `POST /consults/requests/:id/complete/` - Complete consult
- `POST /consults/requests/:id/add_note/` - Add note
- `GET /admin/dashboard/department/` - Department dashboard
- `POST /devices/register/` - Register device for push notifications
- `PATCH /devices/update-token/` - Update FCM token

## Environment Configuration

Edit `src/config/env.ts` to configure API URLs:

```typescript
export const ENV = {
  API_BASE_URL: __DEV__
    ? 'https://dev-consult.pmc.edu.pk/api/v1'  // Your dev server
    : 'https://consult.pmc.edu.pk/api/v1',     // Your prod server
  // ... other config
};
```

## Permissions

The app respects backend permission flags:

- `can_view_department_dashboard` - Access to Department Consults tab
- `can_view_global_dashboard` - Access to global statistics
- `is_hod` - Head of Department privileges
- `can_assign_consults` - Ability to assign consults

## Styling

The app uses a consistent design system:

- **Colors**: Primary blue (`#2563EB`), status colors for urgency/status
- **Spacing**: 8-point grid system
- **Typography**: System fonts with defined text styles

## Future Enhancements

- [ ] iOS support
- [ ] Firebase Cloud Messaging integration
- [ ] Offline mode with data caching
- [ ] Biometric authentication
- [ ] Dark mode support
- [ ] Accessibility improvements

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `npm start -- --reset-cache`
2. **Android build fails**: Run `cd android && ./gradlew clean`
3. **Type errors**: Run `npm run type-check` to identify issues
4. **Gradle sync fails**: Ensure JAVA_HOME points to JDK 17
5. **Network errors**: Check that API_BASE_URL in env.ts is correct

### Debugging

Use React Native Debugger or Flipper for debugging. Console logs are enabled in development mode.

## Contributing

1. Follow the existing code structure
2. Ensure TypeScript strict mode passes
3. Test on Android emulator/device before committing
4. Update this documentation for significant changes
