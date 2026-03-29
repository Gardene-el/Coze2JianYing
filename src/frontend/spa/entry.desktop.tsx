import '../initialize'

import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import BootErrorBoundary from '@/components/BootErrorBoundary'
import SPAGlobalProvider from '@/layout/SPAGlobalProvider'

import { appRoutes } from './router/routes'

// Electron 生产包加载本地文件，basename 不带前缀
const router = createBrowserRouter(appRoutes, { basename: '/' })

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element not found')

createRoot(rootElement).render(
  <BootErrorBoundary>
    <SPAGlobalProvider>
      <RouterProvider router={router} />
    </SPAGlobalProvider>
  </BootErrorBoundary>,
)
