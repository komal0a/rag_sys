import React, { useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'

// Get API URL from environment variable or default to relative path for development
const API_URL = import.meta.env.VITE_API_URL || ''

const API = (path: string, opts: any = {}) => {
  const url = API_URL ? `${API_URL}${path}` : path
  return fetch(url, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(opts.headers||{}) },
    ...opts,
  }).then(r => r.json().catch(()=> ({})).then(b => ({status: r.status, body: b})))
}

function App(){
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [view, setView] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [docs, setDocs] = useState<any[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState<any>(null)
  const [convs, setConvs] = useState<any[]>([])

  useEffect(()=>{ if(token){ fetchDocs(); fetchConvs(); setView('dashboard')} }, [token])

  const headers = token ? { Authorization: `Bearer ${token}` } : {}

  async function register(){
    const r = await API('/auth/register', { method: 'POST', body: JSON.stringify({email,password}) })
    if(r.status===200) alert('registered')
    else alert(r.body.detail || 'error')
  }

  async function login(){
    const r = await API('/auth/login', { method: 'POST', body: JSON.stringify({email,password}) })
    if(r.status===200 && r.body.access_token){
      localStorage.setItem('token', r.body.access_token)
      setToken(r.body.access_token)
    } else alert(r.body.detail || 'login failed')
  }

  async function fetchDocs(){
    const r = await API('/documents', { method: 'GET', headers })
    if(r.status===200) setDocs(r.body)
  }

  async function upload(){
    if(!file) return alert('choose file')
    const form = new FormData(); form.append('file', file, file.name)
    const r = await fetch('/documents/upload', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: form })
    if(r.status===200) { alert('uploaded'); fetchDocs() }
    else { const b = await r.json().catch(()=>({})); alert(b.detail || 'upload failed') }
  }

  async function ask(docId?: number){
    const payload:any = { query, top_k:5 }
    if(docId) payload.document_id = docId
    const r = await API('/chat', { method: 'POST', headers: {...headers}, body: JSON.stringify(payload) })
    if(r.status===200){ setAnswer(r.body) } else { alert(r.body.detail || 'error') }
  }

  async function fetchConvs(){
    const r = await API('/conversations', { method: 'GET', headers })
    if(r.status===200) setConvs(r.body)
  }

  return (
    <div style={{fontFamily:'sans-serif',padding:20}}>
      {!token && (
        <div>
          <h2>Login / Register</h2>
          <input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
          <button onClick={login}>Login</button>
          <button onClick={register}>Register</button>
        </div>
      )}

      {token && (
        <div>
          <h2>Dashboard</h2>
          <button onClick={()=>{localStorage.removeItem('token'); setToken(null); setView('login')}}>Logout</button>
          <hr />
          <h3>Upload PDF</h3>
          <input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0]||null)} />
          <button onClick={upload}>Upload</button>
          <h3>Your Documents</h3>
          <ul>{docs.map(d=> <li key={d.id}>{d.filename} - {d.user_id}</li>)}</ul>
          <hr />
          <h3>Ask a question</h3>
          <input style={{width:'60%'}} value={query} onChange={e=>setQuery(e.target.value)} />
          <button onClick={()=>ask()}>Ask Global</button>
          <div style={{marginTop:10}}>
            <h4>Answer</h4>
            {answer && (<div><p>{answer.answer}</p><h5>Sources</h5><pre>{JSON.stringify(answer.sources,null,2)}</pre></div>)}
          </div>
          <hr />
          <h3>Conversations</h3>
          <button onClick={fetchConvs}>Refresh</button>
          <ul>{convs.map(c=> <li key={c.id}>{c.title} ({c.id})</li>)}</ul>
        </div>
      )}
    </div>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
