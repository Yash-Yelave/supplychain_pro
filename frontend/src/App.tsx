import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Results from './pages/Results';
import SupplierProfile from './pages/SupplierProfile';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results/:requestId" element={<Results />} />
        <Route path="/supplier/:id" element={<SupplierProfile />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
