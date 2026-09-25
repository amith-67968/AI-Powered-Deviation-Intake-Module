import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import LogDeviationPage from './pages/LogDeviationPage';
import DeviationListPage from './pages/DeviationListPage';
import DeviationDetailPage from './pages/DeviationDetailPage';
import EditDeviationPage from './pages/EditDeviationPage';
export default function App() { return <Routes><Route element={<Layout/>}><Route path="/deviations/new" element={<LogDeviationPage/>}/><Route path="/deviations" element={<DeviationListPage/>}/><Route path="/deviations/:id" element={<DeviationDetailPage/>}/><Route path="/deviations/:id/edit" element={<EditDeviationPage/>}/><Route path="*" element={<Navigate to="/deviations/new" replace/>}/></Route></Routes> }
