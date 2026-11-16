import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from './App'

describe('PulseLink frontend', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
  })

  it('renders the creation form and empty state', async () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /make every redirect count/i })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/no links yet/i)).toBeInTheDocument())
  })

  it('submits a URL and renders the created short link', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({ ok: true, json: async () => [] } as Response)
    fetchMock.mockResolvedValueOnce({ ok: true, json: async () => ({ id: '1', original_url: 'https://example.com', short_url: 'http://localhost:8000/hello', short_code: 'hello', is_active: true }) } as Response)
    render(<App />)
    await waitFor(() => expect(screen.getByText(/no links yet/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText('Destination URL'), { target: { value: 'https://example.com' } })
    fireEvent.change(screen.getByLabelText('Custom alias'), { target: { value: 'hello' } })
    fireEvent.click(screen.getByRole('button', { name: /shorten url/i }))
    await waitFor(() => expect(screen.getByText('localhost:8000/hello')).toBeInTheDocument())
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/urls', expect.objectContaining({ method: 'POST' }))
  })
})
