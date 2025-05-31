import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { path = [] } = req.query
  const apiBase = process.env.API_BASE_URL || 'http://localhost:8000'
  const targetUrl = `${apiBase}/${Array.isArray(path) ? path.join('/') : path}`

  try {
    const filteredHeaders: Record<string, string> = {}
    for (const [key, value] of Object.entries(req.headers)) {
      if (
        typeof value === 'string' &&
        !['host', 'connection', 'content-length', 'accept-encoding'].includes(key.toLowerCase())
      ) {
        filteredHeaders[key] = value
      }
    }

    const apiRes = await fetch(targetUrl, {
      method: req.method,
      headers: filteredHeaders,
      body: req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined,
    })

    const contentType = apiRes.headers.get('content-type') || ''
    res.status(apiRes.status)

    if (contentType.includes('application/json')) {
      const data = await apiRes.json()
      res.json(data)
    } else {
      const text = await apiRes.text()
      res.send(text)
    }
  } catch (error) {
    console.error('Proxy error:', error)
    res.status(500).json({ error: 'Proxy request failed' })
  }
}
