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
├── MOBILE_DEV.md             # This file
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

### Push Notifications (Planned)

- FCM integration for Android
- Navigate to consult detail from notification tap
- Foreground and background notification handling

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

## Environment Configuration

Edit `src/config/env.ts` to configure API URLs:

```typescript
export const ENV = {
  API_BASE_URL: __DEV__
    ? 'https://dev-consult.pmc.edu.pk/api/v1'
    : 'https://consult.pmc.edu.pk/api/v1',
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

### Debugging

Use React Native Debugger or Flipper for debugging. Console logs are enabled in development mode.

## Contributing

1. Follow the existing code structure
2. Ensure TypeScript strict mode passes
3. Test on Android emulator/device before committing
4. Update this documentation for significant changes
