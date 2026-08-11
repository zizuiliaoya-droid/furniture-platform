import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import ProtectedRoute from '../ProtectedRoute';
import { useAuthStore } from '../../store/authStore';


function renderProtectedRoute() {
  return render(
    <MemoryRouter initialEntries={['/private']}>
      <Routes>
        <Route path="/login" element={<div>登录页面</div>} />
        <Route
          path="/private"
          element={<ProtectedRoute><div>内部内容</div></ProtectedRoute>}
        />
      </Routes>
    </MemoryRouter>,
  );
}


describe('ProtectedRoute', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null, isAuthenticated: false });
  });

  it('redirects an anonymous visitor to login', () => {
    renderProtectedRoute();

    expect(screen.getByText('登录页面')).toBeInTheDocument();
    expect(screen.queryByText('内部内容')).not.toBeInTheDocument();
  });

  it('renders protected content for an authenticated user', () => {
    useAuthStore.setState({ token: 'test-token', isAuthenticated: true });

    renderProtectedRoute();

    expect(screen.getByText('内部内容')).toBeInTheDocument();
  });
});
