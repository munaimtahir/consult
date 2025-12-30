import { test, expect } from '@playwright/test';

// Mock user profiles for different roles
const mockUsers = {
  superAdmin: {
    email: 'superadmin@pmc.edu.pk',
    first_name: 'Super',
    last_name: 'Admin',
    role: 'ADMIN',
    is_superuser: true,
    is_admin_user: true,
    permissions: {
      can_manage_users: true,
      can_manage_departments: true,
      can_view_department_dashboard: true,
      can_view_global_dashboard: true,
      can_manage_consults_globally: true,
      can_manage_permissions: true,
    },
  },
  hod: {
    email: 'hod@pmc.edu.pk',
    first_name: 'Head',
    last_name: 'Department',
    role: 'HOD',
    is_superuser: false,
    is_admin_user: false,
    permissions: {
      can_manage_users: false,
      can_manage_departments: false,
      can_view_department_dashboard: true,
      can_view_global_dashboard: false,
      can_manage_consults_globally: false,
      can_manage_permissions: false,
    },
  },
  qa: {
    email: 'qa@pmc.edu.pk',
    first_name: 'Quality',
    last_name: 'Assurance',
    role: 'DEPARTMENT_USER',
    is_superuser: false,
    is_admin_user: false,
    permissions: {
      can_manage_users: false,
      can_manage_departments: false,
      can_view_department_dashboard: true,
      can_view_global_dashboard: true,
      can_manage_consults_globally: false,
      can_manage_permissions: false,
    },
  },
  doctor: {
    email: 'doctor@pmc.edu.pk',
    first_name: 'Doctor',
    last_name: 'User',
    role: 'DOCTOR',
    is_superuser: false,
    is_admin_user: false,
    permissions: {
      can_manage_users: false,
      can_manage_departments: false,
      can_view_department_dashboard: false,
      can_view_global_dashboard: false,
      can_manage_consults_globally: false,
      can_manage_permissions: false,
    },
  },
};

// Helper function to setup route mocks for a specific user
function setupUserRoutes(page, user) {
  page.route('**/auth/users/me/**', async (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(user),
    });
  });

  // Mock admin API endpoints
  page.route('**/admin/users/**', async (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [] }),
      });
    }
    return route.continue();
  });

  page.route('**/admin/departments/**', async (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [] }),
      });
    }
    return route.continue();
  });

  page.route('**/admin/dashboards/**', async (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ global_kpis: {}, consults: [], department_stats: [] }),
    });
  });

  page.route('**/admin/analytics/doctors/**', async (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });
}

