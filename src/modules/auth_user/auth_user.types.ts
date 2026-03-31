// Shared auth response typing helper for parser parity.
export type AuthLoginResponse = {
  id: string;
  email: string;
  name: string;
  role: "admin" | "reviewer";
  access_token: string;
  refresh_token?: string;
  expires_at: string;
};
