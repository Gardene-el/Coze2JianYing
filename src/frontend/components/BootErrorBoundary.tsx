import { Button, Result } from 'antd'
import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children?: ReactNode
}
interface State {
  error: Error | null
}

class BootErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[BootErrorBoundary]', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <Result
          status="error"
          title="应用启动失败"
          subTitle={this.state.error.message}
          extra={
            <Button onClick={() => window.location.reload()} type="primary">
              刷新重试
            </Button>
          }
        />
      )
    }
    return this.props.children
  }
}

export default BootErrorBoundary
