import Field from './Field';
import { IMPACTS, SEVERITIES, SITES, SOURCES } from '../utils/constants';
import { useDeviation } from '../hooks/useDeviation';
import { resetForm, setField } from '../features/deviations/deviationSlice';

const Select = ({ value, onChange, options, placeholder = 'Select…' }) => <select value={value || ''} onChange={onChange}><option value="">{placeholder}</option>{options.map((o) => <option key={o}>{o}</option>)}</select>;
export default function DeviationForm({ onSave, saveLabel = 'Save Deviation' }) {
  const { formData, fieldSources, isSaving, dispatch } = useDeviation();
  const change = (field) => (e) => dispatch(setField({ field, value: e.target.value }));
  const valid = formData.site && formData.date_of_occurrence && formData.title.trim() && formData.detailed_description.trim().length >= 10;
  return <section className="card deviation-form"><div className="card-heading"><div><p className="eyebrow">Deviation intake</p><h1>Log Deviation</h1><p>Record an unexpected event, out-of-specification result, or non-conformance.</p></div></div>
    <div className="section-heading">Deviation Information</div><div className="form-grid">
      <Field label="Site / Plant" required source={fieldSources.site}><Select value={formData.site} onChange={change('site')} options={SITES} /></Field>
      <Field label="Date of Occurrence" required source={fieldSources.date_of_occurrence}><input type="date" value={formData.date_of_occurrence || ''} onChange={change('date_of_occurrence')} /></Field>
      <Field label="Title / Short Description" required source={fieldSources.title}><input value={formData.title || ''} onChange={change('title')} placeholder="Briefly describe the event" /></Field>
      <Field label="Source" source={fieldSources.source}><Select value={formData.source} onChange={change('source')} options={SOURCES} /></Field>
      <Field label="Related Product / Material" source={fieldSources.product_material}><input value={formData.product_material || ''} onChange={change('product_material')} placeholder="Product or material" /></Field>
      <Field label="Batch/Lot Number" source={fieldSources.batch_lot_number}><input value={formData.batch_lot_number || ''} onChange={change('batch_lot_number')} placeholder="e.g. API-260924-B17" /></Field>
    </div><div className="section-heading">Deviation Details</div><div className="form-grid">
      <Field label="Detailed Description" required source={fieldSources.detailed_description}><textarea rows="6" value={formData.detailed_description || ''} onChange={change('detailed_description')} placeholder="Describe what occurred, observations and immediate actions." /></Field>
      <Field label="Initial Impact" source={fieldSources.initial_impact}><Select value={formData.initial_impact} onChange={change('initial_impact')} options={IMPACTS} /></Field>
      <Field label="Initial Severity" source={fieldSources.initial_severity}><Select value={formData.initial_severity} onChange={change('initial_severity')} options={SEVERITIES} /></Field>
    </div><div className="form-actions"><button className="button secondary" onClick={() => dispatch(resetForm())} type="button">Reset Form</button><button className="button primary" disabled={!valid || isSaving} onClick={onSave} type="button">{isSaving ? 'Saving…' : saveLabel}</button></div>
  </section>;
}
