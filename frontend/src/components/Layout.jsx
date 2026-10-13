import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { ToastProvider } from './Toast';
import ErrorBoundary from './ErrorBoundary';

export default function Layout() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <div className="layout-container">
          <Sidebar />
          <main className="main-content">
            <Outlet />
          </main>
        </div>
      </ToastProvider>
    </ErrorBoundary>
  );
}
