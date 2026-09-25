import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import DeviationForm from '../components/DeviationForm';
import { getDeviation } from '../services/api';
import { useDeviation } from '../hooks/useDeviation';
import { setFormData } from '../features/deviations/deviationSlice';
export default function EditDeviationPage() { const { id } = useParams(); const navigate = useNavigate(); const { dispatch, save } = useDeviation(); const [ready, setReady] = useState(false); useEffect(() => { getDeviation(id).then(({ data }) => { dispatch(setFormData(data)); setReady(true); }); }, [id, dispatch]); if (!ready) return <div className="loading-page">Loading record…</div>; return <div className="edit-wrap"><DeviationForm saveLabel="Update Deviation" onSave={async () => { try { await save(id); navigate(`/deviations/${id}`); } catch {} }}/></div> }
