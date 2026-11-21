/**
 * GuardDengue — Application Root
 *
 * Wires up:
 *   - TanStack Query client (API state management)
 *   - SettingsProvider (language, inspector mode, theme)
 *   - React Router (ChatPage / AboutPage)
 *   - AppShell layout
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SettingsProvider } from '@/store/settings'
import AppShell from '@/components/layout/AppShell'
import ChatPage from '@/pages/ChatPage'
import AboutPage from '@/pages/AboutPage'
import NotFoundPage from '@/pages/NotFoundPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <SettingsProvider>
        <BrowserRouter>
          <AppShell>
            <Routes>
              <Route path="/"       element={<ChatPage />} />
              <Route path="/about"  element={<AboutPage />} />
              <Route path="*"       element={<NotFoundPage />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </SettingsProvider>
    </QueryClientProvider>
  </StrictMode>,
)