test.describe('Admin Panel RBAC', () => {
  test.describe('SuperAdmin Access', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/auth/token/**', async (route) => {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
        });
      });

      setupUserRoutes(page, mockUsers.superAdmin);

      // Login
      await page.goto('/login');
      await page.fill('input#email', mockUsers.superAdmin.email);
      await page.fill('input#password', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');
    });

    test('should access admin panel home', async ({ page }) => {
      await page.goto('/adminpanel');
      await expect(page.locator('h1')).toContainText('Admin Panel');
    });

    test('should see all admin sections', async ({ page }) => {
      await page.goto('/adminpanel');
      await expect(page.locator('text=Users Management')).toBeVisible();
      await expect(page.locator('text=Departments Management')).toBeVisible();
      await expect(page.locator('text=Department Dashboard')).toBeVisible();
      await expect(page.locator('text=Global Dashboard')).toBeVisible();
      await expect(page.locator('text=Doctor Analytics')).toBeVisible();
    });

    test('should access users management page', async ({ page }) => {
      await page.goto('/adminpanel/users');
      await expect(page.locator('h1')).toContainText('Users Management');
      // Should not see blank page
      await expect(page.locator('body')).not.toHaveText('');
    });

    test('should access departments management page', async ({ page }) => {
      await page.goto('/adminpanel/departments');
      await expect(page.locator('h1')).toContainText('Departments Management');
      await expect(page.locator('body')).not.toHaveText('');
    });

    test('should access global dashboard', async ({ page }) => {
      await page.goto('/adminpanel/dashboards/global');
      await expect(page.locator('h1')).toContainText('Global Dashboard');
      await expect(page.locator('body')).not.toHaveText('');
    });

    test('should access doctor analytics', async ({ page }) => {
      await page.goto('/adminpanel/analytics/doctors');
      await expect(page.locator('h1')).toContainText('Doctor Analytics');
      await expect(page.locator('body')).not.toHaveText('');
    });
  });

  test.describe('HOD Access', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/auth/token/**', async (route) => {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
        });
      });

      setupUserRoutes(page, mockUsers.hod);

      await page.goto('/login');
      await page.fill('input#email', mockUsers.hod.email);
      await page.fill('input#password', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');
    });

    test('should access admin panel home', async ({ page }) => {
      await page.goto('/adminpanel');
      await expect(page.locator('h1')).toContainText('Admin Panel');
    });

    test('should only see department dashboard section', async ({ page }) => {
      await page.goto('/adminpanel');
      await expect(page.locator('text=Department Dashboard')).toBeVisible();
      // Should not see management sections
      await expect(page.locator('text=Users Management')).not.toBeVisible();
      await expect(page.locator('text=Departments Management')).not.toBeVisible();
    });

    test('should access department dashboard', async ({ page }) => {
      await page.goto('/adminpanel/dashboards/department');
      await expect(page.locator('h1')).toContainText('Department Dashboard');
      await expect(page.locator('body')).not.toHaveText('');
    });

    test('should be redirected from users management', async ({ page }) => {
      await page.goto('/adminpanel/users');
      // Should redirect to dashboard or show access denied
      const url = page.url();
      expect(url).not.toContain('/adminpanel/users');
    });

    test('should be redirected from global dashboard', async ({ page }) => {
      await page.goto('/adminpanel/dashboards/global');
      const url = page.url();
      expect(url).not.toContain('/adminpanel/dashboards/global');
    });
  });

  test.describe('QA Access', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/auth/token/**', async (route) => {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
        });
      });

      setupUserRoutes(page, mockUsers.qa);

      await page.goto('/login');
      await page.fill('input#email', mockUsers.qa.email);
      await page.fill('input#password', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');
    });

    test('should see dashboard sections only', async ({ page }) => {
      await page.goto('/adminpanel');
      await expect(page.locator('text=Department Dashboard')).toBeVisible();
      await expect(page.locator('text=Global Dashboard')).toBeVisible();
      await expect(page.locator('text=Users Management')).not.toBeVisible();
      await expect(page.locator('text=Departments Management')).not.toBeVisible();
    });

    test('should access both dashboards', async ({ page }) => {
      await page.goto('/adminpanel/dashboards/department');
      await expect(page.locator('body')).not.toHaveText('');

      await page.goto('/adminpanel/dashboards/global');
      await expect(page.locator('body')).not.toHaveText('');
    });
  });

  test.describe('Doctor (No Admin Access)', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/auth/token/**', async (route) => {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
        });
      });

      setupUserRoutes(page, mockUsers.doctor);

      await page.goto('/login');
      await page.fill('input#email', mockUsers.doctor.email);
      await page.fill('input#password', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');
    });

    test('should be redirected from admin panel', async ({ page }) => {
      await page.goto('/adminpanel');
      const url = page.url();
      expect(url).not.toContain('/adminpanel');
    });

    test('should be redirected from any admin route', async ({ page }) => {
      await page.goto('/adminpanel/users');
      const url = page.url();
      expect(url).not.toContain('/adminpanel');

      await page.goto('/adminpanel/dashboards/global');
      const url2 = page.url();
      expect(url2).not.toContain('/adminpanel');
    });
  });

  test.describe('Error Handling', () => {
    test('should show error message instead of blank page on API failure', async ({ page }) => {
      await page.route('**/auth/token/**', async (route) => {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
        });
      });

      setupUserRoutes(page, mockUsers.superAdmin);

      // Make admin API fail
      await page.route('**/admin/users/**', async (route) => {
        return route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      });

      await page.goto('/login');
      await page.fill('input#email', mockUsers.superAdmin.email);
      await page.fill('input#password', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard');

      await page.goto('/adminpanel/users');
      // Should show error or loading state, not blank page
      const bodyText = await page.locator('body').textContent();
      expect(bodyText).not.toBe('');
      expect(bodyText).not.toBeNull();
    });
  });
});

