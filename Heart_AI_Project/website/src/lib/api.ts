export type ChatResponse = {
  reply: string;
  session_id: string;
  stage: string;
  collected: Record<string, number>;
  prediction?: {
    status: string;
    risk_percentage: number;
    message: string;
  };
  done: boolean;
};

const base =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";

export async function fetchWelcome(): Promise<ChatResponse> {
  const res = await fetch(`${base}/api/chat/welcome`);
  if (!res.ok) throw new Error("Could not reach CardioRisk AI server.");
  return res.json();
}

export async function sendChatMessage(
  message: string,
  sessionId: string | null
): Promise<ChatResponse> {
  const res = await fetch(`${base}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ?? "Chat request failed."
    );
  }
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${base}/api/health`);
    const data = await res.json();
    return data.model_loaded === true;
  } catch {
    return false;
  }
}
