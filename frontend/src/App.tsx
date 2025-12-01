import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Workers } from './pages/Workers'
import { Payouts } from './pages/Payouts'
import { Account } from './pages/Account'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="workers" element={<Workers />} />
          <Route path="payouts" element={<Payouts />} />
          <Route path="account" element={<Account />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
