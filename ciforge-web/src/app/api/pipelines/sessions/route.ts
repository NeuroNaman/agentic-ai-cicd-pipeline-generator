import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";

const CIFORGE_API = process.env.CIFORGE_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const response = await fetch(`${CIFORGE_API}/api/v1/sessions`);

    if (!response.ok) {
      return NextResponse.json([], { status: 200 });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    // If backend is offline, return empty array gracefully
    return NextResponse.json([]);
  }
}
