import { createSlice } from '@reduxjs/toolkit';

export const emptyForm = {
  site: '', date_of_occurrence: '', title: '', source: '', product_material: '', batch_lot_number: '',
  detailed_description: '', initial_impact: '', initial_severity: '', ai_recommended_impact: '',
  ai_recommended_severity: '', ai_severity_reason: '', ai_confidence: null, ai_extracted_data: null, status: 'Draft'
};
const initialState = { formData: emptyForm, fieldSources: {}, analysisResult: null, isAnalyzing: false, isSaving: false, error: null, uploadedFile: null, aiMessages: [], missingInformation: [], confidence: null };

const slice = createSlice({
  name: 'deviation', initialState,
  reducers: {
    setField(state, action) { const { field, value } = action.payload; state.formData[field] = value; state.fieldSources[field] = 'edited'; },
    setFormData(state, action) { state.formData = { ...emptyForm, ...action.payload }; state.fieldSources = {}; },
    setAnalysisResult(state, action) {
      const { extraction, recommendation } = action.payload;
      state.analysisResult = action.payload; state.confidence = extraction.confidence; state.missingInformation = extraction.missing_information || [];
      Object.entries(extraction).forEach(([field, value]) => { if (field !== 'confidence' && field !== 'missing_information' && value !== null && value !== '') { state.formData[field] = value; state.fieldSources[field] = 'ai'; } });
      state.formData.ai_recommended_impact = recommendation.impact || ''; state.formData.ai_recommended_severity = recommendation.severity || '';
      state.formData.ai_severity_reason = recommendation.reason || ''; state.formData.ai_confidence = extraction.confidence;
      state.formData.ai_extracted_data = extraction; state.fieldSources.initial_impact = 'ai'; state.fieldSources.initial_severity = 'ai';
    },
    setUploadedFile(state, action) { state.uploadedFile = action.payload; },
    resetForm() { return initialState; },
    setAnalyzing(state, action) { state.isAnalyzing = action.payload; }, setSaving(state, action) { state.isSaving = action.payload; },
    setError(state, action) { state.error = action.payload; }, clearError(state) { state.error = null; },
    addAiMessage(state, action) { state.aiMessages.push(action.payload); }
  }
});
export const { setField, setFormData, setAnalysisResult, setUploadedFile, resetForm, setAnalyzing, setSaving, setError, clearError, addAiMessage } = slice.actions;
export default slice.reducer;
