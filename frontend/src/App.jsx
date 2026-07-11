import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResidentDashboard from "./pages/ResidentDashboard";
import RaiseComplaint from "./pages/RaiseComplaint";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminDashboard from "./pages/AdminDashboard";
import NoticeBoard from "./pages/NoticeBoard";
import DashboardStats from "./pages/DashboardStats";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <ResidentDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/raise-complaint"
        element={
          <ProtectedRoute>
            <RaiseComplaint />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/notices"
        element={
          <ProtectedRoute>
            <NoticeBoard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard-stats"
        element={
          <ProtectedRoute requireAdmin>
            <DashboardStats />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;