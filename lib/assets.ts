declare global { interface Window { __IPNET_ASSETS__?: Record<string, string>; } }
export function asset(path: string) {
  return typeof window !== "undefined" ? window.__IPNET_ASSETS__?.[path] ?? path : path;
}
