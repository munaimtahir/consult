import { test, expect } from '@playwright/test';

const mockUser = {
  email: 'admin@pmc.edu.pk',
  first_name: 'Admin',
  last_name: 'User',
  role: 'Administrator',
  permissions: {
    can_view_global_dashboard: true,
  },
};

const mockDashboardStats = {
  my_department: { pending: 1, in_progress: 2, overdue: 0 },
  assigned_to_me: { pending: 0, in_progress: 1, overdue: 0 },
  my_requests: { pending: 0, in_progress: 0, completed: 3 },
};

test.beforeEach(async ({ page }) => {
  await page.route('**/auth/token/**', async (route, request) => {
    if (request.method() === 'POST') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access: 'fake-access', refresh: 'fake-refresh' }),
      });
    }
    return route.continue();
  });

  await page.route('**/auth/users/me/**', async (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockUser),
    });
  });

  await page.route('**/consults/requests/dashboard_stats/**', async (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockDashboardStats),
    });
  });
});

test.describe('Authentication', () => {
  test('should redirect to login page for protected route', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });

  test('should login successfully and redirect to dashboard', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input#email', 'admin@pmc.edu.pk');
    await page.fill('input#password', 'password');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toHaveText('Dashboard');
  });
});
