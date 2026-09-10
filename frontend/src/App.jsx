import { useState } from 'react'

const sampleClaim = {
  claim_id: 'CLM-0001',
  policy_holder_name: 'Rajesh Kumar Singh',
  claimant_name: 'Rajesh K Singh',
  claim_date: '2024-02-10',
  policy_start_date: '2023-01-01',
  policy_end_date: '2024-12-31',
  billed_amount: 350000,
  claimed_amount: 550000,
}

function App() {
  const [form, setForm] = useState(sampleClaim)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: name === 'billed_amount' || name === 'claimed_amount' ? Number(value) : value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ success: false, error: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI DETECTIVE</p>
          <h1>Insurance fraud signal dashboard</h1>
        </div>
        <span className="badge">Google Cloud ready</span>
      </header>

      <main className="dashboard-grid">
        <section className="panel form-panel">
          <h2>Claim review</h2>
          <form onSubmit={handleSubmit} className="claim-form">
            <label>
              Claim ID
              <input name="claim_id" value={form.claim_id} onChange={handleChange} />
            </label>
            <label>
              Policy holder name
              <input name="policy_holder_name" value={form.policy_holder_name} onChange={handleChange} />
            </label>
            <label>
              Claimant name
              <input name="claimant_name" value={form.claimant_name} onChange={handleChange} />
            </label>
            <div className="row">
              <label>
                Claim date
                <input type="date" name="claim_date" value={form.claim_date} onChange={handleChange} />
              </label>
              <label>
                Policy start
                <input type="date" name="policy_start_date" value={form.policy_start_date} onChange={handleChange} />
              </label>
            </div>
            <div className="row">
              <label>
                Policy end
                <input type="date" name="policy_end_date" value={form.policy_end_date} onChange={handleChange} />
              </label>
              <label>
                Billed amount
                <input type="number" name="billed_amount" value={form.billed_amount} onChange={handleChange} />
              </label>
            </div>
            <label>
              Claimed amount
              <input type="number" name="claimed_amount" value={form.claimed_amount} onChange={handleChange} />
            </label>
            <button type="submit" disabled={loading}>{loading ? 'Reviewing...' : 'Analyze claim'}</button>
          </form>
        </section>

        <section className="panel result-panel">
          <h2>Fraud signals</h2>
          {result ? (
            <div className="result-box">
              {result.success === false ? (
                <p className="error">{result.error}</p>
              ) : (
                <>
                  <div className="signal-row">
                    <span>Amount variance</span>
                    <strong>{result.signals?.amount_variance_pct ?? 0}%</strong>
                  </div>
                  <div className="signal-row">
                    <span>Inflation flag</span>
                    <strong>{result.signals?.is_amount_inflation ? 'High risk' : 'Normal'}</strong>
                  </div>
                  <div className="signal-row">
                    <span>Policy validity</span>
                    <strong>{result.signals?.policy_valid ? 'Valid' : 'Invalid'}</strong>
                  </div>
                  <div className="signal-row">
                    <span>Name similarity</span>
                    <strong>{result.signals?.name_similarity_score ?? 0}</strong>
                  </div>
                  <div className="signal-row">
                    <span>Duplicate signal</span>
                    <strong>{result.signals?.duplicate_signal?.is_duplicate ? 'Duplicate found' : 'No duplicate'}</strong>
                  </div>
                </>
              )}
            </div>
          ) : (
            <p className="placeholder">No analysis yet. Submit a claim to view fraud clues.</p>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
