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

export async function fetchNotices(): Promise<Notice[]> {
  const res = await fetch('/api/notices');
  if (!res.ok) throw new Error('Failed to fetch notices');
  return res.json();
}

export async function acknowledgeNotice(noticeId: string, ackedBy: string): Promise<void> {
  const res = await fetch(`/api/notices/${noticeId}/ack`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ acked_by: ackedBy })
  });
  if (!res.ok) throw new Error('Failed to acknowledge notice');
}
