import { Spin } from 'antd'
import { lazy, type ReactNode, Suspense } from 'react'
import { Navigate, type RouteObject } from 'react-router-dom'
import MainLayout from '@/routes/_layout'
import AppShell from '@/routes/AppShell'

const CloudServicePage = lazy(() => import('@/routes/CloudService'))
const DraftGeneratorPage = lazy(() => import('@/routes/DraftGenerator'))
const ScriptExecutorPage = lazy(() => import('@/routes/ScriptExecutor'))
const ReplayPage = lazy(() => import('@/routes/Replay'))
const SettingsPage = lazy(() => import('@/routes/Settings'))
const ToolGeneratorPage = lazy(() => import('@/routes/ToolGenerator'))

const LazyWrapper = ({ children }: { children: ReactNode }) => (
  <Suspense fallback={<Spin size="large" style={{ margin: '40px auto', display: 'block' }} />}>
    {children}
  </Suspense>
)

export const appRoutes: RouteObject[] = [
  {
    path: '/',
    element: <AppShell />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { index: true, element: <Navigate replace to="/cloud-service" /> },
          {
            path: 'cloud-service',
            element: (
              <LazyWrapper>
                <CloudServicePage />
              </LazyWrapper>
            ),
          },
          {
            path: 'draft-generator',
            element: (
              <LazyWrapper>
                <DraftGeneratorPage />
              </LazyWrapper>
            ),
          },
          {
            path: 'script-executor',
            element: (
              <LazyWrapper>
                <ScriptExecutorPage />
              </LazyWrapper>
            ),
          },
          {
            path: 'replay',
            element: (
              <LazyWrapper>
                <ReplayPage />
              </LazyWrapper>
            ),
          },
          {
            path: 'settings',
            element: (
              <LazyWrapper>
                <SettingsPage />
              </LazyWrapper>
            ),
          },
          {
            path: 'tool-generator',
            element: (
              <LazyWrapper>
                <ToolGeneratorPage />
              </LazyWrapper>
            ),
          },
        ],
      },
    ],
  },
]
