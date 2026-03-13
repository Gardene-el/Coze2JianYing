/**
 * Permission stubs for Windows.
 * On Windows, media and system permissions are managed by the OS —
 * these helpers always return 'granted' so calling code works unchanged.
 */

export type PermissionStatus =
  | 'authorized'
  | 'denied'
  | 'not-determined'
  | 'restricted'
  | 'granted';

/** @internal test helpers — no-ops on Windows */
export function __resetMacPermissionsModuleCache(): void {}
export function __setMacPermissionsModule(_module: unknown): void {}

export function getPermissionStatus(_type: string): PermissionStatus {
  return 'granted';
}

export function getAccessibilityStatus(): PermissionStatus {
  return 'granted';
}

export function requestAccessibilityAccess(): boolean {
  return true;
}

export function getMicrophoneStatus(): PermissionStatus {
  return 'granted';
}

export async function requestMicrophoneAccess(): Promise<boolean> {
  return true;
}

export function getCameraStatus(): PermissionStatus {
  return 'granted';
}

export async function requestCameraAccess(): Promise<boolean> {
  return true;
}

export function getScreenCaptureStatus(): PermissionStatus {
  return 'granted';
}

export async function requestScreenCaptureAccess(_openPreferences = true): Promise<boolean> {
  return true;
}

export function getFullDiskAccessStatus(): PermissionStatus {
  return 'granted';
}

export function requestFullDiskAccess(): void {}

export async function openFullDiskAccessSettings(): Promise<void> {}

export function getInputMonitoringStatus(): PermissionStatus {
  return 'granted';
}

export function getMediaAccessStatus(_mediaType: 'microphone' | 'screen'): string {
  return 'granted';
}
