import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";

const CIFORGE_API = process.env.CIFORGE_API_URL || "http://localhost:8000";

export async function GET(
  req: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const response = await fetch(
      `${CIFORGE_API}/api/v1/status/${params.sessionId}`
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: "Session not found" },
        { status: 404 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Status check error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
