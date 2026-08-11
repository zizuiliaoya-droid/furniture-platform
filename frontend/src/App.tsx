import { lazy, Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';

const MainLayout = lazy(() => import('./layouts/MainLayout'));
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const DashboardPage = lazy(() => import('./pages/dashboard/DashboardPage'));
const UserManagementPage = lazy(() => import('./pages/auth/UserManagementPage'));
const PermissionManagementPage = lazy(() => import('./pages/auth/PermissionManagementPage'));
const ProductListPage = lazy(() => import('./pages/products/ProductListPage'));
const ProductDetailPage = lazy(() => import('./pages/products/ProductDetailPage'));
const ProductFormPage = lazy(() => import('./pages/products/ProductFormPage'));
const CatalogPage = lazy(() => import('./pages/catalog/CatalogPage'));
const CaseListPage = lazy(() => import('./pages/cases/CaseListPage'));
const CaseDetailPage = lazy(() => import('./pages/cases/CaseDetailPage'));
const CaseFormPage = lazy(() => import('./pages/cases/CaseFormPage'));
const DocumentListPage = lazy(() => import('./pages/documents/DocumentListPage'));
const QuoteListPage = lazy(() => import('./pages/quotes/QuoteListPage'));
const QuoteDetailPage = lazy(() => import('./pages/quotes/QuoteDetailPage'));
const QuoteFormPage = lazy(() => import('./pages/quotes/QuoteFormPage'));
const ShareManagementPage = lazy(() => import('./pages/sharing/ShareManagementPage'));
const ShareViewPage = lazy(() => import('./pages/sharing/ShareViewPage'));

function RouteLoading() {
  return (
    <div role="status" aria-live="polite" style={{ padding: 32, textAlign: 'center' }}>
      正在加载…
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteLoading />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/s/:token" element={<ShareViewPage />} />
          <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/products" element={<ProductListPage />} />
            <Route path="/products/new" element={<ProductFormPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/products/:id/edit" element={<ProductFormPage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/cases" element={<CaseListPage />} />
            <Route path="/cases/new" element={<CaseFormPage />} />
            <Route path="/cases/:id" element={<CaseDetailPage />} />
            <Route path="/cases/:id/edit" element={<CaseFormPage />} />
            <Route path="/documents/:docType" element={<DocumentListPage />} />
            <Route path="/quotes" element={<QuoteListPage />} />
            <Route path="/quotes/new" element={<QuoteFormPage />} />
            <Route path="/quotes/:id" element={<QuoteDetailPage />} />
            <Route path="/quotes/:id/edit" element={<QuoteFormPage />} />
            <Route path="/users" element={<UserManagementPage />} />
            <Route path="/permissions" element={<PermissionManagementPage />} />
            <Route path="/shares" element={<ShareManagementPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
