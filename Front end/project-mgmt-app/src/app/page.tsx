'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/src/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = api.getToken();
    if (token) {
      router.push('/projects');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-600">Loading...</p>
    </div>
  );
}