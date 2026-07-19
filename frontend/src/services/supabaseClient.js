import { createClient } from '@supabase/supabase-js'

// Supabase Auth is used here ONLY to perform the Google OAuth handshake
// (i.e. to prove the user owns a given Google account). It does NOT
// replace TalentForge's own session/authorization system — the backend
// still issues and verifies its own JWTs and still owns all role logic.
// See services/authService.js (oauth methods) and context/AuthContext.jsx.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    'Supabase env vars are missing (VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY). ' +
    '"Continue with Google" will not work until these are set.'
  )
}

export const supabase = createClient(supabaseUrl || '', supabaseAnonKey || '', {
  auth: {
    // Persist + auto-refresh Supabase's own session so the OAuth
    // handshake survives redirects and page refreshes.
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
})

export default supabase
