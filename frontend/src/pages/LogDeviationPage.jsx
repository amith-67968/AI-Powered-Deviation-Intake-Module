import { useNavigate } from 'react-router-dom';
import AiAssistant from '../components/AiAssistant';
import DeviationForm from '../components/DeviationForm';
import { useDeviation } from '../hooks/useDeviation';
export default function LogDeviationPage() { const navigate = useNavigate(); const { save } = useDeviation(); const handleSave = async () => { try { const saved = await save(); navigate(`/deviations/${saved.id}`, { state: { saved: true } }); } catch { /* Error is displayed in assistant. */ } }; return <><div className="breadcrumb">QMS <span>/</span> Deviations <span>/</span> New intake</div><div className="workspace"><DeviationForm onSave={handleSave}/><AiAssistant /></div></>; }
