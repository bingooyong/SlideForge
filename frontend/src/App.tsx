import { NavLink, Route, Routes } from "react-router-dom";
import { UploadPage } from "./features/upload/UploadPage";
import { SettingsPage } from "./features/settings/SettingsPage";

function App() {
  return (
    <div className="app-root">
      <header>
        <h1>SlideForge</h1>
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            首页
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => (isActive ? "active" : "")}>
            配置
          </NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

