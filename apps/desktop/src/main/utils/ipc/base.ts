import { AsyncLocalStorage } from 'node:async_hooks'

import type { IpcMainInvokeEvent, WebContents } from 'electron'
import { ipcMain } from 'electron'

// Base context for IPC methods
export interface IpcContext {
  event: IpcMainInvokeEvent
  sender: WebContents
}

// Metadata storage for decorated methods
const methodMetadata = new WeakMap<object, Map<string, string>>()
const ipcContextStorage = new AsyncLocalStorage<IpcContext>()

// Decorator for IPC methods
export function IpcMethod() {
  return (target: object, propertyKey: string, descriptor: PropertyDescriptor) => {
    const ctor = target.constructor

    if (!methodMetadata.has(ctor)) {
      methodMetadata.set(ctor, new Map())
    }

    const methods = methodMetadata.get(ctor) as Map<string, string>
    methods.set(propertyKey, propertyKey)

    return descriptor
  }
}

// Handler registry for IPC methods
export class IpcHandler {
  private static instance: IpcHandler
  private registeredChannels = new Set<string>()

  static getInstance(): IpcHandler {
    if (!IpcHandler.instance) {
      IpcHandler.instance = new IpcHandler()
    }
    return IpcHandler.instance
  }

  registerMethod<TArgs extends unknown[], TOutput>(
    channel: string,
    handler: (...args: TArgs) => Promise<TOutput> | TOutput,
  ) {
    if (this.registeredChannels.has(channel)) {
      return // Already registered
    }

    this.registeredChannels.add(channel)

    ipcMain.handle(channel, async (event: IpcMainInvokeEvent, ...args: unknown[]) => {
      const context: IpcContext = {
        event,
        sender: event.sender,
      }

      return ipcContextStorage.run(context, async () => {
        try {
          const typedArgs = args as TArgs
          return await handler(...typedArgs)
        } catch (error) {
          console.error(`Error in IPC method ${channel}:`, error)
          throw error
        }
      })
    })
  }

  // Send events to renderer
  sendToRenderer<T = unknown>(webContents: WebContents, channel: string, data: T) {
    webContents.send(channel, data)
  }
}

// Base class for IPC service groups
export abstract class IpcService {
  protected handler = IpcHandler.getInstance()
  static readonly groupName: string

  constructor() {
    this.registerMethods()
  }

  protected registerMethods(): void {
    const ctor = this.constructor
    const methods = methodMetadata.get(ctor)

    if (methods) {
      methods.forEach((methodName, propertyKey) => {
        const method = (this as Record<string, unknown>)[propertyKey]
        if (typeof method === 'function') {
          this.registerMethod(methodName, method.bind(this))
        }
      })
    }
  }

  protected registerMethod<TArgs extends unknown[], TOutput>(
    methodName: string,
    handler: (...args: TArgs) => Promise<TOutput> | TOutput,
  ) {
    const groupName = (this.constructor as typeof IpcService).groupName
    const channel = `${groupName}.${methodName}`
    this.handler.registerMethod(channel, handler)
  }
}

// Service constructor with groupName
export interface IpcServiceConstructor {
  // biome-ignore lint/suspicious/noExplicitAny: allows subclasses with specific constructor args
  new (...args: any[]): IpcService
  readonly groupName: string
}

// Create services function that infers types from service constructors
export function createServices<T extends readonly IpcServiceConstructor[]>(
  serviceConstructors: T,
  ...constructorArgs: unknown[]
): CreateServicesResult<T> {
  const services = {} as CreateServicesResult<T>

  for (const ServiceConstructor of serviceConstructors) {
    const instance = new ServiceConstructor(...constructorArgs)
    const groupName = ServiceConstructor.groupName

    if (!groupName) {
      throw new Error(
        `Service ${ServiceConstructor.name} must define a static readonly groupName property`,
      )
    }

    services[groupName] = instance
  }

  return services
}

// Helper type for createServices return type
export type CreateServicesResult<T extends readonly IpcServiceConstructor[]> = {
  [K in T[number] as K['groupName']]: InstanceType<K>
}

export function getIpcContext() {
  return ipcContextStorage.getStore()
}

export function runWithIpcContext<T>(context: IpcContext, callback: () => T): T {
  return ipcContextStorage.run(context, callback)
}
