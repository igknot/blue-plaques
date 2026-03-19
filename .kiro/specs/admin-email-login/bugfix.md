# Bugfix Requirements Document

## Introduction

The frontend login page (`LoginPage.tsx`) only provides Google OAuth authentication via Supabase Auth. However, admin users are stored in a separate `users` table with email/password credentials, and the backend already has a working `POST /api/v1/auth/login` endpoint that accepts email/password and returns a JWT token. This missing email/password login form prevents administrators from accessing admin-protected operations (create, update, delete plaques and images).

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN an admin user visits the login page THEN the system only displays a Google OAuth login button with no option for email/password authentication

1.2 WHEN an admin user wants to authenticate with email/password THEN the system provides no input fields or form to enter credentials

1.3 WHEN the frontend `authStore` handles authentication THEN the system only supports `loginWithGoogle()` method with no email/password login method

### Expected Behavior (Correct)

2.1 WHEN an admin user visits the login page THEN the system SHALL display an email/password login form in addition to the Google OAuth option

2.2 WHEN an admin user submits valid email/password credentials THEN the system SHALL call the backend `POST /api/v1/auth/login` endpoint and store the returned JWT token in localStorage

2.3 WHEN an admin user successfully authenticates with email/password THEN the system SHALL update the auth state to reflect the authenticated admin user and redirect to the home page

2.4 WHEN an admin user submits invalid credentials THEN the system SHALL display an appropriate error message without crashing

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a regular user clicks "Sign in with Google" THEN the system SHALL CONTINUE TO authenticate via Supabase OAuth as before

3.2 WHEN an authenticated user logs out THEN the system SHALL CONTINUE TO clear the auth state and any stored tokens

3.3 WHEN the page loads THEN the system SHALL CONTINUE TO check for existing sessions and restore authentication state

3.4 WHEN an authenticated user navigates to the login page THEN the system SHALL CONTINUE TO redirect them to the home page
