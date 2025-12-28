export interface Notice {
  id: string;
  severity: 'info' | 'warning' | 'error';
  component: string;
  code: string;
  message: string;
  created_at: number;
  acknowledged: boolean;
  ack_by: string | null;
  ack_at: number | null;
}

// Helper to get API endpoint URL
function getApiUrl(endpoint: string): string {
  const baseUrl = (window as any).API_BASE_URL || '/api';
  return baseUrl.startsWith('http') ? `${baseUrl}${endpoint}` : `/api${endpoint}`;
}

export async function fetchNotices(): Promise<Notice[]> {
  const res = await fetch(getApiUrl('/notices'));
  if (!res.ok) throw new Error('Failed to fetch notices');
  return res.json();
}

export async function acknowledgeNotice(noticeId: string, ackedBy: string): Promise<void> {
  const res = await fetch(getApiUrl(`/notices/${noticeId}/ack`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ acked_by: ackedBy })
  });
  if (!res.ok) throw new Error('Failed to acknowledge notice');
}
