import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResidentDashboard from "./pages/ResidentDashboard";
import RaiseComplaint from "./pages/RaiseComplaint";
import ProtectedRoute from "./components/ProtectedRoute";

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
    </Routes>
  );
}

export default App;