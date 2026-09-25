import { useDispatch, useSelector } from 'react-redux';
import { setAnalysisResult, setAnalyzing, setError, setSaving, setUploadedFile, addAiMessage } from '../features/deviations/deviationSlice';
import { analyzeDeviation, apiError, askDeviationAssistant, saveDeviation, updateDeviation } from '../services/api';

export function useDeviation() {
  const dispatch = useDispatch(); const state = useSelector((s) => s.deviation);
  const analyze = async (text, file) => { dispatch(setError(null)); dispatch(setAnalyzing(true)); try { const { data } = await analyzeDeviation(text, file); dispatch(setAnalysisResult(data)); return data; } catch (e) { dispatch(setError(apiError(e, 'Unable to analyze the document. Please try again.'))); throw e; } finally { dispatch(setAnalyzing(false)); } };
  const save = async (id) => { dispatch(setError(null)); dispatch(setSaving(true)); try { const { data } = id ? await updateDeviation(id, state.formData) : await saveDeviation(state.formData); return data; } catch (e) { dispatch(setError(apiError(e, 'Unable to save the deviation. Please try again.'))); throw e; } finally { dispatch(setSaving(false)); } };
  const ask = async (question) => { try { const { data } = await askDeviationAssistant(question, state.formData); dispatch(addAiMessage({ role: 'user', text: question })); dispatch(addAiMessage({ role: 'assistant', text: data.answer })); } catch (e) { dispatch(setError(apiError(e, 'Unable to contact the AI assistant.'))); } };
  return { ...state, dispatch, analyze, save, ask, setUploadedFile: (file) => dispatch(setUploadedFile(file)) };
}
