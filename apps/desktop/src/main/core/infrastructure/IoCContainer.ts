/**
 * Stores classes in the application that require decorators
 */
export class IoCContainer {
  static shortcuts: WeakMap<object, { methodName: string; name: string }[]> = new WeakMap()

  static protocolHandlers: WeakMap<
    object,
    { action: string; methodName: string; urlType: string }[]
  > = new WeakMap()

  init() {}
}
