/**
 * CertiNexus AI — ML Research Dashboard
 *
 * Displays actual experiment results, model comparison, confusion matrix,
 * dataset statistics, and error analysis. All data loaded from ML pipeline artifacts.
 */

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Brain, Database, FlaskConical, BarChart3, AlertTriangle, CheckCircle2 } from 'lucide-react'
import api from '../lib/api.js'

export default function MLResearch() {
  const { data: datasetStats } = useQuery({ queryKey: ['dataset-stats'], queryFn: () => api.getDatasetStats() })
  const { data: modelPerf } = useQuery({ queryKey: ['model-perf'], queryFn: () => api.getModelPerformance() })
  const { data: experiments } = useQuery({ queryKey: ['experiments'], queryFn: () => api.getExperiments() })
  const { data: modelComparison } = useQuery({ queryKey: ['model-comparison'], queryFn: () => api.getModelComparison() })
  const { data: confusionMatrix } = useQuery({ queryKey: ['confusion-matrix'], queryFn: () => api.getConfusionMatrix() })
  const { data: errorAnalysis } = useQuery({ queryKey: ['error-analysis'], queryFn: () => api.getErrorAnalysis() })

  return (
    <div>
      <div className="page-header">
        <h1>ML Research Dashboard</h1>
        <p>Experiment results, model performance, and dataset analysis — all from actual ML pipeline runs</p>
      </div>

      {/* Dataset Statistics */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: '28px', marginBottom: '20px' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={18} style={{ color: 'var(--color-accent)' }} /> Dataset Statistics
        </h3>
        {datasetStats ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '16px' }}>
            <div className="stat-card" style={{ padding: '16px' }}>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>{datasetStats.total_samples}</div>
              <div className="stat-label">Total Samples</div>
            </div>
            <div className="stat-card" style={{ padding: '16px' }}>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>{datasetStats.total_categories}</div>
              <div className="stat-label">Categories</div>
            </div>
            <div className="stat-card" style={{ padding: '16px' }}>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>{datasetStats.vocabulary?.unique_tokens || '—'}</div>
              <div className="stat-label">Vocabulary Size</div>
            </div>
            <div className="stat-card" style={{ padding: '16px' }}>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>{datasetStats.text_statistics?.word_count?.mean || '—'}</div>
              <div className="stat-label">Avg Words/Doc</div>
            </div>
          </div>
        ) : <div className="skeleton" style={{ height: '80px' }} />}
        {datasetStats?.class_distribution && (
          <div style={{ marginTop: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>Class Distribution</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {Object.entries(datasetStats.class_distribution).map(([cat, count]) => (
                <span key={cat} style={{
                  padding: '4px 10px', borderRadius: 'var(--radius-full)', background: 'var(--glass-bg)',
                  border: '1px solid var(--glass-border)', fontSize: '0.75rem',
                }}>{cat}: <strong>{count}</strong></span>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Model Performance */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="glass-card" style={{ padding: '28px', marginBottom: '20px' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Brain size={18} style={{ color: 'var(--color-primary)' }} /> Production Model Performance
        </h3>
        {modelPerf ? (
          <>
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
              <span style={{ padding: '4px 12px', borderRadius: 'var(--radius-full)', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.2)', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-primary-light)' }}>
                {modelPerf.model_name}
              </span>
              <span style={{ padding: '4px 12px', borderRadius: 'var(--radius-full)', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>
                v{modelPerf.version}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '12px' }}>
              {Object.entries(modelPerf.metrics || {}).map(([key, value]) => (
                <div key={key} className="stat-card" style={{ padding: '14px' }}>
                  <div className="stat-value" style={{ fontSize: '1.3rem' }}>{(value * 100).toFixed(1)}%</div>
                  <div className="stat-label" style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}</div>
                </div>
              ))}
            </div>
          </>
        ) : <div className="skeleton" style={{ height: '100px' }} />}
      </motion.div>

      {/* Model Comparison */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
        className="glass-card" style={{ padding: '28px', marginBottom: '20px' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FlaskConical size={18} style={{ color: 'var(--color-secondary)' }} /> Model Comparison
        </h3>
        {modelComparison?.models ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <th style={{ textAlign: 'left', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>Model</th>
                  <th style={{ textAlign: 'left', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>Features</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>Accuracy</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>Macro F1</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>CV Score</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>Train Time</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelComparison.models).map(([key, m]) => (
                  <tr key={key} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 500 }}>{m.model}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{m.feature_set}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>{(m.val_accuracy * 100).toFixed(1)}%</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-success)' }}>{(m.val_macro_f1 * 100).toFixed(1)}%</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>{(m.cv_score * 100).toFixed(1)}%</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>{m.train_time.toFixed(2)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="skeleton" style={{ height: '200px' }} />}
      </motion.div>

      {/* Confusion Matrix */}
      {confusionMatrix && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="glass-card" style={{ padding: '28px', marginBottom: '20px' }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={18} style={{ color: 'var(--color-accent)' }} /> Confusion Matrix
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'collapse', fontSize: '0.7rem', fontFamily: 'var(--font-mono)' }}>
              <thead>
                <tr>
                  <th style={{ padding: '6px 8px' }}></th>
                  {confusionMatrix.labels?.map((l, i) => (
                    <th key={i} style={{ padding: '6px 4px', color: 'var(--text-tertiary)', writingMode: 'vertical-rl', textOrientation: 'mixed', maxWidth: '30px', fontWeight: 500 }}>
                      {l.length > 12 ? l.slice(0, 10) + '..' : l}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {confusionMatrix.matrix?.map((row, i) => (
                  <tr key={i}>
                    <td style={{ padding: '6px 8px', fontWeight: 500, color: 'var(--text-secondary)', whiteSpace: 'nowrap', fontSize: '0.65rem' }}>
                      {confusionMatrix.labels[i]?.length > 15 ? confusionMatrix.labels[i].slice(0, 13) + '..' : confusionMatrix.labels[i]}
                    </td>
                    {row.map((val, j) => {
                      const maxVal = Math.max(...row)
                      const opacity = maxVal > 0 ? val / maxVal : 0
                      const isDiag = i === j
                      return (
                        <td key={j} style={{
                          padding: '6px 8px', textAlign: 'center',
                          background: isDiag ? `rgba(16,185,129,${opacity * 0.4})` : val > 0 ? `rgba(239,68,68,${opacity * 0.3})` : 'transparent',
                          borderRadius: '4px', fontWeight: isDiag ? 600 : 400,
                          color: isDiag ? 'var(--color-success-light)' : val > 0 ? 'var(--color-error-light)' : 'var(--text-muted)',
                        }}>{val}</td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Error Analysis */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
        className="glass-card" style={{ padding: '28px', marginBottom: '20px' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} /> Error Analysis
        </h3>
        {errorAnalysis ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
              <div className="stat-card" style={{ padding: '14px' }}>
                <div className="stat-value" style={{ fontSize: '1.3rem' }}>{errorAnalysis.total_test_samples}</div>
                <div className="stat-label">Test Samples</div>
              </div>
              <div className="stat-card" style={{ padding: '14px' }}>
                <div className="stat-value" style={{ fontSize: '1.3rem' }}>{errorAnalysis.total_errors}</div>
                <div className="stat-label">Misclassifications</div>
              </div>
              <div className="stat-card" style={{ padding: '14px' }}>
                <div className="stat-value" style={{ fontSize: '1.3rem' }}>{(errorAnalysis.error_rate * 100).toFixed(1)}%</div>
                <div className="stat-label">Error Rate</div>
              </div>
            </div>
            {Object.keys(errorAnalysis.confusion_pairs || {}).length > 0 ? (
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 500, marginBottom: '8px', color: 'var(--text-secondary)' }}>Common Confusion Pairs</div>
                {Object.entries(errorAnalysis.confusion_pairs).map(([pair, count]) => (
                  <div key={pair} style={{
                    display: 'flex', justifyContent: 'space-between', padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)', background: 'var(--glass-bg)',
                    marginBottom: '4px', fontSize: '0.8rem',
                  }}>
                    <span>{pair}</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-warning)' }}>{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-success)', fontSize: '0.85rem' }}>
                <CheckCircle2 size={16} /> No misclassifications on test set
              </div>
            )}
          </div>
        ) : <div className="skeleton" style={{ height: '100px' }} />}
      </motion.div>

      {/* Experiments Log */}
      {experiments?.experiments?.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="glass-card" style={{ padding: '28px' }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px' }}>Experiment Log</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  {['ID', 'Model', 'Features', 'Macro F1', 'Time', 'Notes'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '8px 10px', color: 'var(--text-tertiary)', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {experiments.experiments.map((exp, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>{exp.experiment_id}</td>
                    <td style={{ padding: '8px 10px' }}>{exp.model}</td>
                    <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>{exp.feature_set}</td>
                    <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-success)' }}>{exp.macro_f1}</td>
                    <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>{exp.training_time}s</td>
                    <td style={{ padding: '8px 10px', fontSize: '0.75rem', color: 'var(--text-secondary)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{exp.observations}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  )
}
