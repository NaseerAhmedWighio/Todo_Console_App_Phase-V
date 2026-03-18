'use client';

import { AuthProvider } from '../components/Auth/AuthProvider';
import { ReactNode } from 'react';

export default function ClientAuthProvider({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}