import { FormEvent, useEffect, useState } from 'react'

type ShortURL = { id: string; original_url: string; short_code: string; short_url: string; is_active: boolean }
const API = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')
const headers = { 'Content-Type': 'application/json', 'X-User-ID': 'demo-user' }

export default function App() {
  const [urls, setUrls] = useState<ShortURL[]>([])
  const [originalUrl, setOriginalUrl] = useState('')
  const [alias, setAlias] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const loadUrls = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API}/api/urls`, { headers })
      if (!response.ok) throw new Error('Could not load your links.')
      setUrls(await response.json())
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not load your links.') }
    finally { setLoading(false) }
  }
  useEffect(() => { void loadUrls() }, [])

  const createUrl = async (event: FormEvent) => {
    event.preventDefault(); setError('')
    try {
      const response = await fetch(`${API}/api/urls`, { method: 'POST', headers, body: JSON.stringify({ original_url: originalUrl, custom_alias: alias || null }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Could not shorten that URL.')
      setUrls(current => [data, ...current]); setOriginalUrl(''); setAlias('')
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not shorten that URL.') }
  }

  const disable = async (id: string) => {
    const response = await fetch(`${API}/api/urls/${id}`, { method: 'DELETE', headers })
    if (response.ok) setUrls(current => current.map(url => url.id === id ? { ...url, is_active: false } : url))
  }

  return <main className="shell">
    <header><div className="eyebrow">PULSELINK / LINK OPERATIONS</div><h1>Make every redirect count.</h1><p className="lede">A focused URL shortener with clear ownership, useful stats, and reliability built in.</p></header>
    <section className="card create-card"><div><p className="section-label">CREATE A SHORT LINK</p><h2>Turn a long URL into a shareable moment.</h2></div>
      <form onSubmit={createUrl}><label>Destination URL<input aria-label="Destination URL" type="url" required value={originalUrl} onChange={event => setOriginalUrl(event.target.value)} placeholder="https://example.com/your-story" /></label><label>Custom alias <span>(optional)</span><input aria-label="Custom alias" value={alias} onChange={event => setAlias(event.target.value)} placeholder="your-alias" /></label><button type="submit">Shorten URL <span>→</span></button></form>
      {error && <p role="alert" className="error">{error}</p>}
    </section>
    <section className="links-section"><div className="section-heading"><div><p className="section-label">YOUR LINKS</p><h2>Recent activity</h2></div><span className="count">{urls.length} total</span></div>
      {loading ? <p className="empty">Loading your links…</p> : urls.length === 0 ? <p className="empty">No links yet. Your first one belongs here.</p> : <div className="link-list">{urls.map(url => <article className={url.is_active ? 'link-row' : 'link-row inactive'} key={url.id}><div><a href={url.short_url}>{url.short_url.replace(/^https?:\/\//, '')}</a><p>{url.original_url}</p></div><div className="row-actions"><span>{url.is_active ? 'Active' : 'Disabled'}</span>{url.is_active && <button className="text-button" onClick={() => void disable(url.id)}>Disable</button>}</div></article>)}</div>}
    </section>
  </main>
}
