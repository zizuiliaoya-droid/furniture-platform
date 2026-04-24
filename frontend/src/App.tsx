import { BrowserRouter, Route, Routes } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import UserManagementPage from './pages/auth/UserManagementPage';
import ProductListPage from './pages/products/ProductListPage';
import ProductDetailPage from './pages/products/ProductDetailPage';
import ProductFormPage from './pages/products/ProductFormPage';
import CategoryManagementPage from './pages/products/CategoryManagementPage';
import CatalogPage from './pages/catalog/CatalogPage';
import CaseListPage from './pages/cases/CaseListPage';
import CaseDetailPage from './pages/cases/CaseDetailPage';
import CaseFormPage from './pages/cases/CaseFormPage';
import DocumentListPage from './pages/documents/DocumentListPage';
import QuoteListPage from './pages/quotes/QuoteListPage';
import QuoteDetailPage from './pages/quotes/QuoteDetailPage';
import QuoteFormPage from './pages/quotes/QuoteFormPage';
import ShareManagementPage from './pages/sharing/ShareManagementPage';
import ShareViewPage from './pages/sharing/ShareViewPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/s/:token" element={<ShareViewPage />} />
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/new" element={<ProductFormPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/products/:id/edit" element={<ProductFormPage />} />
          <Route path="/categories" element={<CategoryManagementPage />} />
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
          <Route path="/shares" element={<ShareManagementPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
